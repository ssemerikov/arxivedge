#!/usr/bin/env python3
"""
Demo script showing the Edge ArXiv Analyzer with sample data.

This script demonstrates all components without requiring actual ArXiv scraping.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config
from src.scraper.metadata_extractor import MetadataExtractor
from src.analysis.bibliometric import BibliometricAnalyzer
from src.analysis.thematic import ThematicAnalyzer
from src.analysis.temporal import TemporalAnalyzer
from src.analysis.network import NetworkAnalyzer
from src.analysis.statistical import StatisticalAnalyzer
from src.visualization.tables import TableGenerator
from src.paper_generator.bibtex_manager import BibTeXManager


# Sample data
SAMPLE_PAPERS = [
    {
        "arxiv_id": "2501.00001",
        "title": "Edge Computing for IoT: A Comprehensive Survey",
        "authors": ["Alice Smith", "Bob Johnson", "Carol Williams"],
        "abstract": "This paper presents a comprehensive survey of edge computing techniques for Internet of Things (IoT) applications. We review recent advances in edge intelligence, resource allocation, and distributed machine learning at the edge. Our analysis reveals key trends in federated learning, edge caching, and 5G integration.",
        "published": datetime(2025, 1, 15),
        "year": 2025,
        "month": 1,
        "categories": ["cs.DC", "cs.NI"],
        "primary_category": "cs.DC",
        "keywords": ["edge", "iot", "survey", "federated", "learning"],
        "research_type": "Survey",
    },
    {
        "arxiv_id": "2501.00002",
        "title": "Deep Learning at the Edge: Resource Optimization Strategies",
        "authors": ["Bob Johnson", "David Brown"],
        "abstract": "We propose novel optimization strategies for deploying deep learning models on edge devices. Our approach combines model compression, dynamic scheduling, and adaptive offloading to minimize latency while maintaining accuracy. Experimental results show 40% reduction in inference time.",
        "published": datetime(2025, 2, 3),
        "year": 2025,
        "month": 2,
        "categories": ["cs.LG", "cs.DC"],
        "primary_category": "cs.LG",
        "keywords": ["deep", "learning", "optimization", "edge", "inference"],
        "research_type": "Machine Learning",
    },
    {
        "arxiv_id": "2501.00003",
        "title": "Secure Edge Computing: Privacy-Preserving Protocols",
        "authors": ["Eva Martinez", "Frank Chen"],
        "abstract": "Security and privacy are critical concerns in edge computing environments. This paper introduces privacy-preserving protocols for edge-based data processing, leveraging homomorphic encryption and secure multi-party computation. We demonstrate the feasibility of secure edge analytics with minimal overhead.",
        "published": datetime(2025, 2, 18),
        "year": 2025,
        "month": 2,
        "categories": ["cs.CR", "cs.DC"],
        "primary_category": "cs.CR",
        "keywords": ["security", "privacy", "encryption", "edge", "protocol"],
        "research_type": "Security",
    },
    {
        "arxiv_id": "2501.00004",
        "title": "5G-Enabled Mobile Edge Computing: Architecture and Applications",
        "authors": ["Alice Smith", "George Lee"],
        "abstract": "The integration of 5G networks with mobile edge computing (MEC) enables ultra-low latency applications. We present a novel architecture for 5G-MEC systems and demonstrate its effectiveness for autonomous vehicles, AR/VR, and smart city applications. Our framework achieves sub-10ms latency.",
        "published": datetime(2025, 3, 5),
        "year": 2025,
        "month": 3,
        "categories": ["cs.NI", "cs.DC"],
        "primary_category": "cs.NI",
        "keywords": ["5g", "mec", "latency", "autonomous", "vehicle"],
        "research_type": "Networking",
    },
    {
        "arxiv_id": "2501.00005",
        "title": "Federated Learning for Edge Intelligence",
        "authors": ["Bob Johnson", "Helen Kim", "Ian Rodriguez"],
        "abstract": "Federated learning enables privacy-preserving machine learning at the edge. This work proposes an advanced federated learning framework optimized for heterogeneous edge devices. We address challenges in non-IID data distribution, communication efficiency, and model aggregation.",
        "published": datetime(2025, 3, 20),
        "year": 2025,
        "month": 3,
        "categories": ["cs.LG", "cs.DC"],
        "primary_category": "cs.LG",
        "keywords": ["federated", "learning", "privacy", "edge", "distributed"],
        "research_type": "Machine Learning",
    },
    {
        "arxiv_id": "2501.00006",
        "title": "Energy-Efficient Edge Computing for Sustainable IoT",
        "authors": ["Julia Patel", "Kevin Wong"],
        "abstract": "Energy consumption is a major concern in edge computing deployments. We propose energy-efficient scheduling algorithms and green edge computing strategies that reduce power consumption by 35% while maintaining quality of service. Our approach considers renewable energy integration.",
        "published": datetime(2025, 4, 10),
        "year": 2025,
        "month": 4,
        "categories": ["cs.DC", "cs.SY"],
        "primary_category": "cs.DC",
        "keywords": ["energy", "efficiency", "green", "sustainable", "iot"],
        "research_type": "Optimization",
    },
    {
        "arxiv_id": "2501.00007",
        "title": "Edge Caching for Content Delivery Networks",
        "authors": ["Alice Smith", "Laura Anderson"],
        "abstract": "Edge caching significantly improves content delivery performance. This paper presents adaptive caching strategies for edge CDNs, using machine learning to predict content popularity. Our system achieves 60% cache hit rate and reduces backbone network traffic.",
        "published": datetime(2025, 4, 25),
        "year": 2025,
        "month": 4,
        "categories": ["cs.NI", "cs.DC"],
        "primary_category": "cs.NI",
        "keywords": ["caching", "cdn", "content", "delivery", "prediction"],
        "research_type": "Systems",
    },
    {
        "arxiv_id": "2501.00008",
        "title": "Blockchain-Based Edge Computing for Decentralized IoT",
        "authors": ["Michael Zhang", "Nancy Taylor"],
        "abstract": "We integrate blockchain technology with edge computing to create decentralized IoT systems. Our approach ensures data integrity, transparency, and trust in edge-based services. The proposed framework supports smart contracts for automated edge resource management.",
        "published": datetime(2025, 5, 8),
        "year": 2025,
        "month": 5,
        "categories": ["cs.DC", "cs.CR"],
        "primary_category": "cs.DC",
        "keywords": ["blockchain", "decentralized", "iot", "smart", "contract"],
        "research_type": "Systems",
    },
]


def main():
    """Run demo."""
    print("="*80)
    print("Edge ArXiv Analyzer - Demo Mode")
    print("="*80)
    print(f"\nUsing {len(SAMPLE_PAPERS)} sample papers for demonstration\n")

    # Enrich metadata
    print("[1/6] Enriching metadata...")
    extractor = MetadataExtractor()
    enriched_papers = extractor.enrich_papers(SAMPLE_PAPERS)
    print(f"✓ Enriched {len(enriched_papers)} papers")

    # Bibliometric analysis
    print("\n[2/6] Running bibliometric analysis...")
    bibliometric = BibliometricAnalyzer(enriched_papers)
    bib_results = bibliometric.generate_metrics()
    print(f"✓ Found {bib_results['summary']['total_authors']} unique authors")
    print(f"✓ Identified {bib_results['summary']['total_categories']} categories")

    # Thematic analysis
    print("\n[3/6] Running thematic analysis...")
    thematic = ThematicAnalyzer(enriched_papers)
    theme_results = thematic.analyze_research_themes()
    print(f"✓ Analyzed {len(theme_results['theme_distribution'])} research themes")

    # Temporal analysis
    print("\n[4/6] Running temporal analysis...")
    temporal = TemporalAnalyzer(enriched_papers)
    temp_results = temporal.generate_temporal_analysis()
    print(f"✓ Analyzed publication trends across {len(temp_results['publication_trends']['papers_by_month'])} months")

    # Network analysis
    print("\n[5/6] Running network analysis...")
    network = NetworkAnalyzer(enriched_papers)
    net_results = network.generate_network_analysis()
    print(f"✓ Built co-authorship network with {net_results['coauthorship_network']['n_authors']} nodes")

    # Statistical analysis
    print("\n[6/6] Running statistical analysis...")
    statistical = StatisticalAnalyzer(enriched_papers)
    stat_results = statistical.generate_statistical_analysis()
    print(f"✓ Calculated descriptive statistics")

    # Generate BibTeX
    print("\n[Bonus] Generating BibTeX...")
    bibtex_mgr = BibTeXManager()
    bibtex_content = bibtex_mgr.generate_bibtex_from_papers(enriched_papers)
    print(f"✓ Generated BibTeX for {len(enriched_papers)} papers")

    # Summary
    print("\n" + "="*80)
    print("DEMO RESULTS SUMMARY")
    print("="*80)
    print(f"Total Papers: {len(enriched_papers)}")
    print(f"Total Authors: {bib_results['summary']['total_authors']}")
    print(f"Categories: {', '.join([cat for cat, _ in bib_results['category_distribution']['top_5_categories']])}")
    print(f"\nTop 3 Authors:")
    for i, (author, count) in enumerate(bib_results['author_productivity']['top_10_authors'][:3], 1):
        print(f"  {i}. {author} ({count} papers)")

    print(f"\nResearch Types:")
    for rtype, count in theme_results['theme_distribution'].items():
        print(f"  - {rtype}: {count} papers")

    print("\n" + "="*80)
    print("Demo completed successfully!")
    print("="*80)
    print("\nTo run the full pipeline with real ArXiv data:")
    print("  python main.py")
    print("\nNote: Full pipeline requires internet connection and may take 20-45 minutes")


if __name__ == "__main__":
    main()
