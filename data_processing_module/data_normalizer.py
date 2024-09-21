def normalize_data(papers):
    normalized_papers = []
    for paper in papers:
        normalized_paper = {
            'title': paper['title'].strip().lower(),
            'authors': [author.strip() for author in paper['authors'].split(',')],
            'year': paper['year'].strip(),
            'venue': paper['venue'].strip(),
            'citations': int(paper['citations']) if paper['citations'] != 'N/A' else 0
        }
        normalized_papers.append(normalized_paper)
    return normalized_papers