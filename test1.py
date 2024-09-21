import streamlit as st
from searxng import search_searxng
from datetime import datetime
from data_acquisition_module.google_scholar_crawler import scrape_google_scholar_profile
from data_processing_module.organiser import organize_papers_by_year_and_citations
from data_processing_module.duplicate_remover import remove_duplicates
from data_processing_module.data_normalizer import normalize_data
from data_processing_module.date_range_filter import filter_by_date
from langchain_groq import ChatGroq
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
import io

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def categorize_paper(llm, title, venue):
    messages = [
        (
            "system",
            "You are an advanced assistant designed to categorize research papers based on their titles and publication venues into two distinct domains: 'Journal Research Papers' and 'Conference Research Papers.'"
        ),
        (
            "human",
            f"Categorize this paper: Title: {title}, Venue: {venue}. Respond with only 'Journal' or 'Conference'."
        ),
    ]
    
    ai_msg = llm.invoke(messages)
    return ai_msg.content.strip().lower()

def categorize_papers(papers, llm):
    journal_papers = []
    conference_papers = []

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

def save_categorized_papers(journal_papers, conference_papers):
    journal_df = pd.DataFrame(journal_papers)
    conference_df = pd.DataFrame(conference_papers)

    journal_csv = journal_df.to_csv(index=False)
    conference_csv = conference_df.to_csv(index=False)

    return journal_csv, conference_csv

def main():
    st.set_page_config(page_title="Einstein Research Search and Analysis", layout="wide")
    
    st.title("Albert Einstein Research Search and Analysis")
    st.markdown("""
    This app searches for information related to Albert Einstein, extracts the first result's URL,
    analyzes the Google Scholar profile associated with that URL, removes duplicates, and categorizes papers.
    The analysis is performed for papers published between 2005 and 2013.
    """)
    
    # Sidebar for search options
    st.sidebar.header("Search Options")
    num_results = st.sidebar.slider("Number of search results to display", 1, 20, 10)
    
    # Main search interface
    search_query = st.text_input("Enter a search query related to Albert Einstein:")
    search_button = st.button("Search and Analyze")
    
    if search_query and search_button:
        with st.spinner(f"Searching for: {search_query}"):
            search_results = search_searxng(search_query)
        
        if search_results['results']:
            st.success(f"Found {len(search_results['results'])} results")
            
            # Display search results
            for i, result in enumerate(search_results['results'][:num_results], 1):
                with st.expander(f"Result {i}: {result.title}"):
                    st.write(f"**URL:** [{result.url}]({result.url})")
                    st.write(f"**Engine:** {result.engine}")
                    if result.content:
                        st.write(f"**Content:** {result.content[:500]}...")
            
            # Extract the first result's URL for further analysis
            first_result_url = search_results['results'][0].url
            
            st.subheader("Google Scholar Profile Analysis")
            st.write(f"Analyzing Google Scholar profile based on the first search result: {first_result_url}")
            
            try:
                # Scrape Google Scholar profile
                with st.spinner("Scraping Google Scholar profile..."):
                    papers = scrape_google_scholar_profile(first_result_url)
                
                # Remove duplicates
                with st.spinner("Removing duplicates..."):
                    unique_papers = remove_duplicates(papers)
                
                # Normalize data
                with st.spinner("Normalizing data..."):
                    normalized_papers = normalize_data(unique_papers)
                
                # Filter papers by date
                start_date, end_date = '2005-01-01', '2013-12-31'
                with st.spinner(f"Filtering papers for years 2005-2013..."):
                    filtered_papers = filter_by_date(normalized_papers, start_date, end_date)
                
                # Organize papers
                with st.spinner("Organizing papers by year and citations..."):
                    organized_papers = organize_papers_by_year_and_citations(filtered_papers)
                
                if not organized_papers:
                    st.warning(f"No papers found in the year range 2005-2013.")
                else:
                    # Initialize LLM
                    llm = ChatGroq(
                        model="mixtral-8x7b-32768",
                        temperature=0,
                        max_tokens=None,
                        timeout=None,
                        max_retries=2,
                    )
                    
                    # Categorize papers using LLM
                    with st.spinner("Categorizing papers..."):
                        journal_papers, conference_papers = categorize_papers(organized_papers, llm)
                    
                    # Save categorized papers to CSV
                    journal_csv, conference_csv = save_categorized_papers(journal_papers, conference_papers)
                    
                    st.success("Data processing, organization, and categorization complete.")
                    
                    # Display summary
                    st.subheader("Summary of Categorized Papers")
                    st.write(f"Total papers: {len(journal_papers) + len(conference_papers)}")
                    st.write(f"Journal papers: {len(journal_papers)}")
                    st.write(f"Conference papers: {len(conference_papers)}")
                    
                    # Provide download links for the CSV files
                    st.download_button(
                        label="Download Journal Papers CSV",
                        data=journal_csv,
                        file_name="journal_papers_2005_2013.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        label="Download Conference Papers CSV",
                        data=conference_csv,
                        file_name="conference_papers_2005_2013.csv",
                        mime="text/csv"
                    )
            
            except Exception as e:
                st.error(f"An error occurred during the analysis: {str(e)}")
        
        else:
            st.warning("No results found. Try a different search query.")
    
    # Footer
    st.markdown("---")
    st.markdown("Powered by SearXNG, Google Scholar, and Groq | Created with Streamlit")

if __name__ == "__main__":
    main()