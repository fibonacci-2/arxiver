import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from config_loader import config

def summarize_paper(text, metadata):
    chunk_size = config.get('indexer', 'chunk_size')
    chunk_overlap = config.get('indexer', 'chunk_overlap')
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_text(text)
    
    embedding_model = config.get('embeddings', 'model')
    embeddings = OpenAIEmbeddings(model=embedding_model)
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    
    model_name = config.get('llm', 'model')
    temperature = config.get('llm', 'temperature')
    llm = ChatOpenAI(model=model_name, temperature=temperature)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.invoke(f"Summarize the paper titled '{metadata['title']}'")
    
    context = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"""Use the following context to create a concise summary of the research paper.
Include: main objective, methodology, key findings, and conclusion.
Keep it brief and clear, suitable for a 1-2 page summary document.

Context: {context}

Paper Title: {metadata['title']}

Summary:"""
    
    response = llm.invoke(prompt)
    return response.content
