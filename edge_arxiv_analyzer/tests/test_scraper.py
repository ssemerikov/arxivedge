"""
Tests for ArXiv scraper module.
"""

import pytest
from datetime import datetime
from src.scraper.arxiv_scraper import ArXivScraper
from src.utils.config import Config


def test_arxiv_scraper_initialization():
    """Test ArXiv scraper initialization."""
    scraper = ArXivScraper()
    assert scraper is not None
    assert scraper.config is not None


def test_build_search_query():
    """Test search query building."""
    scraper = ArXivScraper()
    query = scraper._build_search_query()
    assert query is not None
    assert len(query) > 0
    assert "edge" in query.lower() or "fog" in query.lower()


def test_result_to_dict():
    """Test conversion of ArXiv result to dictionary."""
    scraper = ArXivScraper()

    # Create mock result
    class MockResult:
        entry_id = "http://arxiv.org/abs/2501.12345"
        title = "Test Paper"
        authors = [type('obj', (object,), {'name': "John Doe"})]
        summary = "This is a test abstract."
        published = datetime(2025, 1, 15)
        updated = datetime(2025, 1, 16)
        categories = ["cs.DC"]
        primary_category = "cs.DC"
        doi = None
        pdf_url = "http://arxiv.org/pdf/2501.12345"
        links = []
        comment = None
        journal_ref = None

    result_dict = scraper._result_to_dict(MockResult())

    assert result_dict["arxiv_id"] == "2501.12345"
    assert result_dict["title"] == "Test Paper"
    assert len(result_dict["authors"]) == 1
    assert result_dict["authors"][0] == "John Doe"


def test_filter_by_year():
    """Test year filtering."""
    scraper = ArXivScraper()

    papers = [
        {"arxiv_id": "1", "published": datetime(2025, 1, 1), "year": 2025},
        {"arxiv_id": "2", "published": datetime(2024, 12, 31), "year": 2024},
        {"arxiv_id": "3", "published": datetime(2025, 6, 15), "year": 2025},
    ]

    filtered = scraper._filter_by_year(papers, 2025)

    assert len(filtered) == 2
    assert all(p["year"] == 2025 for p in filtered)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
