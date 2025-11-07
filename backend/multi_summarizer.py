import os
from langchain_openai import ChatOpenAI
from .config_loader import config
from .indexers import get_indexer

def summarize_multiple_papers(papers_data, topic):
    indexer_type = config.get('indexer', 'type')
    chunk_size = config.get('indexer', 'chunk_size')
    chunk_overlap = config.get('indexer', 'chunk_overlap')
    top_k = config.get('indexer', 'top_k')
    
    indexer = get_indexer(indexer_type, chunk_size, chunk_overlap)
    indexer.index(papers_data)
    
    relevant_docs = indexer.retrieve(f"Research about {topic}", top_k)
    
    context_parts = []
    for doc in relevant_docs:
        if hasattr(doc, 'page_content'):
            title = doc.metadata['title']
            content = doc.page_content
        else:
            title = doc['metadata']['title']
            content = doc['page_content']
        context_parts.append(f"[From: {title}]\n{content}")
    
    context = "\n\n".join(context_parts)
    
    paper_list = "\n".join([
        f"- {p['metadata']['title']} (arXiv:{p['metadata']['arxiv_id']})"
        for p in papers_data
    ])
    
    model_name = config.get('llm', 'model')
    temperature = config.get('llm', 'temperature')
    
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    
    prompt = f"""Create a comprehensive research report on the topic: {topic}

The report should synthesize findings from the following papers:
{paper_list}

Use the context below to write a cohesive report covering:
1. Introduction to the topic
2. Key methodologies across papers
3. Main findings and results
4. Comparison of approaches
5. Conclusions and future directions

Context from papers:
{context}

Generate the report in LaTeX format with proper sections, subsections, and citations.
Use \\section, \\subsection for structure. Output only the document body content (no preamble or document environment).
Escape special characters properly. Use \\cite{{paper1}}, \\cite{{paper2}}, etc. for references."""
    
    response = llm.invoke(prompt)
    return response.content
