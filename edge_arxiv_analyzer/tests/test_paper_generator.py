"""
Tests for paper generation modules.
"""

import pytest
from datetime import datetime
from src.paper_generator.bibtex_manager import BibTeXManager
from src.paper_generator.latex_writer import LaTeXWriter


SAMPLE_PAPER = {
    "arxiv_id": "2501.12345",
    "title": "Edge Computing for Real-Time Applications",
    "authors": ["John Doe", "Jane Smith"],
    "abstract": "This paper presents a novel approach to edge computing.",
    "published": datetime(2025, 1, 15),
    "year": 2025,
    "month": 1,
    "categories": ["cs.DC", "cs.NI"],
    "primary_category": "cs.DC",
}


def test_bibtex_manager_initialization():
    """Test BibTeX manager initialization."""
    manager = BibTeXManager()
    assert manager is not None


def test_generate_citation_key():
    """Test citation key generation."""
    manager = BibTeXManager()
    key = manager._generate_citation_key(SAMPLE_PAPER)

    assert key is not None
    assert "Doe" in key or "doe" in key.lower()
    assert "2025" in key


def test_generate_bibtex_entry():
    """Test BibTeX entry generation."""
    manager = BibTeXManager()
    entry = manager.generate_bibtex_entry(SAMPLE_PAPER)

    assert entry is not None
    assert "@misc{" in entry
    assert "title" in entry
    assert "author" in entry
    assert "Edge Computing" in entry
    assert "John Doe and Jane Smith" in entry


def test_bibtex_validation():
    """Test BibTeX entry validation."""
    manager = BibTeXManager()
    entry = manager.generate_bibtex_entry(SAMPLE_PAPER)

    # Check basic structure
    assert entry.startswith("@misc{")
    assert entry.count("{") == entry.count("}")


def test_generate_bibtex_from_papers():
    """Test generating BibTeX for multiple papers."""
    manager = BibTeXManager()
    papers = [SAMPLE_PAPER, SAMPLE_PAPER.copy()]

    bibtex_content = manager.generate_bibtex_from_papers(papers)

    assert bibtex_content is not None
    assert len(bibtex_content) > 0
    assert bibtex_content.count("@misc{") == 2


def test_latex_writer_initialization():
    """Test LaTeX writer initialization."""
    writer = LaTeXWriter()
    assert writer is not None


def test_latex_escape():
    """Test LaTeX character escaping."""
    writer = LaTeXWriter()

    text = "Test & symbols: $, %, #, _, {, }"
    escaped = writer._escape_latex(text)

    assert r"\&" in escaped
    assert r"\$" in escaped
    assert r"\%" in escaped


def test_generate_preamble():
    """Test LaTeX preamble generation."""
    writer = LaTeXWriter()
    preamble = writer.generate_preamble()

    assert r"\documentclass" in preamble
    assert r"\usepackage" in preamble
    assert "Edge of ArXiv" in preamble


def test_generate_abstract():
    """Test abstract generation."""
    writer = LaTeXWriter()

    analysis_results = {
        "bibliometric": {
            "summary": {
                "total_papers": 100,
                "total_authors": 250,
            }
        }
    }

    abstract = writer.generate_abstract(analysis_results)

    assert r"\begin{abstract}" in abstract
    assert r"\end{abstract}" in abstract
    assert "100" in abstract
    assert "250" in abstract


def test_generate_introduction():
    """Test introduction generation."""
    writer = LaTeXWriter()

    analysis_results = {
        "bibliometric": {
            "summary": {
                "total_papers": 100,
            }
        }
    }

    intro = writer.generate_introduction(analysis_results)

    assert r"\section{Introduction}" in intro
    assert "edge computing" in intro.lower()
    assert "100" in intro


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
