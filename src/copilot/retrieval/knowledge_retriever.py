"""
Deterministic Knowledge Retriever for VyaparMitra business and domain documentation.
Indexes markdown documentation in data/knowledge/ and provides keyword / BM25-style matching.
"""

from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.copilot.schemas import Fact, SourceReference


class KnowledgeChunk:
    def __init__(self, doc_name: str, title: str, content: str, chunk_id: str):
        self.doc_name = doc_name
        self.title = title
        self.content = content.strip()
        self.chunk_id = chunk_id
        # Tokenize for BM25/keyword scoring
        self.tokens = self._tokenize(f"{title} {content}")

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        return [t for t in cleaned.split() if len(t) > 2]


class KnowledgeRetriever:
    """
    Retriever for business glossaries, FAQ, metric definitions, and capability guides.
    Performs deterministic term-frequency and BM25-like scoring over document chunks.
    """

    def __init__(self, knowledge_dir: str = "data/knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.chunks: List[KnowledgeChunk] = []
        self._doc_lengths: List[int] = []
        self._avg_dl: float = 0.0
        self._df: Dict[str, int] = {}
        self._num_docs: int = 0
        self._load_and_index()

    def _load_and_index(self) -> None:
        """Loads all markdown files in knowledge directory and indexes sections."""
        if not self.knowledge_dir.exists():
            return

        md_files = list(self.knowledge_dir.glob("*.md"))
        chunks: List[KnowledgeChunk] = []

        for fpath in md_files:
            try:
                text = fpath.read_text(encoding="utf-8")
                doc_name = fpath.name
                file_chunks = self._chunk_markdown(doc_name, text)
                chunks.extend(file_chunks)
            except Exception:
                continue

        self.chunks = chunks
        self._num_docs = len(self.chunks)
        if self._num_docs == 0:
            return

        self._doc_lengths = [len(c.tokens) for c in self.chunks]
        self._avg_dl = sum(self._doc_lengths) / max(self._num_docs, 1)

        # Compute document frequency for each token
        df: Dict[str, int] = {}
        for c in self.chunks:
            unique_tokens = set(c.tokens)
            for t in unique_tokens:
                df[t] = df.get(t, 0) + 1
        self._df = df

    def _chunk_markdown(self, doc_name: str, text: str) -> List[KnowledgeChunk]:
        """Splits markdown into header-based chunks."""
        sections = re.split(r"\n(?=#{1,3}\s+)", text)
        result = []
        doc_base = os.path.splitext(doc_name)[0]

        for idx, sec in enumerate(sections):
            sec = sec.strip()
            if not sec:
                continue
            lines = sec.splitlines()
            first_line = lines[0].strip()
            title = re.sub(r"^#{1,3}\s+", "", first_line) if first_line.startswith("#") else f"{doc_base} section {idx+1}"
            body = "\n".join(lines[1:]).strip() if len(lines) > 1 else sec
            chunk_id = f"{doc_base}_{idx+1}"
            result.append(KnowledgeChunk(doc_name=doc_name, title=title, content=sec, chunk_id=chunk_id))

        return result

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches knowledge documents for matching chunks using BM25 ranking.
        Returns list of matched chunks with score, title, document, and text content.
        """
        if not self.chunks:
            return []

        q_tokens = KnowledgeChunk._tokenize(query)
        if not q_tokens:
            return []

        k1 = 1.5
        b = 0.75
        scored_chunks: List[Tuple[float, KnowledgeChunk]] = []

        for idx, chunk in enumerate(self.chunks):
            doc_len = self._doc_lengths[idx]
            if doc_len == 0:
                continue

            score = 0.0
            # Term counts in chunk
            term_counts: Dict[str, int] = {}
            for t in chunk.tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for qt in q_tokens:
                if qt in term_counts:
                    tf = term_counts[qt]
                    n_q = self._df.get(qt, 0)
                    # Standard BM25 IDF
                    idf = math.log((self._num_docs - n_q + 0.5) / (n_q + 0.5) + 1.0)
                    # BM25 TF component
                    tf_component = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / self._avg_dl)))
                    score += idf * tf_component

            if score > 0.0:
                scored_chunks.append((score, chunk))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_results = scored_chunks[:top_k]

        return [
            {
                "doc_name": chunk.doc_name,
                "title": chunk.title,
                "content": chunk.content,
                "score": round(score, 4),
                "chunk_id": chunk.chunk_id,
            }
            for score, chunk in top_results
        ]

    def get_facts_and_sources(self, query: str, top_k: int = 3) -> Tuple[List[Fact], List[SourceReference]]:
        """Returns structured Fact and SourceReference objects for context builder."""
        results = self.search(query, top_k=top_k)
        facts: List[Fact] = []
        sources: List[SourceReference] = []

        for r in results:
            facts.append(
                Fact(
                    key=r["title"],
                    value=r["content"][:250].replace("\n", " "),
                    source=f"knowledge/{r['doc_name']}",
                    category="knowledge",
                )
            )
            sources.append(
                SourceReference(
                    source="knowledge_base",
                    artifact=f"data/knowledge/{r['doc_name']}",
                    entity=r["title"],
                    description=f"Section '{r['title']}' from {r['doc_name']}",
                )
            )

        return facts, sources
