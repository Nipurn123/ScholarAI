from datetime import datetime

def filter_by_date(papers, start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    filtered_papers = []
    for paper in papers:
        try:
            paper_date = datetime.strptime(paper['year'], '%Y')
            if start <= paper_date <= end:
                filtered_papers.append(paper)
        except ValueError:
            # If the year is not in the correct format, skip this paper
            continue
    
    return filtered_papers