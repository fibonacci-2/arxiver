from langchain_openai import OpenAIEmbeddings
from config_loader import config
import numpy as np

def rank_papers(papers, topic, top_k=None):
    if top_k is None:
        top_k = config.get('search', 'top_papers')
    
    embedding_model = config.get('embeddings', 'model')
    embeddings = OpenAIEmbeddings(model=embedding_model)
    
    topic_embedding = embeddings.embed_query(topic)
    
    paper_texts = [
        f"{p['title']} {p['summary']}" for p in papers
    ]
    paper_embeddings = embeddings.embed_documents(paper_texts)
    
    similarities = []
    for paper_emb in paper_embeddings:
        similarity = np.dot(topic_embedding, paper_emb) / (
            np.linalg.norm(topic_embedding) * np.linalg.norm(paper_emb)
        )
        similarities.append(similarity)
    
    ranked_indices = np.argsort(similarities)[::-1][:top_k]
    
    ranked_papers = [papers[i] for i in ranked_indices]
    
    return ranked_papers
