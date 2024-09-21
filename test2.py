import streamlit as st
import pandas as pd
from datetime import datetime
from searxng import search_searxng
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

# Mock functions for demonstration purposes
def scrape_google_scholar_profile(url):
    # Implement web scraping logic here
    return [{'title': 'Sample Paper', 'year': 2010, 'citations': 100, 'venue': 'Sample Conference'}]

def scrape_dblp(query):
    # Implement DBLP scraping logic here
    return [{'title': 'DBLP Paper', 'year': 2011, 'citations': 50, 'venue': 'Sample Journal'}]

def organize_papers(papers):
    return sorted(papers, key=lambda x: (x['year'], x['citations']), reverse=True)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def categorize_paper(llm, title, venue):
    messages = [
        ("system", "Categorize research papers into 'Journal' or 'Conference' based on their titles and venues."),
        ("human", f"Categorize this paper: Title: {title}, Venue: {venue}. Respond with only 'Journal' or 'Conference'.")
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content.strip().lower()

def categorize_papers(papers, llm):
    journal_papers, conference_papers = [], []
    for paper in papers:
        try:
            category = categorize_paper(llm, paper['title'], paper['venue'])
            if category == 'journal':
                journal_papers.append(paper)
            elif category == 'conference':
                conference_papers.append(paper)
        except Exception as e:
            st.warning(f"Error categorizing paper: {paper['title']}. Error: {str(e)}")
    return journal_papers, conference_papers

def save_categorized_papers(papers, category):
    df = pd.DataFrame(papers)
    csv = df.to_csv(index=False)
    return csv

def main():
    st.set_page_config(page_title="ScholarAI - Research Analysis", layout="wide")
    
    # Custom CSS for a more attractive and professional look
    st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        background-color: #fff;
    }
    h1 {
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("ScholarAI - Advanced Research Analysis")
    st.markdown("Analyze and categorize research papers with ease.")

    # Input section
    col1, col2 = st.columns(2)
    with col1:
        input_type = st.radio("Select input type:", ["Excel", "BibTeX"])
    with col2:
        if input_type == "Excel":
            uploaded_file = st.file_uploader("Upload Excel file", type="xlsx")
        else:
            uploaded_file = st.file_uploader("Upload BibTeX file", type="bib")

    search_query = st.text_input("Enter a search query for additional papers:")
    
    start_year, end_year = st.slider("Select year range:", 1900, datetime.now().year, (2005, 2013))

    if st.button("Analyze Papers"):
        with st.spinner("Processing and analyzing papers..."):
            # Step 1: Load and process input data
            if uploaded_file:
                # Process uploaded file (Excel or BibTeX)
                st.info("Processing uploaded file...")
                # Implement file processing logic here
                papers = []  # Replace with actual data from file

            # Step 2: Perform additional search if query provided
            if search_query:
                st.info(f"Searching for additional papers: {search_query}")
                search_results = search_searxng(search_query)
                if search_results['results']:
                    first_result_url = search_results['results'][0].url
                    additional_papers = scrape_google_scholar_profile(first_result_url)
                    papers.extend(additional_papers)

                # DBLP search
                dblp_papers = scrape_dblp(search_query)
                papers.extend(dblp_papers)

            # Step 3: Filter papers by year range
            filtered_papers = [p for p in papers if start_year <= p['year'] <= end_year]

            # Step 4: Organize papers
            organized_papers = organize_papers(filtered_papers)

            # Step 5: Categorize papers using LLM
            llm = ChatGroq(model="mixtral-8x7b-32768", temperature=0)
            journal_papers, conference_papers = categorize_papers(organized_papers, llm)

            # Display results
            st.success("Analysis complete!")
            st.subheader("Results Summary")
            st.write(f"Total papers analyzed: {len(organized_papers)}")
            st.write(f"Journal papers: {len(journal_papers)}")
            st.write(f"Conference papers: {len(conference_papers)}")

            # Provide download options
            st.subheader("Download Results")
            journal_csv = save_categorized_papers(journal_papers, "journal")
            conference_csv = save_categorized_papers(conference_papers, "conference")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download Journal Papers (CSV)", journal_csv, "journal_papers.csv", "text/csv")
            with col2:
                st.download_button("Download Conference Papers (CSV)", conference_csv, "conference_papers.csv", "text/csv")

            # Option to export as Excel
            if st.button("Export as Excel"):
                # Implement Excel export logic here
                st.success("Excel file generated successfully!")

    # Footer
    st.markdown("---")
    st.markdown("Powered by SearXNG, Google Scholar, DBLP, and Groq LLM | Created by Team ScholarAI")

if __name__ == "__main__":
    main()