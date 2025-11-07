import arxiv
import os

def fetch_paper(arxiv_id):
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(client.results(search))
    
    clean_id = paper.get_short_id()
    safe_filename = clean_id.replace('/', '_')
    pdf_path = f"data/papers/{safe_filename}.pdf"
    paper.download_pdf(filename=pdf_path)
    
    return pdf_path
