def classify_publications(papers):
    classified_papers = []
    for paper in papers:
        if 'journal' in paper['venue'].lower():
            paper['type'] = 'journal'
        elif 'conference' in paper['venue'].lower() or 'proceedings' in paper['venue'].lower():
            paper['type'] = 'conference'
        else:
            paper['type'] = 'other'
        classified_papers.append(paper)
    return classified_papers
