import os
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from lancedb.rerankers import RRFReranker
from typing import List, Dict, Any, Optional

# 1. Configure Local Embedding Model
# BAAI/bge-small-en-v1.5 produces high-quality 384-dim embeddings locally
embeddings = (
    get_registry()
    .get("sentence-transformers")
    .create(name="BAAI/bge-small-en-v1.5", device="cpu")
)

# 2. Define Pydantic Schema for Forensic Documents
class ForensicStandardChunk(LanceModel):
    id: str
    doc_title: str          # e.g., "NFPA 921: Guide for Fire and Explosion Investigations"
    standard_code: str      # e.g., "NFPA 921", "OSAC 2021-N-0001"
    section_number: str     # e.g., "Section 6.2.1", "Clause 4.3"
    content: str = embeddings.SourceField()
    vector: Vector(embeddings.ndims()) = embeddings.VectorField()


class ForensicVectorStore:
    def __init__(self, db_path: str = "./forensic_lancedb"):
        """Initializes embedded LanceDB database locally."""
        self.db = lancedb.connect(db_path)
        self.table_name = "forensic_standards"
        self.table = self._get_or_create_table()

    def _get_or_create_table(self):
        if self.table_name in self.db.table_names():
            return self.db.open_table(self.table_name)
        else:
            table = self.db.create_table(
                self.table_name,
                schema=ForensicStandardChunk,
                mode="overwrite"
            )
            return table

    def ingest_documents(self, chunks: List[Dict[str, Any]]):
        """
        Ingests processed document chunks and creates full-text search index.
        """
        data = [
            ForensicStandardChunk(
                id=f"{chunk['standard_code']}_{idx}",
                doc_title=chunk["doc_title"],
                standard_code=chunk["standard_code"],
                section_number=chunk["section_number"],
                content=chunk["content"]
            )
            for idx, chunk in enumerate(chunks)
        ]
        
        self.table.add(data)
        
        # Create Full-Text Search (FTS) index on the text field for keyword matching
        self.table.create_fts_index("content", replace=True)
        print(f"[INGESTION] Successfully indexed {len(data)} forensic standard chunks.")

    def search_hybrid(self, query: str, top_k: int = 3, filter_standard: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Performs Hybrid Search (Vector Similarity + BM25 Keyword Search) 
        and reranks results using Reciprocal Rank Fusion (RRF).
        """
        search_query = self.table.search(
            query=query, 
            query_type="hybrid"
        ).rerank(reranker=RRFReranker())

        if filter_standard:
            search_query = search_query.where(f"standard_code = '{filter_standard}'", prefilter=True)

        results = search_query.limit(top_k).to_pandas()
        
        formatted_results = []
        for _, row in results.iterrows():
            formatted_results.append({
                "standard_code": row["standard_code"],
                "section": row["section_number"],
                "doc_title": row["doc_title"],
                "content": row["content"],
                "score": float(row["_relevance_score"]) if "_relevance_score" in row else None
            })
            
        return formatted_results


# --- DEMO EXECUTION ---
if __name__ == "__main__":
    # Sample corpus simulating chunks from NFPA 921 and OSAC standards
    sample_forensic_corpus = [
        {
            "doc_title": "NFPA 921: Guide for Fire and Explosion Investigations",
            "standard_code": "NFPA 921",
            "section_number": "Chapter 6.2.1",
            "content": "Char Patterns. The density, depth, and appearance of char can provide information regarding the intensity and duration of exposure to a heat source. Fast heat release rates produce clean burn patterns, whereas prolonged low-intensity fires produce deep alligator charring."
        },
        {
            "doc_title": "NFPA 921: Guide for Fire and Explosion Investigations",
            "standard_code": "NFPA 921",
            "section_number": "Chapter 8.4.2",
            "content": "Arc Mapping. Arcing occurs when an electrical circuit short-circuits due to external fire heat destroying wire insulation or localized electrical failure. Primary arcing occurs before fire damage, while secondary arcing occurs due to fire melting conductor insulation."
        },
        {
            "doc_title": "OSAC Preferred Terms for Friction Ridge Analysis",
            "standard_code": "OSAC 2021-N-0001",
            "section_number": "Section 3.1",
            "content": "Level 2 Detail. Specific friction ridge formations including bifurcations, ridge endings, dots, islands, and continuous ridges. Level 2 details are used in conjunction with Level 1 pattern flow to establish individualization or exclusion."
        }
    ]

    # Initialize store and ingest
    store = ForensicVectorStore()
    store.ingest_documents(sample_forensic_corpus)

    # Perform Hybrid Query
    query = "How do you distinguish primary electrical arcing from fire secondary arcing?"
    print(f"\n[QUERY]: '{query}'\n" + "-"*50)
    
    results = store.search_hybrid(query=query, top_k=2)
    for res in results:
        print(f"[{res['standard_code']} - {res['section']}] (Score: {res['score']:.4f})")
        print(f"Text: {res['content']}\n")
