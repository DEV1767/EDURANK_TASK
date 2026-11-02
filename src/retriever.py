import os
import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from src.chunker import knowledgeBaseChunker


class KnowledgeBaseRetriever:
    """Search engine over knowledge base document chunks using BM25."""

    def __init__(self, docs_dir: str):
        self.docs_dir = docs_dir
        self.chunker = knowledgeBaseChunker(chunk_size=600, chunk_overlap=60)

      
        self.all_chunks: List[Document] = self.chunker.chunk_directory(docs_dir)

       
        self.public_active_chunks: List[Document] = [
            doc for doc in self.all_chunks
            if doc.metadata.get("status") == "ACTIVE"
            and doc.metadata.get("audience") == "public"
        ]

       
        self.tokenized_corpus = [
            doc.page_content.lower().split() for doc in self.public_active_chunks
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Returns the top_k most relevant active public document chunks for a query."""
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        top_indices = ranked_indices[:top_k]

        return [self.public_active_chunks[i] for i in top_indices]


if __name__ == "__main__":
    docs_path = r"c:\Users\Shivam\Desktop\Task\data\docs"
    retriever = KnowledgeBaseRetriever(docs_path)

    test_query = "What is the restocking fee for electronics?"
    results = retriever.retrieve(test_query, top_k=2)

    print(f"Query: '{test_query}'\n")
    for i, doc in enumerate(results):
        print(f"--- [Result {i+1}] Source: {doc.metadata.get('source')} | Section: {doc.metadata.get('section_title')} ---")
        print(doc.page_content[:200], "...\n")
