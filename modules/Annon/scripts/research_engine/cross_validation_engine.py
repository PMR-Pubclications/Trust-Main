from typing import Dict, List, Set
from urllib.parse import urlparse

class CrossValidationEngine:
    """
    Enforces a strict cross-validation threshold. 
    A claim or empirical finding is held as UNVERIFIED until at least 5 distinct, 
    independent sources (different domains or hardware device IDs) assert correlating data.
    """
    
    MIN_REQUIRED_INDEPENDENT_SOURCES = 5

    @classmethod
    def extract_source_identity(cls, document: Dict) -> str:
        """
        Extracts a unique source identifier to prevent multiple pages 
        from the same domain/owner from double-counting.
        """
        metadata = document.get("metadata", {})
        url = metadata.get("url", "")
        tee_device_id = metadata.get("tee_device_id", "")
        
        # Priority 1: Hardware-level TEE identifier
        if tee_device_id:
            return f"hardware_node:{tee_device_id}"
            
        # Priority 2: Root domain address (strips subdomains to enforce unique organization/owner)
        if url:
            netloc = urlparse(url).netloc.lower()
            parts = netloc.split(".")
            if len(parts) > 2:
                return ".".join(parts[-2:]) # e.g., 'sub.domain.com' -> 'domain.com'
            return netloc
            
        return document.get("source_id", "unknown_source")

    @classmethod
    def calculate_correlation_score(cls, doc_a: Dict, doc_b: Dict) -> float:
        """
        Evaluates physical metric and term correlation between two documents.
        """
        metrics_a = set(doc_a.get("extracted_metrics", []))
        metrics_b = set(doc_b.get("extracted_metrics", []))
        
        # 1. Physical metric alignment (Hz, dB, sample sizes, exact values)
        if metrics_a and metrics_b:
            shared_metrics = metrics_a.intersection(metrics_b)
            if shared_metrics:
                return 1.0  # Strong physical metric correlation
                
        # 2. Textual/Lexical token correlation fallback
        words_a = set(doc_a.get("content", "").lower().split())
        words_b = set(doc_b.get("content", "").lower().split())
        
        # Strip common stopwords
        stopwords = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is"}
        words_a -= stopwords
        words_b -= stopwords
        
        if not words_a or not words_b:
            return 0.0
            
        jaccard_similarity = len(words_a.intersection(words_b)) / len(words_a.union(words_b))
        return jaccard_similarity

    @classmethod
    def validate_consensus(cls, ranked_documents: List[Dict]) -> Dict:
        """
        Groups incoming documents by correlation and verifies whether any cluster
        meets or exceeds the 5-independent-source threshold.
        """
        claim_clusters = []

        for doc in ranked_documents:
            source_id = cls.extract_source_identity(doc)
            matched_cluster = None

            # Attempt to match document with an existing correlated claim cluster
            for cluster in claim_clusters:
                representative_doc = cluster["documents"][0]
                correlation = cls.calculate_correlation_score(doc, representative_doc)
                
                if correlation > 0.15:  # Threshold for topic/metric alignment
                    matched_cluster = cluster
                    break

            if matched_cluster:
                matched_cluster["documents"].append(doc)
                matched_cluster["independent_sources"].add(source_id)
            else:
                claim_clusters.append({
                    "cluster_id": len(claim_clusters) + 1,
                    "documents": [doc],
                    "independent_sources": {source_id},
                    "is_verified": False
                })

        verified_findings = []
        unverified_hypotheses = []

        # Enforce the 5-source rule
        for cluster in claim_clusters:
            source_count = len(cluster["independent_sources"])
            cluster["source_count"] = source_count
            cluster["sources_list"] = list(cluster["independent_sources"])

            if source_count >= cls.MIN_REQUIRED_INDEPENDENT_SOURCES:
                cluster["is_verified"] = True
                cluster["verification_status"] = (
                    f"VERIFIED: Supported by {source_count} independent sources "
                    f"(Minimum required: {cls.MIN_REQUIRED_INDEPENDENT_SOURCES})"
                )
                verified_findings.append(cluster)
            else:
                cluster["is_verified"] = False
                cluster["verification_status"] = (
                    f"UNVERIFIED: Supported by only {source_count}/{cls.MIN_REQUIRED_INDEPENDENT_SOURCES} "
                    f"independent sources. Kept as unconfirmed hypothesis."
                )
                unverified_hypotheses.append(cluster)

        return {
            "verified_truth_findings": verified_findings,
            "unverified_hypotheses": unverified_hypotheses,
            "total_clusters_evaluated": len(claim_clusters)
        }
