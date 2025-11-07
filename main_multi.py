import sys
import os
from dotenv import load_dotenv
from searcher import search_papers
from ranker import rank_papers
from fetcher import fetch_paper
from extractor import extract_text
from multi_summarizer import summarize_multiple_papers
from report_generator import generate_report_pdf
from config_loader import config
from logger import log_step, log_info, log_config, console

def main():
    load_dotenv()
    
    if len(sys.argv) < 2:
        console.print("[red]Usage:[/red] python main_multi.py '<topic query>'")
        console.print("[yellow]Example:[/yellow] python main_multi.py 'transformer models in NLP'")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    os.makedirs("papers", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    log_config(config.data)
    
    log_step("Searching ArXiv")
    log_info(f"Query: '{topic}'")
    papers = search_papers(topic)
    log_info(f"Found {len(papers)} papers")
    
    log_step("Ranking Papers")
    log_info(f"Using embeddings model: {config.get('embeddings', 'model')}")
    top_papers = rank_papers(papers, topic)
    log_info(f"Selected top {len(top_papers)} papers")
    for i, paper in enumerate(top_papers, 1):
        console.print(f"    {i}. {paper['title'][:80]}...")
    
    log_step("Downloading & Extracting Papers")
    papers_data = []
    for i, paper in enumerate(top_papers, 1):
        arxiv_id = paper['arxiv_id']
        log_info(f"[{i}/{len(top_papers)}] {arxiv_id}")
        pdf_path = fetch_paper(arxiv_id)
        text, metadata = extract_text(pdf_path)
        papers_data.append({
            'text': text,
            'metadata': metadata
        })
    
    log_step("Generating Report")
    log_info(f"Using indexer: {config.get('indexer', 'type')}")
    log_info(f"Using LLM: {config.get('llm', 'model')}")
    report = summarize_multiple_papers(papers_data, topic)
    
    log_step("Creating PDF")
    log_info(f"Format: {config.get('output', 'format')}")
    topic_slug = topic.replace(' ', '_')[:50]
    output_path = f"outputs/{topic_slug}_report.pdf"
    generate_report_pdf(report, top_papers, topic, output_path)
    
    console.print(f"\n[bold green]✓ Report saved to:[/bold green] [cyan]{output_path}[/cyan]\n")

if __name__ == "__main__":
    main()
