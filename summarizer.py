import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

def summarize_paper(text, metadata):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_text(text)
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="chroma_db"
    )
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
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
