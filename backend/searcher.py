import arxiv
from .config_loader import config

def search_papers(topic, max_results=None):
    if max_results is None:
        max_results = config.get('search', 'max_results')
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    papers = []
    for result in client.results(search):
        papers.append({
            'arxiv_id': result.get_short_id(),
            'title': result.title,
            'authors': [author.name for author in result.authors],
            'published': result.published.strftime("%Y-%m-%d"),
            'summary': result.summary,
            'pdf_url': result.pdf_url
        })
    
    return papers
