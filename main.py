import sys
import os
from dotenv import load_dotenv
from fetcher import fetch_paper
from extractor import extract_text
from summarizer import summarize_paper
from generator import generate_pdf

def main():
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    
    os.makedirs("papers", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    print(f"Fetching paper {arxiv_id}...")
    pdf_path = fetch_paper(arxiv_id)
    
    print("Extracting text...")
    text, metadata = extract_text(pdf_path)
    
    print("Generating summary...")
    summary = summarize_paper(text, metadata)
    
    print("Creating PDF...")
    output_path = f"outputs/{arxiv_id}_summary.pdf"
    generate_pdf(summary, metadata, output_path)
    
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    main()
