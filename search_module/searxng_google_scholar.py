import requests
from typing import List, Dict, Optional

class SearxngSearchOptions:
    def __init__(self, categories: Optional[List[str]] = None,
                 engines: Optional[List[str]] = None,
                 language: Optional[str] = None,
                 pageno: Optional[int] = None):
        self.categories = categories
        self.engines = engines
        self.language = language
        self.pageno = pageno

class SearxngSearchResult:
    def __init__(self, title: str, url: str, engine: str, **kwargs):
        self.title = title
        self.url = url
        self.engine = engine
        self.img_src = kwargs.get('img_src')
        self.thumbnail_src = kwargs.get('thumbnail_src')
        self.thumbnail = kwargs.get('thumbnail')
        self.content = kwargs.get('content')
        self.author = kwargs.get('author')
        self.iframe_src = kwargs.get('iframe_src')
        # Store any additional unexpected arguments
        self.additional_info = kwargs

def search_searxng(query: str, opts: Optional[SearxngSearchOptions] = None):
    searxng_url = "http://localhost:4000"
    url = f"{searxng_url}/search"
    
    params = {
        'q': query + ' site:scholar.google.com',  # Add site:scholar.google.com to the query
        'format': 'json'
    }
    
    if opts:
        for key, value in opts.__dict__.items():
            if value is not None:
                if isinstance(value, list):
                    params[key] = ','.join(value)
                else:
                    params[key] = value
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Filter results to only include those from scholar.google.com
    results = [SearxngSearchResult(**result) for result in data['results'] 
               if result.get('url', '').startswith('https://scholar.google.com')]
    suggestions = data.get('suggestions', [])
    
    return {'results': results, 'suggestions': suggestions}