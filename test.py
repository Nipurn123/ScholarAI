import streamlit as st
import pandas as pd
import io
import bibtexparser
from searxng import search_searxng
from datetime import datetime
from data_acquisition_module.google_scholar_crawler import scrape_google_scholar_profile
from data_processing_module.organiser import organize_papers_by_year_and_citations
from data_processing_module.duplicate_remover import remove_duplicates
from data_processing_module.data_normalizer import normalize_data
from data_processing_module.date_range_filter import filter_by_date
from langchain_groq import ChatGroq
from tenacity import retry, stop_after_attempt, wait_exponential

def load_excel_file(uploaded_file):
    df = pd.read_excel(uploaded_file)
    return df

def load_bibtex_file(uploaded_file):
    bibtex_str = uploaded_file.getvalue().decode("utf-8")
    bib_database = bibtexparser.loads(bibtex_str)
    return bib_database.entries

def extract_faculty_names(df):
    # Assuming the faculty names are in a column named 'Faculty'
    # Adjust this based on your Excel file structure
    return df['Faculty Name'].unique().tolist()

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
    st.set_page_config(page_title="Research Analysis Tool", layout="wide")
    
    st.title("Research Analysis Tool")
    st.markdown("""
    This app analyzes research papers based on input from Excel or BibTeX files.
    You can select a faculty member, choose a database for analysis, and get categorized results.
    """)
    
    # File input selection
    file_type = st.radio("Select input file type:", ("Excel", "BibTeX"))
    
    uploaded_file = st.file_uploader(f"Upload your {file_type} file", type=["xlsx", "bib"] if file_type == "BibTeX" else ["xlsx"])
    
    if uploaded_file is not None:
        if file_type == "Excel":
            df = load_excel_file(uploaded_file)
            faculty_names = extract_faculty_names(df)
            selected_faculty = st.selectbox("Select a faculty member:", faculty_names)
        else:
            bib_data = load_bibtex_file(uploaded_file)
            selected_faculty = None
        
        # Database selection
        database = st.selectbox("Select database for analysis:", ["Google Scholar", "DBLP", "Both"])
        
        if st.button("Analyze"):
            try:
                # Data acquisition based on selected database
                papers = []
                if database in ["Google Scholar", "Both"]:
                    with st.spinner("Scraping Google Scholar..."):
                        papers += scrape_google_scholar_profile(selected_faculty) if selected_faculty else bib_data
                
                if database in ["DBLP", "Both"]:
                    with st.spinner("Scraping DBLP..."):
                        # Implement DBLP scraping here
                        pass
                
                # Remove duplicates
                with st.spinner("Removing duplicates..."):
                    unique_papers = remove_duplicates(papers)
                
                # Normalize data
                with st.spinner("Normalizing data..."):
                    normalized_papers = normalize_data(unique_papers)
                
                # Organize papers without date filtering
                with st.spinner("Organizing papers by year and citations..."):
                    organized_papers = organize_papers_by_year_and_citations(normalized_papers)
                
                if not organized_papers:
                    st.warning("No papers found.")
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
                        file_name="journal_papers_all.csv",
                        mime="text/csv"
                    )
                    st.download_button(
                        label="Download Conference Papers CSV",
                        data=conference_csv,
                        file_name="conference_papers_all.csv",
                        mime="text/csv"
                    )
            
            except Exception as e:
                st.error(f"An error occurred during the analysis: {str(e)}")
    
    # Footer
    st.markdown("---")
    st.markdown("Powered by SearXNG, Google Scholar, DBLP, and Groq | Created with Streamlit")

if __name__ == "__main__":
    main()