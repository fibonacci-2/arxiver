from PyPDF2 import PdfReader
import arxiv

def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    arxiv_id = pdf_path.split("/")[-1].replace(".pdf", "")
    client = arxiv.Client()
    search = arxiv.Search(id_list=[arxiv_id])
    paper = next(client.results(search))
    
    metadata = {
        "title": paper.title,
        "authors": [author.name for author in paper.authors],
        "published": paper.published.strftime("%Y-%m-%d"),
        "arxiv_id": arxiv_id
    }
    
    return text, metadata
