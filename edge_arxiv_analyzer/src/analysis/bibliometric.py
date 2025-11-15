"""
Bibliometric analysis module for ArXiv papers.
"""

from typing import List, Dict, Any, Tuple
from collections import Counter, defaultdict
import pandas as pd
import numpy as np
from loguru import logger


class BibliometricAnalyzer:
    """Perform bibliometric analysis on ArXiv papers."""

    def __init__(self, papers: List[Dict[str, Any]]):
        """
        Initialize bibliometric analyzer.

        Args:
            papers: List of paper dictionaries
        """
        self.papers = papers
        self.df = None
        self._prepare_dataframe()

    def _prepare_dataframe(self):
        """Prepare pandas DataFrame from papers."""
        from ..scraper.metadata_extractor import MetadataExtractor

        extractor = MetadataExtractor()
        self.df = extractor.create_papers_dataframe(self.papers)

    def analyze_author_productivity(self) -> Dict[str, Any]:
        """
        Analyze author productivity metrics.

        Returns:
            dict: Author productivity statistics
        """
        logger.info("Analyzing author productivity")

        # Count papers per author
        author_papers = defaultdict(list)
        for paper in self.papers:
            for author in paper.get("authors", []):
                author_papers[author].append(paper["arxiv_id"])

        # Calculate statistics
        papers_per_author = {author: len(papers) for author, papers in author_papers.items()}

        # Sort by productivity
        top_authors = sorted(papers_per_author.items(), key=lambda x: x[1], reverse=True)

        # Calculate h-index estimation (simplified for new 2025 papers)
        # Note: True h-index requires citation counts from external sources
        # For 2025 papers with minimal citations, we use paper count as proxy
        h_index = {}
        for author, paper_list in author_papers.items():
            # Simplified h-index: for papers with no citation data,
            # h-index approximates to sqrt(paper_count) or paper_count
            # depending on career stage. For new papers, we use paper count.
            num_papers = len(paper_list)
            # Conservative estimate: h-index is bounded by number of papers
            # For new papers without citations, assume h = num_papers
            # (This would be refined with actual citation data)
            h = num_papers
            h_index[author] = h

        stats = {
            "total_authors": len(author_papers),
            "total_papers": len(self.papers),
            "papers_per_author_mean": np.mean(list(papers_per_author.values())),
            "papers_per_author_median": np.median(list(papers_per_author.values())),
            "papers_per_author_max": max(papers_per_author.values()),
            "top_10_authors": top_authors[:10],
            "top_20_authors": top_authors[:20],
            "single_paper_authors": sum(1 for count in papers_per_author.values() if count == 1),
            "multi_paper_authors": sum(1 for count in papers_per_author.values() if count > 1),
        }

        logger.info(f"Found {stats['total_authors']} unique authors")
        return stats

    def analyze_collaboration_patterns(self) -> Dict[str, Any]:
        """
        Analyze collaboration patterns.

        Returns:
            dict: Collaboration statistics
        """
        logger.info("Analyzing collaboration patterns")

        author_counts = [len(paper.get("authors", [])) for paper in self.papers]

        # Co-authorship pairs
        coauthor_pairs = Counter()
        for paper in self.papers:
            authors = paper.get("authors", [])
            if len(authors) > 1:
                for i, author1 in enumerate(authors):
                    for author2 in authors[i + 1:]:
                        pair = tuple(sorted([author1, author2]))
                        coauthor_pairs[pair] += 1

        stats = {
            "mean_authors_per_paper": np.mean(author_counts),
            "median_authors_per_paper": np.median(author_counts),
            "max_authors_per_paper": max(author_counts) if author_counts else 0,
            "min_authors_per_paper": min(author_counts) if author_counts else 0,
            "single_author_papers": sum(1 for c in author_counts if c == 1),
            "multi_author_papers": sum(1 for c in author_counts if c > 1),
            "collaboration_index": np.mean([c for c in author_counts if c > 1]) if any(c > 1 for c in author_counts) else 0,
            "total_coauthor_pairs": len(coauthor_pairs),
            "top_collaborations": coauthor_pairs.most_common(10),
        }

        logger.info(f"Mean authors per paper: {stats['mean_authors_per_paper']:.2f}")
        return stats

    def analyze_category_distribution(self) -> Dict[str, Any]:
        """
        Analyze ArXiv category distribution.

        Returns:
            dict: Category statistics
        """
        logger.info("Analyzing category distribution")

        # Count categories
        category_counts = Counter()
        primary_category_counts = Counter()

        for paper in self.papers:
            # All categories
            for cat in paper.get("categories", []):
                category_counts[cat] += 1

            # Primary category
            primary = paper.get("primary_category")
            if primary:
                primary_category_counts[primary] += 1

        # Cross-category analysis
        cross_category_papers = sum(
            1 for paper in self.papers
            if len(paper.get("categories", [])) > 1
        )

        stats = {
            "total_categories": len(category_counts),
            "category_distribution": dict(category_counts.most_common()),
            "primary_category_distribution": dict(primary_category_counts.most_common()),
            "top_5_categories": category_counts.most_common(5),
            "top_10_categories": category_counts.most_common(10),
            "cross_category_papers": cross_category_papers,
            "cross_category_ratio": cross_category_papers / len(self.papers) if self.papers else 0,
        }

        logger.info(f"Found {stats['total_categories']} unique categories")
        return stats

    def analyze_keywords(self) -> Dict[str, Any]:
        """
        Analyze keyword frequency and co-occurrence.

        Returns:
            dict: Keyword statistics
        """
        logger.info("Analyzing keywords")

        # Extract keywords from enriched papers
        all_keywords = []
        keyword_pairs = Counter()

        for paper in self.papers:
            keywords = paper.get("keywords", [])
            all_keywords.extend(keywords)

            # Keyword co-occurrence
            if len(keywords) > 1:
                for i, kw1 in enumerate(keywords):
                    for kw2 in keywords[i + 1:]:
                        pair = tuple(sorted([kw1, kw2]))
                        keyword_pairs[pair] += 1

        keyword_counts = Counter(all_keywords)

        stats = {
            "total_keywords": len(keyword_counts),
            "top_20_keywords": keyword_counts.most_common(20),
            "top_50_keywords": keyword_counts.most_common(50),
            "keyword_frequency": dict(keyword_counts),
            "top_keyword_pairs": keyword_pairs.most_common(20),
        }

        logger.info(f"Found {stats['total_keywords']} unique keywords")
        return stats

    def analyze_research_types(self) -> Dict[str, Any]:
        """
        Analyze distribution of research types.

        Returns:
            dict: Research type statistics
        """
        logger.info("Analyzing research types")

        research_types = Counter()
        for paper in self.papers:
            rtype = paper.get("research_type", "Other")
            research_types[rtype] += 1

        total = sum(research_types.values())

        stats = {
            "research_type_counts": dict(research_types),
            "research_type_percentages": {
                rtype: (count / total) * 100
                for rtype, count in research_types.items()
            },
            "most_common_type": research_types.most_common(1)[0] if research_types else ("None", 0),
        }

        logger.info(f"Research type distribution: {dict(research_types)}")
        return stats

    def calculate_prolific_authors(self, min_papers: int = 3) -> pd.DataFrame:
        """
        Identify prolific authors.

        Args:
            min_papers: Minimum number of papers to be considered prolific

        Returns:
            pd.DataFrame: Prolific authors with statistics
        """
        author_papers = defaultdict(list)
        for paper in self.papers:
            for author in paper.get("authors", []):
                author_papers[author].append(paper)

        # Filter by minimum papers
        prolific = {
            author: papers
            for author, papers in author_papers.items()
            if len(papers) >= min_papers
        }

        # Create DataFrame
        data = []
        for author, papers in prolific.items():
            # Get categories for this author's papers
            categories = []
            for paper in papers:
                categories.extend(paper.get("categories", []))

            data.append({
                "author": author,
                "paper_count": len(papers),
                "primary_categories": Counter([p.get("primary_category") for p in papers]).most_common(3),
                "research_types": Counter([p.get("research_type", "Other") for p in papers]).most_common(3),
                "first_paper_date": min(p.get("published") for p in papers),
                "latest_paper_date": max(p.get("published") for p in papers),
            })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values("paper_count", ascending=False)

        return df

    def generate_metrics(self) -> Dict[str, Any]:
        """
        Generate comprehensive bibliometric metrics.

        Returns:
            dict: Complete bibliometric analysis
        """
        logger.info("Generating comprehensive bibliometric metrics")

        metrics = {
            "author_productivity": self.analyze_author_productivity(),
            "collaboration_patterns": self.analyze_collaboration_patterns(),
            "category_distribution": self.analyze_category_distribution(),
            "keywords": self.analyze_keywords(),
            "research_types": self.analyze_research_types(),
        }

        # Add summary statistics
        metrics["summary"] = {
            "total_papers": len(self.papers),
            "total_authors": metrics["author_productivity"]["total_authors"],
            "average_authors_per_paper": metrics["collaboration_patterns"]["mean_authors_per_paper"],
            "total_categories": metrics["category_distribution"]["total_categories"],
            "total_keywords": metrics["keywords"]["total_keywords"],
        }

        logger.info("Bibliometric analysis complete")
        return metrics

    def export_author_statistics(self, output_file: str):
        """
        Export author statistics to CSV.

        Args:
            output_file: Output CSV file path
        """
        author_stats = self.analyze_author_productivity()

        # Create DataFrame
        data = [
            {"author": author, "paper_count": count}
            for author, count in author_stats["top_20_authors"]
        ]

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False)
        logger.info(f"Exported author statistics to {output_file}")


def main():
    """Main function for testing bibliometric analysis."""
    print("Bibliometric analyzer module loaded successfully")


if __name__ == "__main__":
    main()
