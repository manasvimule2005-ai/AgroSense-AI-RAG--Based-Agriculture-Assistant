"""
AgroSense AI - Agricultural Document Ingestion & Chunking
Loads PDF, DOCX, Markdown, Text, and CSV files, extracts structured metadata, and performs recursive chunking.
"""

from pathlib import Path
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import KB_DIR, AppConfig


class AgroDocumentLoader:
    """Ingests agricultural manuals, guidelines, and advisory datasets."""

    def __init__(self, kb_dir: Path = KB_DIR):
        self.kb_dir = kb_dir

    def load_single_file(self, file_path: Path) -> List[Document]:
        """Loads a single document from disk and returns Document objects with metadata."""
        ext = file_path.suffix.lower()
        docs = []

        try:
            if ext in [".md", ".txt"]:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                # Derive title from first header or filename
                lines = [line.strip() for line in content.split("\n") if line.strip()]
                title = lines[0].lstrip("#").strip() if lines and lines[0].startswith("#") else file_path.stem.replace("_", " ").title()
                docs.append(Document(
                    page_content=content,
                    metadata={"source": file_path.name, "title": title, "type": ext.lstrip(".")}
                ))

            elif ext == ".pdf":
                from pypdf import PdfReader
                reader = PdfReader(str(file_path))
                full_text = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        docs.append(Document(
                            page_content=text,
                            metadata={"source": file_path.name, "page": i + 1, "title": file_path.stem.replace("_", " ").title(), "type": "pdf"}
                        ))

            elif ext == ".docx":
                import docx
                doc = docx.Document(str(file_path))
                text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                docs.append(Document(
                    page_content=text,
                    metadata={"source": file_path.name, "title": file_path.stem.replace("_", " ").title(), "type": "docx"}
                ))

        except Exception as e:
            print(f"Error loading {file_path.name}: {e}")

        return docs

    def load_all_documents(self) -> List[Document]:
        """Loads all supported documents in knowledge_base directory."""
        all_docs = []
        if not self.kb_dir.exists():
            return all_docs

        for f in self.kb_dir.iterdir():
            if f.is_file() and f.suffix.lower() in [".md", ".txt", ".pdf", ".docx"]:
                all_docs.extend(self.load_single_file(f))

        return all_docs

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Splits raw documents into semantic chunks preserving metadata."""
        chunk_size = AppConfig.get_chunk_size()
        chunk_overlap = AppConfig.get_chunk_overlap()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
        )

        chunks = splitter.split_documents(documents)
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_id"] = i
        return chunks
