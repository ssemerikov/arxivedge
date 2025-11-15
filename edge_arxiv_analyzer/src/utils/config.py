"""
Configuration settings for Edge ArXiv Analyzer.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import yaml

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
DATA_DIR = OUTPUT_DIR / "data"
FIGURES_DIR = OUTPUT_DIR / "figures"
TABLES_DIR = OUTPUT_DIR / "tables"
BIBTEX_DIR = OUTPUT_DIR / "bibtex"
PAPER_DIR = OUTPUT_DIR / "paper"

# Ensure all directories exist
for directory in [OUTPUT_DIR, DATA_DIR, FIGURES_DIR, TABLES_DIR, BIBTEX_DIR, PAPER_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


class Config:
    """Configuration class for ArXiv Edge Computing analyzer."""

    # ArXiv search parameters
    ARXIV_SEARCH_KEYWORDS = [
        "edge computing",
        "mobile edge computing",
        "multi-access edge computing",
        "MEC",
        "fog computing",
        "edge AI",
        "edge intelligence",
        "edge analytics",
        "edge machine learning",
        "edge deep learning",
        "cloudlet",
        "edge cloud",
        "edge orchestration",
        "edge offloading",
        "edge caching",
    ]

    # Year filter for 2025
    YEAR_START = 2025
    YEAR_END = 2025

    # ArXiv categories to search
    ARXIV_CATEGORIES = [
        "cs.DC",  # Distributed, Parallel, and Cluster Computing
        "cs.NI",  # Networking and Internet Architecture
        "cs.AI",  # Artificial Intelligence
        "cs.LG",  # Machine Learning
        "cs.CV",  # Computer Vision
        "cs.SY",  # Systems and Control
        "cs.AR",  # Hardware Architecture
        "cs.PF",  # Performance
    ]

    # API settings
    ARXIV_API_DELAY = 3.0  # Seconds between API calls (respect rate limits)
    ARXIV_MAX_RESULTS = 2000  # Maximum results per query
    ARXIV_RESULTS_PER_PAGE = 100

    # Cache settings
    USE_CACHE = True
    CACHE_EXPIRY_DAYS = 1

    # Analysis settings
    MIN_KEYWORDS = 5
    MAX_KEYWORDS = 50
    N_TOPICS_LDA = 10
    N_TOPICS_BERT = 8

    # Visualization settings
    FIGURE_DPI = 300
    FIGURE_FORMAT = "pdf"  # primary format
    FIGURE_FORMATS = ["pdf", "png"]  # export both
    FIGURE_STYLE = "seaborn-v0_8-paper"
    COLOR_PALETTE = "Set2"
    FONT_SIZE = 10

    # Network analysis settings
    MIN_COLLABORATIONS = 2
    NETWORK_LAYOUT = "spring"

    # Paper generation settings
    PAPER_TITLE = "Edge of ArXiv: Cutting-Edge Computing Research Trends in 2025"
    PAPER_AUTHORS = ["ArXiv Analysis System"]
    PAPER_ABSTRACT_MAX_LENGTH = 250
    JOURNAL_NAME = "Journal of Edge Computing"

    # Statistical settings
    SIGNIFICANCE_LEVEL = 0.05
    CONFIDENCE_INTERVAL = 0.95

    # Logging settings
    LOG_LEVEL = "INFO"
    LOG_FILE = OUTPUT_DIR / "arxiv_analyzer.log"

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith("_") and not callable(value)
        }

    @classmethod
    def save_config(cls, filepath: Path = None):
        """Save configuration to YAML file."""
        if filepath is None:
            filepath = OUTPUT_DIR / "config.yaml"

        config_dict = cls.to_dict()
        # Convert Path objects to strings for YAML serialization
        config_dict = {
            k: str(v) if isinstance(v, Path) else v
            for k, v in config_dict.items()
        }

        with open(filepath, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def get_search_query(cls) -> str:
        """
        Generate ArXiv search query string.

        Returns:
            str: Formatted search query for ArXiv API
        """
        # Build query with OR conditions for keywords
        keyword_query = " OR ".join([f'"{kw}"' for kw in cls.ARXIV_SEARCH_KEYWORDS])

        # Add category filters
        category_query = " OR ".join([f"cat:{cat}" for cat in cls.ARXIV_CATEGORIES])

        # Combine queries
        full_query = f"({keyword_query}) AND ({category_query})"

        return full_query


# Global configuration instance
config = Config()


# File path helpers
def get_data_path(filename: str) -> Path:
    """Get path for data file."""
    return DATA_DIR / filename


def get_figure_path(filename: str, format: str = None) -> Path:
    """Get path for figure file."""
    if format is None:
        format = Config.FIGURE_FORMAT

    if not filename.endswith(f".{format}"):
        filename = f"{filename}.{format}"

    return FIGURES_DIR / filename


def get_table_path(filename: str) -> Path:
    """Get path for table file."""
    if not filename.endswith(".tex"):
        filename = f"{filename}.tex"

    return TABLES_DIR / filename


def get_bibtex_path(filename: str) -> Path:
    """Get path for BibTeX file."""
    if not filename.endswith(".bib"):
        filename = f"{filename}.bib"

    return BIBTEX_DIR / filename


def get_paper_path(filename: str) -> Path:
    """Get path for paper file."""
    return PAPER_DIR / filename
