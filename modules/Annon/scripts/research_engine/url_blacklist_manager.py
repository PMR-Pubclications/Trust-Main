import json
import os
from typing import Dict, List, Set
from urllib.parse import urlparse

class URLBlacklistManager:
    """
    Tracks source validation failures across research cycles.
    If a domain or URL fails validation tests more than twice (3+ failures),
    it is permanently added to a local cryptographic asset/config blacklist 
    and rejected from future research execution pipelines.
    """

    DEFAULT_BLACKLIST_PATH = "config/blacklist.json"
    FAILURE_THRESHOLD = 2  # More than 2 failures triggers permanent blacklist

    def __init__(self, storage_path: str = DEFAULT_BLACKLIST_PATH):
        self.storage_path = storage_path
        self.failure_counts: Dict[str, int] = {}
        self.blacklisted_domains: Set[str] = set()
        self._load_state()

    def _extract_domain(self, url: str) -> str:
        """Extracts the root domain from a URL to prevent subdomain evasions."""
        if not url:
            return "unknown_source"
        netloc = urlparse(url).netloc.lower()
        parts = netloc.split(".")
        if len(parts) > 2:
            return ".".join(parts[-2:])
        return netloc

    def _load_state(self) -> None:
        """Loads persistent failure history and blacklists from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.failure_counts = data.get("failure_counts", {})
                    self.blacklisted_domains = set(data.get("blacklisted_domains", []))
            except (json.JSONDecodeError, OSError):
                self.failure_counts = {}
                self.blacklisted_domains = set()

    def _save_state(self) -> None:
        """Persists failure history and updated blacklists to disk."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        data = {
            "failure_counts": self.failure_counts,
            "blacklisted_domains": list(self.blacklisted_domains)
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def is_blacklisted(self, url_or_domain: str) -> bool:
        """Checks whether a given URL or domain is permanently blacklisted."""
        domain = self._extract_domain(url_or_domain) if "://" in url_or_domain else url_or_domain.lower()
        return domain in self.blacklisted_domains

    def record_failure(self, url_or_domain: str, reason: str = "Validation Test Failed") -> None:
        """
        Increments the failure counter for a source.
        If failures exceed 2 (i.e., 3 or more), it is permanently blacklisted.
        """
        domain = self._extract_domain(url_or_domain) if "://" in url_or_domain else url_or_domain.lower()

        if domain in self.blacklisted_domains:
            return  # Already permanently banned

        current_failures = self.failure_counts.get(domain, 0) + 1
        self.failure_counts[domain] = current_failures

        if current_failures > self.FAILURE_THRESHOLD:
            self.blacklisted_domains.add(domain)
            print(f"[PERMANENT BLACKLIST] Domain '{domain}' failed validation {current_failures} times. Permanently banned.")

        self._save_state()

    def filter_incoming_sources(self, search_results: List[Dict]) -> List[Dict]:
        """
        Filters out any documents originating from blacklisted domains 
        before research execution or ranking begins.
        """
        clean_results = []
        for doc in search_results:
            url = doc.get("metadata", {}).get("url", "")
            if not self.is_blacklisted(url):
                clean_results.append(doc)
            else:
                print(f"[REJECTED SOURCE] Dropped '{url}' — Permanently blacklisted due to prior validation failures.")
        return clean_results
