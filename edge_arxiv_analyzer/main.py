#!/usr/bin/env python3
"""
Main execution script for ArXiv Edge Computing Review Paper Generator.

This script orchestrates the complete pipeline:
1. Scrape ArXiv papers on edge computing
2. Extract and enrich metadata
3. Run all analyses (bibliometric, thematic, temporal, network, statistical)
4. Generate visualizations
5. Create LaTeX tables
6. Generate BibTeX files
7. Create complete review paper
8. Compile to PDF (if LaTeX is available)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config import Config, OUTPUT_DIR, get_data_path
from src.utils.validators import validate_pipeline_output, DataQualityChecker

# Import modules
from src.scraper.arxiv_scraper import ArXivScraper
from src.scraper.metadata_extractor import MetadataExtractor
from src.analysis.bibliometric import BibliometricAnalyzer
from src.analysis.thematic import ThematicAnalyzer
from src.analysis.temporal import TemporalAnalyzer
from src.analysis.network import NetworkAnalyzer
from src.analysis.statistical import StatisticalAnalyzer
from src.visualization.plots import VisualizationGenerator
from src.visualization.tables import TableGenerator
from src.paper_generator.bibtex_manager import BibTeXManager
from src.paper_generator.latex_writer import LaTeXWriter


# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add(OUTPUT_DIR / "arxiv_analyzer.log", level="DEBUG", rotation="10 MB")


class ArXivEdgeAnalyzer:
    """Main pipeline orchestrator."""

    def __init__(self, config: Config = None):
        """
        Initialize analyzer.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.papers = []
        self.enriched_papers = []
        self.analysis_results = {}

    def run_pipeline(self, skip_scraping: bool = False):
        """
        Execute complete analysis pipeline.

        Args:
            skip_scraping: If True, load papers from cache instead of scraping
        """
        logger.info("="*80)
        logger.info("Starting ArXiv Edge Computing Analysis Pipeline")
        logger.info("="*80)

        try:
            # Step 1: Data Collection
            if not skip_scraping:
                self.collect_data()
            else:
                self.load_cached_data()

            # Step 2: Data Enrichment
            self.enrich_metadata()

            # Step 3: Data Quality Check
            self.check_data_quality()

            # Step 4: Run Analyses
            self.run_analyses()

            # Step 5: Generate Visualizations
            self.generate_visualizations()

            # Step 6: Generate Tables
            self.generate_tables()

            # Step 7: Generate BibTeX
            self.generate_bibtex()

            # Step 8: Generate Paper
            self.generate_paper()

            # Step 9: Validate Output
            self.validate_output()

            # Step 10: Generate Summary
            self.generate_summary()

            logger.info("="*80)
            logger.info("Pipeline completed successfully!")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    def collect_data(self):
        """Step 1: Collect papers from ArXiv."""
        logger.info("Step 1: Collecting data from ArXiv")

        scraper = ArXivScraper(self.config)
        self.papers = scraper.search_edge_papers_2025()

        logger.info(f"Collected {len(self.papers)} papers")

        # Get statistics
        stats = scraper.get_statistics()
        logger.info(f"Statistics: {json.dumps(stats, indent=2, default=str)}")

    def load_cached_data(self):
        """Load papers from cached data."""
        logger.info("Loading cached data")

        cache_file = get_data_path("raw_arxiv_data.json")
        if not cache_file.exists():
            raise FileNotFoundError(f"Cache file not found: {cache_file}")

        with open(cache_file, 'r') as f:
            self.papers = json.load(f)

        # Convert date strings back to datetime objects
        from datetime import datetime
        for paper in self.papers:
            if "published" in paper and isinstance(paper["published"], str):
                paper["published"] = datetime.fromisoformat(paper["published"].replace("Z", "+00:00"))

        logger.info(f"Loaded {len(self.papers)} papers from cache")

    def enrich_metadata(self):
        """Step 2: Enrich metadata."""
        logger.info("Step 2: Enriching metadata")

        extractor = MetadataExtractor()
        self.enriched_papers = extractor.enrich_papers(self.papers)

        # Save processed data
        output_file = get_data_path("processed_papers.csv")
        extractor.save_processed_data(self.enriched_papers, output_file)

        logger.info(f"Enriched {len(self.enriched_papers)} papers")

    def check_data_quality(self):
        """Step 3: Check data quality."""
        logger.info("Step 3: Checking data quality")

        checker = DataQualityChecker()

        # Completeness check
        completeness = checker.check_completeness(self.enriched_papers)
        logger.info(f"Data completeness: {completeness['completeness_score']:.2%}")

        # Duplicate check
        duplicates = checker.identify_duplicates(self.enriched_papers)
        if duplicates:
            logger.warning(f"Found {len(duplicates)} potential duplicates")

        # Type check
        type_issues = checker.check_data_types(self.enriched_papers)
        if type_issues:
            logger.warning(f"Found data type issues: {type_issues}")

    def run_analyses(self):
        """Step 4: Run all analyses."""
        logger.info("Step 4: Running analyses")

        self.analysis_results = {}

        # Bibliometric analysis
        logger.info("Running bibliometric analysis...")
        bibliometric_analyzer = BibliometricAnalyzer(self.enriched_papers)
        self.analysis_results["bibliometric"] = bibliometric_analyzer.generate_metrics()

        # Thematic analysis
        logger.info("Running thematic analysis...")
        thematic_analyzer = ThematicAnalyzer(self.enriched_papers)
        self.analysis_results["thematic"] = thematic_analyzer.identify_research_themes()

        # Temporal analysis
        logger.info("Running temporal analysis...")
        temporal_analyzer = TemporalAnalyzer(self.enriched_papers)
        self.analysis_results["temporal"] = temporal_analyzer.generate_temporal_analysis()

        # Network analysis
        logger.info("Running network analysis...")
        network_analyzer = NetworkAnalyzer(self.enriched_papers)
        self.analysis_results["network"] = network_analyzer.generate_network_analysis()

        # Export network
        network_file = get_data_path("author_network.graphml")
        network_analyzer.export_network(network_file, "coauthor")

        # Statistical analysis
        logger.info("Running statistical analysis...")
        statistical_analyzer = StatisticalAnalyzer(self.enriched_papers)
        self.analysis_results["statistical"] = statistical_analyzer.generate_statistical_analysis()

        # Save analysis results
        results_file = get_data_path("analysis_results.json")
        with open(results_file, 'w') as f:
            json.dump(self.analysis_results, f, indent=2, default=str)

        logger.info("All analyses completed")

    def generate_visualizations(self):
        """Step 5: Generate visualizations."""
        logger.info("Step 5: Generating visualizations")

        # Generate matplotlib figures (PDF/PNG)
        viz_generator = VisualizationGenerator(self.config)
        figures = viz_generator.create_all_figures(self.analysis_results)
        logger.info(f"Generated {len(figures)} matplotlib figures")

        # Generate TikZ/LaTeX-native figures
        from src.visualization.tikz_plots import TikZGenerator
        tikz_generator = TikZGenerator(self.config)
        tikz_generator.generate_all_figures(self.analysis_results)
        logger.info("Generated TikZ/LaTeX-native figures")

    def generate_tables(self):
        """Step 6: Generate LaTeX tables."""
        logger.info("Step 6: Generating LaTeX tables")

        table_generator = TableGenerator()
        tables = table_generator.generate_all_tables(self.analysis_results)

        logger.info(f"Generated {len(tables)} tables")

    def generate_bibtex(self):
        """Step 7: Generate BibTeX files."""
        logger.info("Step 7: Generating BibTeX files")

        bibtex_manager = BibTeXManager()
        bibtex_manager.generate_all_bibtex_files(self.enriched_papers)

        logger.info("BibTeX files generated")

    def generate_paper(self):
        """Step 8: Generate LaTeX paper."""
        logger.info("Step 8: Generating LaTeX paper")

        latex_writer = LaTeXWriter(self.config)
        paper_content = latex_writer.generate_paper(self.analysis_results)

        logger.info("LaTeX paper generated")

        # Try to compile if pdflatex is available
        self.compile_pdf()

    def compile_pdf(self):
        """Attempt to compile LaTeX to PDF."""
        import subprocess
        from src.utils.config import get_paper_path, PAPER_DIR

        logger.info("Attempting to compile PDF...")

        tex_file = get_paper_path("edge_of_arxiv_2025.tex")

        try:
            # Change to paper directory
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                cwd=PAPER_DIR,
                capture_output=True,
                timeout=120
            )

            if result.returncode == 0:
                logger.info("PDF compiled successfully!")

                # Run again for references
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_file.name],
                    cwd=PAPER_DIR,
                    capture_output=True,
                    timeout=120
                )

                pdf_file = PAPER_DIR / "edge_of_arxiv_2025.pdf"
                if pdf_file.exists():
                    logger.info(f"PDF saved to: {pdf_file}")
            else:
                logger.warning("PDF compilation had errors (check .log file)")

        except FileNotFoundError:
            logger.warning("pdflatex not found - skipping PDF compilation")
        except subprocess.TimeoutExpired:
            logger.warning("PDF compilation timed out")
        except Exception as e:
            logger.warning(f"PDF compilation failed: {e}")

    def validate_output(self):
        """Step 9: Validate pipeline output."""
        logger.info("Step 9: Validating output")

        validation_results = validate_pipeline_output(OUTPUT_DIR)

        all_valid = all(validation_results.values())

        if all_valid:
            logger.info("All outputs validated successfully ✓")
        else:
            logger.warning("Some outputs missing:")
            for output_type, valid in validation_results.items():
                if not valid:
                    logger.warning(f"  - {output_type}: MISSING")

    def generate_summary(self):
        """Step 10: Generate summary report."""
        logger.info("Step 10: Generating summary report")

        summary = {
            "pipeline_run": datetime.now().isoformat(),
            "total_papers": len(self.enriched_papers),
            "analysis_results": {
                "bibliometric": {
                    "total_authors": self.analysis_results.get("bibliometric", {}).get("summary", {}).get("total_authors", 0),
                    "total_categories": self.analysis_results.get("bibliometric", {}).get("summary", {}).get("total_categories", 0),
                },
                "thematic": {
                    "n_topics": len(self.analysis_results.get("thematic", {}).get("lda_topics", {}).get("topics", {})),
                },
                "network": {
                    "n_authors": self.analysis_results.get("network", {}).get("coauthorship_network", {}).get("n_authors", 0),
                },
            },
            "output_files": {
                "data": len(list(OUTPUT_DIR.glob("data/*"))),
                "figures": len(list(OUTPUT_DIR.glob("figures/*"))),
                "tables": len(list(OUTPUT_DIR.glob("tables/*"))),
                "bibtex": len(list(OUTPUT_DIR.glob("bibtex/*"))),
                "paper": len(list(OUTPUT_DIR.glob("paper/*"))),
            }
        }

        summary_file = OUTPUT_DIR / "pipeline_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"Summary saved to: {summary_file}")

        # Print summary
        print("\n" + "="*80)
        print("PIPELINE SUMMARY")
        print("="*80)
        print(f"Total Papers Analyzed: {summary['total_papers']}")
        print(f"Total Authors: {summary['analysis_results']['bibliometric']['total_authors']}")
        print(f"Topics Identified: {summary['analysis_results']['thematic']['n_topics']}")
        print(f"\nOutput Files:")
        for output_type, count in summary['output_files'].items():
            print(f"  - {output_type}: {count} files")
        print("="*80)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ArXiv Edge Computing Review Paper Generator"
    )
    parser.add_argument(
        "--skip-scraping",
        action="store_true",
        help="Skip scraping and use cached data"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to custom configuration file"
    )

    args = parser.parse_args()

    # Initialize configuration
    config = Config()
    if args.config:
        logger.info(f"Loading custom configuration from {args.config}")
        # Load custom config if provided

    # Save configuration
    config.save_config()

    # Run pipeline
    analyzer = ArXivEdgeAnalyzer(config)
    analyzer.run_pipeline(skip_scraping=args.skip_scraping)


if __name__ == "__main__":
    main()
