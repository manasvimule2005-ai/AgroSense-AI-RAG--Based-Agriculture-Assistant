"""
AgroSense AI - FAISS Vector Store Manager
Handles FAISS index lifecycle: creation, on-disk persistence, similarity ranking, and source metadata retrieval.
"""

import os
import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from src.config import VECTOR_STORE_DIR, KB_DIR, AppConfig
from src.rag.document_loader import AgroDocumentLoader
from src.rag.embeddings import get_embedding_engine, DenseTfidfEmbeddings


class AgroVectorStore:
    """FAISS-backed semantic retrieval engine for agricultural intelligence."""

    def __init__(self, store_dir: Path = VECTOR_STORE_DIR):
        self.store_dir = store_dir
        self.index_name = "faiss_agri_index"
        self._vector_store: Optional[FAISS] = None
        self._meta_cache: List[Document] = []
        self._embedding_engine = None

    def is_indexed(self) -> bool:
        """Checks if a saved index exists on disk."""
        faiss_file = self.store_dir / f"{self.index_name}.faiss"
        pkl_file = self.store_dir / f"{self.index_name}.pkl"
        return faiss_file.exists() and pkl_file.exists()

    def build_index(self, force_rebuild: bool = False) -> FAISS:
        """Loads all documents from knowledge base, computes embeddings, and builds FAISS index."""
        if not force_rebuild and self.is_indexed() and self._vector_store is not None:
            return self._vector_store

        # 1. Load documents
        loader = AgroDocumentLoader()
        raw_docs = loader.load_all_documents()
        if not raw_docs:
            # Create a placeholder if knowledge base is empty
            raw_docs = [Document(
                page_content="AgroSense AI Knowledge Base: Verified agricultural practices from ICAR, FAO, and State Agricultural Universities.",
                metadata={"source": "system_default.md", "title": "System Default Knowledge", "type": "md"}
            )]

        # 2. Chunk documents
        chunks = loader.chunk_documents(raw_docs)
        self._meta_cache = chunks

        # 3. Initialize embeddings
        texts = [c.page_content for c in chunks]
        self._embedding_engine = get_embedding_engine(texts_for_fitting=texts)

        # 4. Build FAISS index
        self._vector_store = FAISS.from_documents(chunks, self._embedding_engine)

        # 5. Persist to disk
        self.save()
        return self._vector_store

    def save(self):
        """Saves FAISS index and metadata to disk."""
        if self._vector_store:
            self.store_dir.mkdir(parents=True, exist_ok=True)
            self._vector_store.save_local(str(self.store_dir), index_name=self.index_name)

    def load(self) -> Optional[FAISS]:
        """Loads saved FAISS index from disk."""
        if not self.is_indexed():
            return self.build_index()

        try:
            # Try to load existing index
            # If TF-IDF is used, we re-fit on existing documents to maintain feature mapping
            loader = AgroDocumentLoader()
            raw_docs = loader.load_all_documents()
            chunks = loader.chunk_documents(raw_docs)
            texts = [c.page_content for c in chunks]

            self._embedding_engine = get_embedding_engine(texts_for_fitting=texts)
            self._vector_store = FAISS.load_local(
                str(self.store_dir),
                self._embedding_engine,
                index_name=self.index_name,
                allow_dangerous_deserialization=True
            )
            self._meta_cache = chunks
            return self._vector_store
        except Exception as e:
            print(f"Warning: Failed to load cached index ({e}), rebuilding fresh...")
            return self.build_index(force_rebuild=True)

    def search(self, query: str, top_k: Optional[int] = None) -> List[Tuple[Document, float]]:
        """Retrieves top-k relevant chunks with similarity score."""
        if self._vector_store is None:
            self.load()

        k = top_k or AppConfig.get_retrieval_top_k()
        try:
            results = self._vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the vector store."""
        loader = AgroDocumentLoader()
        raw_docs = loader.load_all_documents()
        total_sources = len(set(d.metadata.get("source", "") for d in raw_docs))

        total_chunks = len(self._meta_cache) if self._meta_cache else len(loader.chunk_documents(raw_docs))
        index_size_kb = 0
        faiss_file = self.store_dir / f"{self.index_name}.faiss"
        if faiss_file.exists():
            index_size_kb = round(faiss_file.stat().st_size / 1024, 1)

        return {
            "total_documents": len(raw_docs),
            "total_sources": total_sources,
            "total_chunks": total_chunks,
            "index_size_kb": index_size_kb,
            "status": "Ready" if self.is_indexed() else "Unindexed"
        }
