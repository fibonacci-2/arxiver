from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from sklearn.feature_extraction.text import TfidfVectorizer
from rank_bm25 import BM25Okapi
import numpy as np

class BaseIndexer:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    
    def index(self, papers_data):
        raise NotImplementedError
    
    def retrieve(self, query, top_k=10):
        raise NotImplementedError

class VectorIndexer(BaseIndexer):
    def index(self, papers_data):
        all_chunks = []
        chunk_metadata = []
        
        for paper_data in papers_data:
            text = paper_data['text']
            metadata = paper_data['metadata']
            
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            
            for _ in chunks:
                chunk_metadata.append({
                    'title': metadata['title'],
                    'arxiv_id': metadata['arxiv_id']
                })
        
        embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma.from_texts(
            texts=all_chunks,
            embedding=embeddings,
            metadatas=chunk_metadata,
            persist_directory="chroma_db_multi"
        )
    
    def retrieve(self, query, top_k=10):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": top_k})
        docs = retriever.invoke(query)
        return docs

class BM25Indexer(BaseIndexer):
    def index(self, papers_data):
        all_chunks = []
        self.chunk_metadata = []
        
        for paper_data in papers_data:
            text = paper_data['text']
            metadata = paper_data['metadata']
            
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            
            for _ in chunks:
                self.chunk_metadata.append({
                    'title': metadata['title'],
                    'arxiv_id': metadata['arxiv_id']
                })
        
        self.chunks = all_chunks
        tokenized_chunks = [chunk.lower().split() for chunk in all_chunks]
        self.bm25 = BM25Okapi(tokenized_chunks)
    
    def retrieve(self, query, top_k=10):
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        docs = []
        for idx in top_indices:
            docs.append({
                'page_content': self.chunks[idx],
                'metadata': self.chunk_metadata[idx]
            })
        return docs

class TFIDFIndexer(BaseIndexer):
    def index(self, papers_data):
        all_chunks = []
        self.chunk_metadata = []
        
        for paper_data in papers_data:
            text = paper_data['text']
            metadata = paper_data['metadata']
            
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            
            for _ in chunks:
                self.chunk_metadata.append({
                    'title': metadata['title'],
                    'arxiv_id': metadata['arxiv_id']
                })
        
        self.chunks = all_chunks
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.tfidf_matrix = self.vectorizer.fit_transform(all_chunks)
    
    def retrieve(self, query, top_k=10):
        query_vec = self.vectorizer.transform([query])
        scores = (self.tfidf_matrix * query_vec.T).toarray().flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        docs = []
        for idx in top_indices:
            docs.append({
                'page_content': self.chunks[idx],
                'metadata': self.chunk_metadata[idx]
            })
        return docs

class InvertedIndexer(BaseIndexer):
    def index(self, papers_data):
        all_chunks = []
        self.chunk_metadata = []
        
        for paper_data in papers_data:
            text = paper_data['text']
            metadata = paper_data['metadata']
            
            chunks = self.text_splitter.split_text(text)
            all_chunks.extend(chunks)
            
            for _ in chunks:
                self.chunk_metadata.append({
                    'title': metadata['title'],
                    'arxiv_id': metadata['arxiv_id']
                })
        
        self.chunks = all_chunks
        self.inverted_index = {}
        
        for doc_id, chunk in enumerate(all_chunks):
            words = set(chunk.lower().split())
            for word in words:
                if word not in self.inverted_index:
                    self.inverted_index[word] = []
                self.inverted_index[word].append(doc_id)
    
    def retrieve(self, query, top_k=10):
        query_words = set(query.lower().split())
        doc_scores = {}
        
        for word in query_words:
            if word in self.inverted_index:
                for doc_id in self.inverted_index[word]:
                    doc_scores[doc_id] = doc_scores.get(doc_id, 0) + 1
        
        top_doc_ids = sorted(doc_scores.keys(), key=lambda x: doc_scores[x], reverse=True)[:top_k]
        
        docs = []
        for doc_id in top_doc_ids:
            docs.append({
                'page_content': self.chunks[doc_id],
                'metadata': self.chunk_metadata[doc_id]
            })
        return docs

def get_indexer(indexer_type, chunk_size=1000, chunk_overlap=200):
    indexers = {
        'vector': VectorIndexer,
        'bm25': BM25Indexer,
        'tfidf': TFIDFIndexer,
        'inverted': InvertedIndexer
    }
    
    if indexer_type not in indexers:
        raise ValueError(f"Unknown indexer type: {indexer_type}")
    
    return indexers[indexer_type](chunk_size, chunk_overlap)
