from PyPDF2 import PdfReader
import arxiv

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        filename = pdf_path.split("/")[-1].replace(".pdf", "")
        arxiv_id = filename.replace('_', '/')
        
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(client.results(search))
        
        metadata = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "published": paper.published.strftime("%Y-%m-%d"),
            "arxiv_id": paper.get_short_id()
        }
        
        return text, metadata
    except StopIteration:
        raise Exception(f"Could not find metadata for paper {arxiv_id}")
    except Exception as e:
        raise Exception(f"Error extracting text from {pdf_path}: {str(e)}")
