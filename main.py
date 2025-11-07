import sys
import os
from dotenv import load_dotenv
from backend.fetcher import fetch_paper
from backend.extractor import extract_text
from backend.summarizer import summarize_paper
from backend.generator import generate_pdf
from backend.config_loader import config
from backend.logger import log_step, log_info, log_config, console

def main():
    load_dotenv()
    
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python main.py <arxiv_id>")
        sys.exit(1)
    
    arxiv_id = sys.argv[1]
    
    os.makedirs("data/papers", exist_ok=True)
    os.makedirs("data/outputs", exist_ok=True)
    
    log_config(config.data)
    
    log_step("Fetching Paper")
    log_info(f"ArXiv ID: {arxiv_id}")
    pdf_path = fetch_paper(arxiv_id)
    
    log_step("Extracting Text")
    text, metadata = extract_text(pdf_path)
    log_info(f"Title: {metadata['title']}")
    
    log_step("Generating Summary")
    log_info(f"Using LLM: {config.get('llm', 'model')}")
    summary = summarize_paper(text, metadata)
    
    log_step("Creating PDF")
    output_path = f"data/outputs/{arxiv_id}_summary.pdf"
    generate_pdf(summary, metadata, output_path)
    
    console.print(f"\n[bold green]✓ Summary saved to:[/bold green] [cyan]{output_path}[/cyan]\n")

if __name__ == "__main__":
    main()
