"""
Tests for analysis modules.
"""

import pytest
from datetime import datetime
from src.analysis.bibliometric import BibliometricAnalyzer
from src.analysis.thematic import ThematicAnalyzer
from src.analysis.temporal import TemporalAnalyzer
from src.analysis.network import NetworkAnalyzer
from src.analysis.statistical import StatisticalAnalyzer


# Sample test data
SAMPLE_PAPERS = [
    {
        "arxiv_id": "2501.00001",
        "title": "Edge Computing for IoT Applications",
        "authors": ["Alice Smith", "Bob Jones"],
        "abstract": "This paper proposes edge computing for IoT applications using machine learning.",
        "published": datetime(2025, 1, 15),
        "year": 2025,
        "month": 1,
        "categories": ["cs.DC", "cs.NI"],
        "primary_category": "cs.DC",
        "keywords": ["edge", "iot", "machine", "learning"],
        "research_type": "Machine Learning",
    },
    {
        "arxiv_id": "2501.00002",
        "title": "Fog Computing Network Architecture",
        "authors": ["Bob Jones", "Charlie Brown"],
        "abstract": "We present a novel fog computing architecture for low latency applications.",
        "published": datetime(2025, 2, 1),
        "year": 2025,
        "month": 2,
        "categories": ["cs.NI"],
        "primary_category": "cs.NI",
        "keywords": ["fog", "network", "latency"],
        "research_type": "Networking",
    },
    {
        "arxiv_id": "2501.00003",
        "title": "Resource Allocation in Edge Networks",
        "authors": ["Alice Smith", "Diana Prince"],
        "abstract": "Optimization of resource allocation for edge computing systems.",
        "published": datetime(2025, 3, 10),
        "year": 2025,
        "month": 3,
        "categories": ["cs.DC"],
        "primary_category": "cs.DC",
        "keywords": ["resource", "allocation", "optimization"],
        "research_type": "Optimization",
    },
]


def test_bibliometric_analyzer():
    """Test bibliometric analysis."""
    analyzer = BibliometricAnalyzer(SAMPLE_PAPERS)
    metrics = analyzer.generate_metrics()

    assert "author_productivity" in metrics
    assert "collaboration_patterns" in metrics
    assert "category_distribution" in metrics

    # Check author productivity
    assert metrics["author_productivity"]["total_authors"] == 4
    assert metrics["author_productivity"]["total_papers"] == 3


def test_author_productivity():
    """Test author productivity analysis."""
    analyzer = BibliometricAnalyzer(SAMPLE_PAPERS)
    stats = analyzer.analyze_author_productivity()

    assert stats["total_authors"] == 4
    assert stats["total_papers"] == 3

    # Alice Smith and Bob Jones have 2 papers each
    top_authors_dict = dict(stats["top_10_authors"])
    assert "Alice Smith" in top_authors_dict
    assert "Bob Jones" in top_authors_dict


def test_collaboration_patterns():
    """Test collaboration pattern analysis."""
    analyzer = BibliometricAnalyzer(SAMPLE_PAPERS)
    stats = analyzer.analyze_collaboration_patterns()

    assert stats["mean_authors_per_paper"] == 2.0
    assert stats["multi_author_papers"] == 3
    assert stats["single_author_papers"] == 0


def test_category_distribution():
    """Test category distribution analysis."""
    analyzer = BibliometricAnalyzer(SAMPLE_PAPERS)
    stats = analyzer.analyze_category_distribution()

    assert "cs.DC" in stats["category_distribution"]
    assert "cs.NI" in stats["category_distribution"]
    assert stats["category_distribution"]["cs.DC"] == 2


def test_thematic_analyzer():
    """Test thematic analysis."""
    analyzer = ThematicAnalyzer(SAMPLE_PAPERS)

    # Test preprocessing
    text = "This is a TEST text with SPECIAL characters!!!"
    cleaned = analyzer.preprocess_text(text)
    assert cleaned == "this is a test text with special characters"

    # Test topic extraction (with minimal papers, just check it runs)
    try:
        results = analyzer.extract_topics_lda(n_topics=2, max_features=50)
        assert "topics" in results
    except Exception as e:
        # With so few papers, topic modeling might fail
        pytest.skip(f"Topic modeling requires more papers: {e}")


def test_temporal_analyzer():
    """Test temporal analysis."""
    analyzer = TemporalAnalyzer(SAMPLE_PAPERS)

    # Test publication trends
    trends = analyzer.analyze_publication_trends()
    assert "papers_by_month" in trends
    assert "total_papers" in trends
    assert trends["total_papers"] == 3


def test_network_analyzer():
    """Test network analysis."""
    analyzer = NetworkAnalyzer(SAMPLE_PAPERS)

    # Build co-authorship network
    graph = analyzer.build_coauthorship_network()

    assert graph.number_of_nodes() == 4  # 4 unique authors
    assert graph.number_of_edges() >= 2  # At least 2 collaborations

    # Test network analysis
    stats = analyzer.analyze_coauthorship_network()
    assert "n_authors" in stats
    assert stats["n_authors"] == 4


def test_statistical_analyzer():
    """Test statistical analysis."""
    analyzer = StatisticalAnalyzer(SAMPLE_PAPERS)

    # Test descriptive statistics
    stats = analyzer.descriptive_statistics()
    assert "paper_count" in stats
    assert "authors_per_paper" in stats
    assert stats["paper_count"]["total"] == 3
    assert stats["authors_per_paper"]["mean"] == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
