import arxiv
import os

def fetch_paper(arxiv_id):
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(client.results(search))
    
    pdf_path = f"papers/{arxiv_id}.pdf"
    paper.download_pdf(filename=pdf_path)
    
    return pdf_path
