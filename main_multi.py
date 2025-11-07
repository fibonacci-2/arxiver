import sys
import os
from dotenv import load_dotenv
from searcher import search_papers
from ranker import rank_papers
from fetcher import fetch_paper
from extractor import extract_text
from multi_summarizer import summarize_multiple_papers
from report_generator import generate_report_pdf

def main():
    load_dotenv()
    
    if len(sys.argv) < 2:
        print("Usage: python main_multi.py '<topic query>'")
        print("Example: python main_multi.py 'transformer models in NLP'")
        sys.exit(1)
    
    topic = " ".join(sys.argv[1:])
    
    os.makedirs("papers", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)
    
    print(f"Searching for papers on: {topic}")
    papers = search_papers(topic, max_results=10)
    print(f"Found {len(papers)} papers")
    
    print("Ranking papers by relevance...")
    top_papers = rank_papers(papers, topic, top_k=5)
    print(f"Selected top {len(top_papers)} papers:")
    for i, paper in enumerate(top_papers, 1):
        print(f"  {i}. {paper['title']}")
    
    print("\nDownloading and extracting papers...")
    papers_data = []
    for paper in top_papers:
        arxiv_id = paper['arxiv_id']
        print(f"  Processing {arxiv_id}...")
        pdf_path = fetch_paper(arxiv_id)
        text, metadata = extract_text(pdf_path)
        papers_data.append({
            'text': text,
            'metadata': metadata
        })
    
    print("\nGenerating comprehensive report...")
    report = summarize_multiple_papers(papers_data, topic)
    
    print("Creating report PDF...")
    topic_slug = topic.replace(' ', '_')[:50]
    output_path = f"outputs/{topic_slug}_report.pdf"
    generate_report_pdf(report, top_papers, topic, output_path)
    
    print(f"\nReport saved to {output_path}")

if __name__ == "__main__":
    main()
