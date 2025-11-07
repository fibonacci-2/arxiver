import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

def summarize_multiple_papers(papers_data, topic):
    all_chunks = []
    chunk_metadata = []
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    for paper_data in papers_data:
        text = paper_data['text']
        metadata = paper_data['metadata']
        
        chunks = text_splitter.split_text(text)
        all_chunks.extend(chunks)
        
        for _ in chunks:
            chunk_metadata.append({
                'title': metadata['title'],
                'arxiv_id': metadata['arxiv_id']
            })
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_texts(
        texts=all_chunks,
        embedding=embeddings,
        metadatas=chunk_metadata,
        persist_directory="chroma_db_multi"
    )
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    relevant_docs = retriever.invoke(f"Research about {topic}")
    
    context = "\n\n".join([
        f"[From: {doc.metadata['title']}]\n{doc.page_content}" 
        for doc in relevant_docs
    ])
    
    paper_list = "\n".join([
        f"- {p['metadata']['title']} (arXiv:{p['metadata']['arxiv_id']})"
        for p in papers_data
    ])
    
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

Generate a well-structured report:"""
    
    response = llm.invoke(prompt)
    return response.content
