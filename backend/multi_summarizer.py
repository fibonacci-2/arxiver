import os
from langchain_openai import ChatOpenAI
from .config_loader import config
from .indexers import get_indexer

def summarize_multiple_papers(papers_data, topic, query_spec=None):
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
    
    citation_map = "\n".join([f"Paper {i+1}: {p['metadata']['title']}" for i, p in enumerate(papers_data)])
    
    if query_spec:
        themes_section = "\n".join([f"- {theme}" for theme in query_spec.get('themes', [])])
        structure_section = "\n".join([f"{i+1}. {s}" for i, s in enumerate(query_spec.get('structure', []))])
        special_req = query_spec.get('special_requirements', '')
        
        prompt = f"""Create a comprehensive research report on the topic: {topic}

The report should synthesize findings from the following papers:
{paper_list}

Citation mapping (use these in your report):
{citation_map}

SPECIFIC THEMES TO EMPHASIZE:
{themes_section}

SUGGESTED REPORT STRUCTURE:
{structure_section}

SPECIAL REQUIREMENTS:
{special_req}

Use the context below from the papers:
{context}

Generate the report in LaTeX format following these requirements:

1. START with an abstract (\\begin{{abstract}}...\\end{{abstract}}) that summarizes the report in 150-200 words

2. Use proper sections and subsections (\\section, \\subsection)

3. IMPORTANT: Use citations throughout the text using \\cite{{paper1}}, \\cite{{paper2}}, etc.
   - Cite papers when referencing their methods, results, or findings
   - Use multiple citations when comparing: \\cite{{paper1,paper2}}
   - Ensure every paper is cited at least once in the body

4. Follow the suggested structure and emphasize the specified themes

5. Output ONLY the document body content (no preamble, no \\documentclass, no \\begin{{document}})

6. Properly escape special LaTeX characters"""
    else:
        prompt = f"""Create a comprehensive research report on the topic: {topic}

The report should synthesize findings from the following papers:
{paper_list}

Citation mapping (use these in your report):
{citation_map}

Use the context below to write a cohesive report covering:
1. Introduction to the topic
2. Key methodologies across papers
3. Main findings and results
4. Comparison of approaches
5. Conclusions and future directions

Context from papers:
{context}

Generate the report in LaTeX format following these requirements:

1. START with an abstract (\\begin{{abstract}}...\\end{{abstract}}) that summarizes the report in 150-200 words

2. Use proper sections and subsections (\\section, \\subsection)

3. IMPORTANT: Use citations throughout the text using \\cite{{paper1}}, \\cite{{paper2}}, etc.
   - Cite papers when referencing their methods, results, or findings
   - Use multiple citations when comparing: \\cite{{paper1,paper2}}
   - Ensure every paper is cited at least once in the body

4. Output ONLY the document body content (no preamble, no \\documentclass, no \\begin{{document}})

5. Properly escape special LaTeX characters"""
    
    response = llm.invoke(prompt)
    return response.content
