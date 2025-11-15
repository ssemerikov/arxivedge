"""
Metadata extraction and enrichment for ArXiv papers.
"""

import re
from typing import List, Dict, Any, Set, Tuple
from collections import Counter
import pandas as pd
from loguru import logger
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import requests
from bs4 import BeautifulSoup


class MetadataExtractor:
    """Extract and enrich metadata from ArXiv papers."""

    def __init__(self):
        """Initialize metadata extractor."""
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

        self.stop_words = set(stopwords.words('english'))

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text using frequency analysis.

        Args:
            text: Input text (abstract or title)
            max_keywords: Maximum number of keywords to extract

        Returns:
            list: List of extracted keywords
        """
        # Tokenize and clean
        words = word_tokenize(text.lower())

        # Remove stopwords and short words
        words = [
            w for w in words
            if w.isalnum() and len(w) > 3 and w not in self.stop_words
        ]

        # Count frequencies
        word_freq = Counter(words)

        # Get top keywords
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]

        return keywords

    def extract_author_affiliations(self, papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Extract author affiliations from papers.

        Note: ArXiv API doesn't provide affiliations directly.
        This is a placeholder for potential enhancement.

        Args:
            papers: List of paper dictionaries

        Returns:
            dict: Mapping of authors to affiliations
        """
        # This would require additional scraping or external APIs
        # For now, return empty affiliations
        author_affiliations = {}

        for paper in papers:
            for author in paper.get("authors", []):
                if author not in author_affiliations:
                    author_affiliations[author] = []

        logger.warning("Affiliation extraction not fully implemented (ArXiv API limitation)")
        return author_affiliations

    def extract_technical_terms(self, papers: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract edge computing specific technical terms.

        Args:
            papers: List of paper dictionaries

        Returns:
            dict: Technical terms with frequencies
        """
        # Define edge computing domain terms
        technical_terms = {
            # Infrastructure
            "edge server", "edge node", "edge device", "fog node", "cloudlet",
            "base station", "access point", "gateway",

            # Computing paradigms
            "edge computing", "fog computing", "mobile edge computing", "MEC",
            "multi-access edge computing", "cloud computing", "edge cloud",

            # Techniques
            "offloading", "task offloading", "computation offloading",
            "caching", "edge caching", "content caching",
            "orchestration", "resource allocation", "load balancing",
            "scheduling", "task scheduling",

            # AI/ML
            "edge AI", "edge intelligence", "federated learning",
            "distributed learning", "edge analytics", "inference",
            "model training", "deep learning", "neural network",

            # Networking
            "5G", "6G", "network slicing", "SDN", "NFV",
            "latency", "bandwidth", "QoS", "quality of service",

            # Applications
            "IoT", "Internet of Things", "smart city", "autonomous vehicle",
            "AR", "VR", "augmented reality", "virtual reality",
            "video streaming", "real-time", "mobile application",

            # Performance metrics
            "response time", "throughput", "energy consumption",
            "energy efficiency", "resource utilization",
        }

        term_counts = Counter()

        for paper in papers:
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

            for term in technical_terms:
                count = len(re.findall(r'\b' + re.escape(term) + r'\b', text))
                if count > 0:
                    term_counts[term] += count

        return dict(term_counts)

    def categorize_research_type(self, paper: Dict[str, Any]) -> str:
        """
        Categorize research type based on keywords and abstract.

        Args:
            paper: Paper dictionary

        Returns:
            str: Research type category
        """
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()

        # Define patterns for different research types
        categories = {
            "Machine Learning": [
                "machine learning", "deep learning", "neural network",
                "reinforcement learning", "supervised learning", "federated learning"
            ],
            "Systems": [
                "system design", "architecture", "implementation", "prototype",
                "framework", "platform"
            ],
            "Networking": [
                "network", "protocol", "routing", "5G", "6G", "SDN", "NFV",
                "communication"
            ],
            "Optimization": [
                "optimization", "algorithm", "scheduling", "resource allocation",
                "genetic algorithm", "heuristic"
            ],
            "Security": [
                "security", "privacy", "authentication", "encryption",
                "attack", "threat"
            ],
            "Theory": [
                "theoretical", "mathematical", "model", "analysis", "proof",
                "game theory"
            ],
            "Survey": [
                "survey", "review", "taxonomy", "literature", "state-of-the-art"
            ],
        }

        # Count matches for each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in text)
            category_scores[category] = score

        # Return category with highest score
        if not category_scores or max(category_scores.values()) == 0:
            return "Other"

        return max(category_scores, key=category_scores.get)

    def extract_citation_count(self, arxiv_id: str) -> int:
        """
        Extract citation count for a paper (from external sources).

        Note: This requires external API calls and may be rate-limited.

        Args:
            arxiv_id: ArXiv ID

        Returns:
            int: Estimated citation count (returns 0 as placeholder)
        """
        # This would require Semantic Scholar, Google Scholar, or similar APIs
        # For now, return 0 as placeholder
        logger.warning("Citation count extraction not implemented")
        return 0

    def enrich_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich papers with additional metadata.

        Args:
            papers: List of paper dictionaries

        Returns:
            list: Enriched paper dictionaries
        """
        logger.info(f"Enriching {len(papers)} papers with metadata")

        enriched = []
        for paper in papers:
            enriched_paper = paper.copy()

            # Extract keywords from abstract
            abstract_keywords = self.extract_keywords(
                paper.get("abstract", ""),
                max_keywords=10
            )
            enriched_paper["keywords"] = abstract_keywords

            # Categorize research type
            enriched_paper["research_type"] = self.categorize_research_type(paper)

            # Extract author count
            enriched_paper["author_count"] = len(paper.get("authors", []))

            # Extract first/last author
            authors = paper.get("authors", [])
            if authors:
                enriched_paper["first_author"] = authors[0]
                enriched_paper["last_author"] = authors[-1]

            # Extract year, month
            if "published" in paper:
                pub_date = paper["published"]
                enriched_paper["year"] = pub_date.year
                enriched_paper["month"] = pub_date.month
                enriched_paper["month_name"] = pub_date.strftime("%B")

            enriched.append(enriched_paper)

        logger.info("Metadata enrichment complete")
        return enriched

    def create_papers_dataframe(self, papers: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Create pandas DataFrame from papers.

        Args:
            papers: List of paper dictionaries

        Returns:
            pd.DataFrame: Papers dataframe
        """
        # Flatten nested structures for DataFrame
        df_data = []

        for paper in papers:
            row = {
                "arxiv_id": paper.get("arxiv_id"),
                "title": paper.get("title"),
                "abstract": paper.get("abstract"),
                "published": paper.get("published"),
                "author_count": len(paper.get("authors", [])),
                "first_author": paper.get("authors", [""])[0] if paper.get("authors") else "",
                "primary_category": paper.get("primary_category"),
                "research_type": paper.get("research_type", "Other"),
                "year": paper.get("year"),
                "month": paper.get("month"),
                "pdf_url": paper.get("pdf_url"),
            }

            # Add category flags
            categories = paper.get("categories", [])
            row["categories"] = ",".join(categories)
            row["is_cs_dc"] = "cs.DC" in categories
            row["is_cs_ni"] = "cs.NI" in categories
            row["is_cs_lg"] = "cs.LG" in categories
            row["is_cs_ai"] = "cs.AI" in categories

            df_data.append(row)

        df = pd.DataFrame(df_data)

        # Convert published to datetime
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"])

        return df

    def save_processed_data(self, papers: List[Dict[str, Any]], output_file: str):
        """
        Save processed papers to CSV.

        Args:
            papers: List of paper dictionaries
            output_file: Output file path
        """
        df = self.create_papers_dataframe(papers)
        df.to_csv(output_file, index=False)
        logger.info(f"Saved processed data to {output_file}")


def main():
    """Main function for testing metadata extraction."""
    # This would load papers from the scraper
    print("Metadata extractor module loaded successfully")


if __name__ == "__main__":
    main()
