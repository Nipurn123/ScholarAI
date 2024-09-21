def remove_duplicates(papers):
    unique_papers = {}
    for paper in papers:
        key = (paper['title'], tuple(paper['authors']), paper['year'])
        if key not in unique_papers or paper['citations'] > unique_papers[key]['citations']:
            unique_papers[key] = paper
    return list(unique_papers.values())