import arxiv
import os

def fetch_paper(arxiv_id):
    try:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(client.results(search))
        
        clean_id = paper.get_short_id()
        safe_filename = clean_id.replace('/', '_')
        pdf_path = f"data/papers/{safe_filename}.pdf"
        
        if os.path.exists(pdf_path):
            return pdf_path
        
        paper.download_pdf(filename=pdf_path)
        
        return pdf_path
    except StopIteration:
        raise Exception(f"Paper {arxiv_id} not found on ArXiv")
    except Exception as e:
        raise Exception(f"Error fetching paper {arxiv_id}: {str(e)}")
