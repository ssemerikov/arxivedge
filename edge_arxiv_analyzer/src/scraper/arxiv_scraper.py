"""
ArXiv scraper module for retrieving edge computing papers.
"""

import arxiv
import time
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from tqdm import tqdm
from loguru import logger
import pickle

from ..utils.config import Config, get_data_path
from ..utils.validators import PaperValidator


class ArXivScraper:
    """Scraper for ArXiv papers on edge computing."""

    def __init__(self, config: Config = None):
        """
        Initialize ArXiv scraper.

        Args:
            config: Configuration object (uses default if None)
        """
        self.config = config or Config()
        self.validator = PaperValidator()
        self.papers = []
        self.cache_file = get_data_path("arxiv_cache.pkl")

    def search_edge_papers_2025(self) -> List[Dict[str, Any]]:
        """
        Search ArXiv for edge computing papers from 2025.

        Returns:
            list: List of paper metadata dictionaries
        """
        logger.info("Starting ArXiv search for edge computing papers in 2025")

        # Check cache first
        if self.config.USE_CACHE and self._load_from_cache():
            logger.info(f"Loaded {len(self.papers)} papers from cache")
            return self.papers

        # Build search query
        query = self._build_search_query()
        logger.info(f"Search query: {query}")

        # Search ArXiv
        self.papers = self._execute_search(query)

        # Filter by year
        self.papers = self._filter_by_year(self.papers, self.config.YEAR_START)

        # Validate papers
        self.papers = self._validate_papers(self.papers)

        # Save to cache
        self._save_to_cache()

        # Save raw data
        self._save_raw_data()

        logger.info(f"Total papers retrieved: {len(self.papers)}")
        return self.papers

    def _build_search_query(self) -> str:
        """
        Build ArXiv search query from configuration.

        Returns:
            str: Search query string
        """
        # Create OR query for keywords
        keyword_queries = []
        for keyword in self.config.ARXIV_SEARCH_KEYWORDS:
            # Search in title, abstract
            keyword_queries.append(f'ti:"{keyword}" OR abs:"{keyword}"')

        query = " OR ".join(keyword_queries)
        return query

    def _execute_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute ArXiv API search.

        Args:
            query: Search query string

        Returns:
            list: List of paper metadata dictionaries
        """
        papers = []

        try:
            # Create search object
            search = arxiv.Search(
                query=query,
                max_results=self.config.ARXIV_MAX_RESULTS,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            # Execute search with progress bar
            client = arxiv.Client()
            results = list(tqdm(
                client.results(search),
                desc="Fetching papers from ArXiv",
                unit="papers"
            ))

            logger.info(f"Retrieved {len(results)} papers from ArXiv API")

            # Convert to dictionaries
            for result in tqdm(results, desc="Processing paper metadata"):
                paper_dict = self._result_to_dict(result)
                papers.append(paper_dict)

                # Rate limiting (config value is already in seconds)
                time.sleep(self.config.ARXIV_API_DELAY)

        except Exception as e:
            logger.error(f"Error searching ArXiv: {e}")
            raise

        return papers

    def _result_to_dict(self, result: arxiv.Result) -> Dict[str, Any]:
        """
        Convert ArXiv result object to dictionary.

        Args:
            result: ArXiv result object

        Returns:
            dict: Paper metadata dictionary
        """
        return {
            "arxiv_id": result.entry_id.split("/")[-1],
            "title": self.validator.clean_text(result.title),
            "authors": [author.name for author in result.authors],
            "abstract": self.validator.clean_text(result.summary),
            "published": result.published,
            "updated": result.updated,
            "categories": result.categories,
            "primary_category": result.primary_category,
            "doi": result.doi,
            "pdf_url": result.pdf_url,
            "links": [link.href for link in result.links],
            "comment": result.comment,
            "journal_ref": result.journal_ref,
        }

    def _filter_by_year(self, papers: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
        """
        Filter papers by publication year.

        Args:
            papers: List of paper dictionaries
            year: Target year

        Returns:
            list: Filtered papers
        """
        filtered = []

        for paper in papers:
            if self.validator.validate_year(paper, year):
                filtered.append(paper)

        logger.info(f"Filtered to {len(filtered)} papers from year {year}")
        return filtered

    def _validate_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate paper metadata.

        Args:
            papers: List of paper dictionaries

        Returns:
            list: Validated papers
        """
        validated = []

        for paper in papers:
            if self.validator.validate_paper_metadata(paper):
                validated.append(paper)
            else:
                logger.warning(f"Invalid paper metadata: {paper.get('title', 'Unknown')}")

        logger.info(f"Validated {len(validated)} papers")
        return validated

    def _load_from_cache(self) -> bool:
        """
        Load papers from cache file.

        Returns:
            bool: True if successfully loaded from cache
        """
        if not self.cache_file.exists():
            return False

        try:
            # Check cache age
            cache_age_days = (datetime.now() - datetime.fromtimestamp(
                self.cache_file.stat().st_mtime
            )).days

            if cache_age_days > self.config.CACHE_EXPIRY_DAYS:
                logger.info("Cache expired")
                return False

            # Load cache
            with open(self.cache_file, 'rb') as f:
                self.papers = pickle.load(f)

            return True

        except Exception as e:
            logger.warning(f"Error loading cache: {e}")
            return False

    def _save_to_cache(self):
        """Save papers to cache file."""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.papers, f)

            logger.info(f"Saved {len(self.papers)} papers to cache")

        except Exception as e:
            logger.warning(f"Error saving cache: {e}")

    def _save_raw_data(self):
        """Save raw paper data to JSON file."""
        output_file = get_data_path("raw_arxiv_data.json")

        try:
            # Convert datetime objects to strings for JSON serialization
            papers_json = []
            for paper in self.papers:
                paper_copy = paper.copy()
                if isinstance(paper_copy.get("published"), datetime):
                    paper_copy["published"] = paper_copy["published"].isoformat()
                if isinstance(paper_copy.get("updated"), datetime):
                    paper_copy["updated"] = paper_copy["updated"].isoformat()
                papers_json.append(paper_copy)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(papers_json, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved raw data to {output_file}")

        except Exception as e:
            logger.error(f"Error saving raw data: {e}")
            raise

    def export_to_bibtex(self, output_file: Path = None) -> str:
        """
        Generate BibTeX entries for all papers.

        Args:
            output_file: Path to output BibTeX file (optional)

        Returns:
            str: BibTeX content
        """
        from ..paper_generator.bibtex_manager import BibTeXManager

        bibtex_manager = BibTeXManager()
        bibtex_content = bibtex_manager.generate_bibtex_from_papers(self.papers)

        if output_file:
            bibtex_manager.save_bibtex(bibtex_content, output_file)

        return bibtex_content

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics about retrieved papers.

        Returns:
            dict: Statistics dictionary
        """
        if not self.papers:
            return {}

        stats = {
            "total_papers": len(self.papers),
            "date_range": {
                "earliest": min(p["published"] for p in self.papers).isoformat() if self.papers else None,
                "latest": max(p["published"] for p in self.papers).isoformat() if self.papers else None,
            },
            "total_authors": len(set(
                author for paper in self.papers for author in paper.get("authors", [])
            )),
            "categories": {},
            "papers_by_month": {},
        }

        # Count categories
        for paper in self.papers:
            for category in paper.get("categories", []):
                stats["categories"][category] = stats["categories"].get(category, 0) + 1

        # Count papers by month
        for paper in self.papers:
            month_key = paper["published"].strftime("%Y-%m")
            stats["papers_by_month"][month_key] = stats["papers_by_month"].get(month_key, 0) + 1

        return stats


def main():
    """Main function for testing scraper."""
    scraper = ArXivScraper()
    papers = scraper.search_edge_papers_2025()

    print(f"\nRetrieved {len(papers)} papers")
    print("\nStatistics:")
    stats = scraper.get_statistics()
    print(json.dumps(stats, indent=2, default=str))


if __name__ == "__main__":
    main()
