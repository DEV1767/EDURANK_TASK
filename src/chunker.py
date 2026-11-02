import os
import re
from typing import List, Dict, Any
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter
)
from langchain_core.documents import Document


class knowledgeBaseChunker:
    """
    Split markdown support documents into structured LangChain Document Chunks.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.headers_to_split_on = [
            ("#", "doc_title"),
            ("##", "section_title"),
            ("###", "subsection_title"),
        ]
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on,
            strip_headers=False
        )

        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "- ", " ", ""]
        )

    def _extract_file_metadata(self, text: str, filename: str) -> Dict[str, Any]:
        """Parses metadata from top matter/headers of the markdown files."""
        metadata: Dict[str, Any] = {
            "source": filename,
            "status": "ACTIVE",
            "audience": "public",
            "effective_date": "Unknown"
        }

        lower_name = filename.lower()
        if "legacy" in lower_name or "old" in lower_name or "2022" in lower_name or "2023" in lower_name:
            metadata["status"] = "OBSOLETE"
        
        if "internal" in lower_name or "CONFIDENTIAL" in text:
            metadata["audience"] = "internal"

        date_match = re.search(r"(?:Effective Date|Last Updated|Date|Posted)[*:\s]+([A-Za-z]+ \d{1,2}, \d{4})", text)
        if date_match:
            metadata["effective_date"] = date_match.group(1)

        return metadata

    def chunk_files(self, file_path: str) -> List[Document]:
        """Read a single markdown file and return enriched LangChain Documents."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        file_meta = self._extract_file_metadata(raw_text, path.name)

        header_splits = self.header_splitter.split_text(raw_text)
        final_docs = self.recursive_splitter.split_documents(header_splits)

        for doc in final_docs:
            doc.metadata.update(file_meta)
            if "section_title" not in doc.metadata:
                doc.metadata["section_title"] = doc.metadata.get("doc_title", path.stem)

        return final_docs

    def chunk_directory(self, docs_dir: str) -> List[Document]:
        """Loads and chunks all markdown documents in the target directory."""
        all_docs: List[Document] = []
        target_path = Path(docs_dir)

        if not target_path.exists():
            raise FileNotFoundError(f"Directory not found: {docs_dir}")
        
        for file in sorted(target_path.glob("*.md")):
            file_chunks = self.chunk_files(str(file))
            all_docs.extend(file_chunks)
        
        return all_docs


if __name__ == "__main__":
    import json
    DOCS_PATH = r"c:\Users\Shivam\Desktop\Task\data\docs"

    chunker = knowledgeBaseChunker(chunk_size=600, chunk_overlap=60)

    chunks = chunker.chunk_directory(DOCS_PATH)
    print(f"Total chunks generated: {len(chunks)}")

    for i, c in enumerate(chunks[:2]):
        print(f"\n--- [Chunk {i+1}] ---")
        print("Metadata:", json.dumps(c.metadata, indent=2))
        print("Content Preview:\n", c.page_content[:200], "...")
