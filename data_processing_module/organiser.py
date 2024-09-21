from collections import defaultdict
import csv

def organize_papers_by_year_and_citations(papers):
    """
    Organize papers by year (descending) and then by citations (descending) within each year.
    """
    # Group papers by year
    papers_by_year = defaultdict(list)
    for paper in papers:
        year = paper.get('year', 'Unknown')
        papers_by_year[year].append(paper)
    
    # Sort papers within each year by citations
    for year in papers_by_year:
        papers_by_year[year].sort(key=lambda x: x.get('citations', 0), reverse=True)
    
    # Sort years in descending order
    sorted_years = sorted(papers_by_year.keys(), key=lambda x: (x != 'Unknown', x), reverse=True)
    
    # Flatten the sorted structure
    organized_papers = []
    for year in sorted_years:
        organized_papers.extend(papers_by_year[year])
    
    return organized_papers

def save_to_csv(papers, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['year', 'citations', 'title', 'authors', 'venue']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)