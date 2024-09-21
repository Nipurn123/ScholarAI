from langchain_groq import ChatGroq


import pandas as pd
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def categorize_paper(llm, paper):
    messages = [
        (
            "system",
            "You are an advanced assistant designed to categorize research papers based on their titles and publication venues into two distinct domains: 'Journal Research Papers' and 'Conference Research Papers.'"
        ),
        (
            "human",
            f"Categorize this paper: Title: {paper['title']}, Venue: {paper.get('venue', 'Unknown')}. Respond with only 'Journal' or 'Conference'."
        ),
    ]
    
    ai_msg = llm.invoke(messages)
    return ai_msg.content.strip().lower()

def categorize_papers(papers, start_year, end_year):
    llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

    # Filter papers by year range, handling potential invalid year values
    filtered_papers = []
    for paper in papers:
        try:
            year = int(paper['year'])
            if start_year <= year <= end_year:
                filtered_papers.append(paper)
        except ValueError:
            # Skip papers with invalid year values
            continue

    journal_papers = []
    conference_papers = []

    for paper in filtered_papers:
        try:
            category = categorize_paper(llm, paper)
            if category == 'journal':
                journal_papers.append(paper)
            elif category == 'conference':
                conference_papers.append(paper)
        except Exception as e:
            print(f"Error categorizing paper: {paper['title']}. Error: {str(e)}")
            # Optionally, you could add the paper to an 'uncategorized' list here

    return journal_papers, conference_papers

def save_categorized_papers(journal_papers, conference_papers):
    journal_df = pd.DataFrame(journal_papers)
    conference_df = pd.DataFrame(conference_papers)

    journal_csv = journal_df.to_csv(index=False)
    conference_csv = conference_df.to_csv(index=False)

    return journal_csv, conference_csv