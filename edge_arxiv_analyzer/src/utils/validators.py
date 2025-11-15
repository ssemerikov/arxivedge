"""
Data validation utilities for Edge ArXiv Analyzer.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import re
from loguru import logger


class PaperValidator:
    """Validate paper metadata and data quality."""

    @staticmethod
    def validate_paper_metadata(paper: Dict[str, Any]) -> bool:
        """
        Validate that paper metadata contains required fields.

        Args:
            paper: Dictionary containing paper metadata

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ["title", "authors", "abstract", "published", "arxiv_id"]

        for field in required_fields:
            if field not in paper or not paper[field]:
                logger.warning(f"Paper missing required field: {field}")
                return False

        # Validate title length
        if len(paper["title"]) < 10:
            logger.warning(f"Paper title too short: {paper.get('title', '')}")
            return False

        # Validate abstract length
        if len(paper["abstract"]) < 50:
            logger.warning(f"Paper abstract too short for: {paper.get('title', '')}")
            return False

        # Validate authors
        if not isinstance(paper["authors"], list) or len(paper["authors"]) == 0:
            logger.warning(f"Invalid authors for paper: {paper.get('title', '')}")
            return False

        return True

    @staticmethod
    def validate_arxiv_id(arxiv_id: str) -> bool:
        """
        Validate ArXiv ID format.

        Args:
            arxiv_id: ArXiv identifier

        Returns:
            bool: True if valid format
        """
        # Pattern for new arXiv IDs: YYMM.NNNNN or YYMM.NNNNNV (with version)
        pattern = r"^\d{4}\.\d{4,5}(v\d+)?$"

        if re.match(pattern, arxiv_id):
            return True

        # Pattern for old arXiv IDs: archive/YYMMNNN
        old_pattern = r"^[a-z\-]+/\d{7}$"
        return bool(re.match(old_pattern, arxiv_id))

    @staticmethod
    def validate_year(paper: Dict[str, Any], target_year: int) -> bool:
        """
        Validate that paper is from target year.

        Args:
            paper: Paper metadata dictionary
            target_year: Target year to validate against

        Returns:
            bool: True if paper is from target year
        """
        if "published" not in paper:
            return False

        try:
            if isinstance(paper["published"], str):
                pub_date = datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))
            elif isinstance(paper["published"], datetime):
                pub_date = paper["published"]
            else:
                return False

            return pub_date.year == target_year

        except (ValueError, AttributeError) as e:
            logger.warning(f"Error validating year for paper: {e}")
            return False

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Input text

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove special characters that might cause issues
        text = text.strip()

        return text

    @staticmethod
    def validate_bibtex_entry(entry: str) -> bool:
        """
        Validate BibTeX entry format.

        Args:
            entry: BibTeX entry string

        Returns:
            bool: True if valid BibTeX format
        """
        # Check for basic BibTeX structure
        if not entry.startswith("@"):
            return False

        # Check for opening and closing braces
        if entry.count("{") != entry.count("}"):
            return False

        # Check for required entry type
        entry_type_pattern = r"^@(article|inproceedings|misc|techreport|unpublished)"
        if not re.match(entry_type_pattern, entry.lower()):
            logger.warning("Invalid BibTeX entry type")
            return False

        return True


class DataQualityChecker:
    """Check data quality and completeness."""

    @staticmethod
    def check_completeness(papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check data completeness across all papers.

        Args:
            papers: List of paper dictionaries

        Returns:
            dict: Statistics about data completeness
        """
        if not papers:
            return {"total_papers": 0, "completeness": 0.0}

        total = len(papers)
        stats = {
            "total_papers": total,
            "with_title": 0,
            "with_authors": 0,
            "with_abstract": 0,
            "with_categories": 0,
            "with_doi": 0,
            "with_pdf_url": 0,
            "completeness_score": 0.0,
        }

        for paper in papers:
            if paper.get("title"):
                stats["with_title"] += 1
            if paper.get("authors"):
                stats["with_authors"] += 1
            if paper.get("abstract"):
                stats["with_abstract"] += 1
            if paper.get("categories"):
                stats["with_categories"] += 1
            if paper.get("doi"):
                stats["with_doi"] += 1
            if paper.get("pdf_url"):
                stats["with_pdf_url"] += 1

        # Calculate completeness score (0-1)
        required_fields = ["with_title", "with_authors", "with_abstract"]
        completeness = sum(stats[field] for field in required_fields) / (len(required_fields) * total)
        stats["completeness_score"] = round(completeness, 3)

        # Add percentages
        for key in list(stats.keys()):
            if key.startswith("with_"):
                stats[f"{key}_pct"] = round((stats[key] / total) * 100, 1)

        return stats

    @staticmethod
    def identify_duplicates(papers: List[Dict[str, Any]]) -> List[str]:
        """
        Identify duplicate papers by ArXiv ID.

        Args:
            papers: List of paper dictionaries

        Returns:
            list: List of duplicate ArXiv IDs
        """
        seen = set()
        duplicates = []

        for paper in papers:
            arxiv_id = paper.get("arxiv_id", "")
            # Remove version suffix for comparison
            base_id = re.sub(r"v\d+$", "", arxiv_id)

            if base_id in seen:
                duplicates.append(arxiv_id)
            else:
                seen.add(base_id)

        return duplicates

    @staticmethod
    def check_data_types(papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Check for data type inconsistencies.

        Args:
            papers: List of paper dictionaries

        Returns:
            dict: Issues found by field
        """
        issues = {
            "title": [],
            "authors": [],
            "abstract": [],
            "published": [],
            "categories": [],
        }

        for idx, paper in enumerate(papers):
            # Check title
            if "title" in paper and not isinstance(paper["title"], str):
                issues["title"].append(f"Paper {idx}: title is not string")

            # Check authors
            if "authors" in paper and not isinstance(paper["authors"], list):
                issues["authors"].append(f"Paper {idx}: authors is not list")

            # Check abstract
            if "abstract" in paper and not isinstance(paper["abstract"], str):
                issues["abstract"].append(f"Paper {idx}: abstract is not string")

            # Check published date
            if "published" in paper:
                if not isinstance(paper["published"], (str, datetime)):
                    issues["published"].append(f"Paper {idx}: invalid date type")

            # Check categories
            if "categories" in paper and not isinstance(paper["categories"], list):
                issues["categories"].append(f"Paper {idx}: categories is not list")

        return {k: v for k, v in issues.items() if v}


def validate_pipeline_output(output_dir: str) -> Dict[str, bool]:
    """
    Validate that pipeline has generated all expected outputs.

    Args:
        output_dir: Path to output directory

    Returns:
        dict: Validation results for each output type
    """
    from pathlib import Path

    output_path = Path(output_dir)

    validations = {
        "data_files": (output_path / "data").exists() and len(list((output_path / "data").glob("*.json"))) > 0,
        "figures": (output_path / "figures").exists() and len(list((output_path / "figures").glob("*.pdf"))) > 0,
        "tables": (output_path / "tables").exists() and len(list((output_path / "tables").glob("*.tex"))) > 0,
        "bibtex": (output_path / "bibtex").exists() and len(list((output_path / "bibtex").glob("*.bib"))) > 0,
        "paper": (output_path / "paper").exists() and (output_path / "paper" / "edge_of_arxiv_2025.tex").exists(),
    }

    return validations
