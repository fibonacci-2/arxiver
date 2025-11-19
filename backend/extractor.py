from PyPDF2 import PdfReader
import arxiv
import re

def clean_text(text):
    """Clean text to remove problematic Unicode characters that cause encoding issues."""
    # Remove or replace surrogate characters and other problematic Unicode characters
    # Surrogates are in the range U+D800 to U+DFFF
    text = re.sub(r'[\ud800-\udfff]', '', text)
    
    # Remove other common problematic characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', ' ', text)
    
    # Replace multiple whitespaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Ensure the text can be encoded as UTF-8
    try:
        text.encode('utf-8')
        return text
    except UnicodeEncodeError:
        # If there are still encoding issues, use a more aggressive approach
        return text.encode('utf-8', 'ignore').decode('utf-8')

def extract_text(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += clean_text(page_text) + "\n"
        
        # Clean the final text
        text = clean_text(text.strip())
        
        filename = pdf_path.split("/")[-1].replace(".pdf", "")
        arxiv_id = filename.replace('_', '/')
        
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        paper = next(client.results(search))
        
        metadata = {
            "title": clean_text(paper.title),
            "authors": [clean_text(author.name) for author in paper.authors],
            "published": paper.published.strftime("%Y-%m-%d"),
            "arxiv_id": paper.get_short_id()
        }
        
        return text, metadata
    except StopIteration:
        raise Exception(f"Could not find metadata for paper {arxiv_id}")
    except Exception as e:
        raise Exception(f"Error extracting text from {pdf_path}: {str(e)}")
