# Edge of ArXiv: Cutting-Edge Computing Research Trends in 2025

A comprehensive Python application for analyzing ArXiv.org papers on edge computing, performing bibliometric and thematic analyses, and automatically generating a publication-ready review paper.

## Overview

This project automatically:
1. Scrapes edge computing papers from ArXiv (2025)
2. Performs comprehensive bibliometric analysis
3. Conducts thematic analysis using NLP and topic modeling
4. Analyzes temporal trends and collaboration networks
5. Generates publication-quality visualizations
6. Creates LaTeX tables and BibTeX files
7. Produces a complete review paper ready for submission to Q1 journals

## Features

### Data Collection
- **ArXiv API Integration**: Automated querying with rate limiting
- **Comprehensive Metadata**: Extracts titles, authors, abstracts, categories, dates
- **Smart Caching**: Avoids redundant API calls
- **Data Validation**: Ensures quality and completeness

### Analysis Capabilities

#### Bibliometric Analysis
- Author productivity metrics (papers per author, h-index estimation)
- Institutional and geographic distribution
- Collaboration pattern analysis
- Category distribution across ArXiv taxonomy
- Keyword frequency and co-occurrence

#### Thematic Analysis
- Topic modeling (LDA, NMF)
- Keyword extraction (TF-IDF based)
- Abstract clustering (K-Means)
- Research theme identification
- Emerging topics detection

#### Temporal Analysis
- Publication trend analysis
- Seasonal pattern detection
- Category-specific trends
- Growth metrics and forecasting
- Trend significance testing

#### Network Analysis
- Co-authorship network construction
- Research community detection (Louvain algorithm)
- Centrality measures (degree, betweenness, closeness, eigenvector)
- Keyword co-occurrence networks

#### Statistical Analysis
- Descriptive statistics
- Correlation analysis
- Hypothesis testing (t-tests, chi-square)
- Outlier detection
- Trend significance testing

### Visualization
Publication-quality figures in PDF and PNG formats:
- Temporal trend plots with trend lines
- Category distribution bar charts
- Author productivity visualizations
- Collaboration networks (NetworkX)
- Word clouds from keywords
- Research type pie charts
- Topic heatmaps
- Multi-panel statistical summaries

### Paper Generation
- Complete LaTeX document with proper structure
- Automatically generated BibTeX files
- Professional tables with booktabs
- Figure integration with captions
- Academic writing style suitable for Q1 journals
- Automatic PDF compilation (if LaTeX available)

## Installation

### Prerequisites
- Python 3.8 or higher
- LaTeX distribution (optional, for PDF generation)
  - Linux: `sudo apt-get install texlive-full`
  - macOS: Install MacTeX
  - Windows: Install MiKTeX

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd arxivedge
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
cd edge_arxiv_analyzer
pip install -r requirements.txt
```

4. Download NLTK data (first time only):
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Usage

### Quick Start

Run the complete pipeline:
```bash
python main.py
```

This will:
- Scrape ArXiv papers from 2025
- Perform all analyses
- Generate all visualizations
- Create LaTeX tables and BibTeX files
- Generate the review paper
- Attempt PDF compilation

### Options

Skip scraping and use cached data:
```bash
python main.py --skip-scraping
```

Use custom configuration:
```bash
python main.py --config custom_config.yaml
```

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific test module:
```bash
pytest tests/test_scraper.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
edge_arxiv_analyzer/
├── src/
│   ├── scraper/
│   │   ├── arxiv_scraper.py       # ArXiv API interaction
│   │   └── metadata_extractor.py   # Metadata enrichment
│   ├── analysis/
│   │   ├── bibliometric.py        # Author/citation analysis
│   │   ├── thematic.py            # Topic modeling
│   │   ├── temporal.py            # Time-series analysis
│   │   ├── network.py             # Network analysis
│   │   └── statistical.py         # Statistical tests
│   ├── visualization/
│   │   ├── plots.py               # Figure generation
│   │   └── tables.py              # LaTeX tables
│   ├── paper_generator/
│   │   ├── latex_writer.py        # Paper generation
│   │   ├── bibtex_manager.py      # BibTeX handling
│   │   └── templates/             # LaTeX templates
│   └── utils/
│       ├── config.py              # Configuration
│       └── validators.py          # Data validation
├── tests/                         # Test suite
├── output/                        # Generated outputs
│   ├── data/                      # Raw and processed data
│   ├── figures/                   # Visualizations
│   ├── tables/                    # LaTeX tables
│   ├── bibtex/                    # BibTeX files
│   └── paper/                     # Final paper
├── requirements.txt
├── main.py                        # Main pipeline
└── README.md
```

## Output Files

After running the pipeline, the `output/` directory contains:

### Data Files
- `raw_arxiv_data.json`: Original ArXiv data
- `processed_papers.csv`: Enriched paper metadata
- `author_network.graphml`: Co-authorship network
- `analysis_results.json`: Complete analysis results

### Figures (PDF & PNG)
- `temporal_trends.pdf`: Publication trends over time
- `category_distribution.pdf`: ArXiv category breakdown
- `author_productivity.pdf`: Top authors visualization
- `collaboration_network.pdf`: Co-authorship network
- `keyword_cloud.pdf`: Keyword word cloud
- `research_type_distribution.pdf`: Research type pie chart
- `topic_heatmap.pdf`: Topic-keyword associations
- `collaboration_statistics.pdf`: Collaboration metrics
- `monthly_category_trends.pdf`: Category evolution

### Tables (LaTeX)
- `top_authors.tex`: Top 15 prolific authors
- `category_distribution.tex`: Category breakdown
- `keyword_frequency.tex`: Top 20 keywords
- `research_types.tex`: Research type distribution
- `statistical_summary.tex`: Descriptive statistics
- `lda_topics.tex`: Discovered topics

### BibTeX Files
- `all_papers_2025.bib`: All analyzed papers
- `highly_relevant.bib`: Top 50 papers
- `cited_in_paper.bib`: Papers cited in review

### Paper
- `edge_of_arxiv_2025.tex`: Complete LaTeX document
- `edge_of_arxiv_2025.pdf`: Compiled paper (if LaTeX available)

## Configuration

Edit `src/utils/config.py` to customize:

### Search Parameters
```python
ARXIV_SEARCH_KEYWORDS = [
    "edge computing",
    "mobile edge computing",
    "fog computing",
    # Add more keywords...
]

YEAR_START = 2025
YEAR_END = 2025
```

### Analysis Settings
```python
N_TOPICS_LDA = 10  # Number of LDA topics
N_TOPICS_BERT = 8  # Number of BERT topics
```

### Visualization Settings
```python
FIGURE_DPI = 300
FIGURE_FORMAT = "pdf"
COLOR_PALETTE = "Set2"
```

## Key Dependencies

### Core Libraries
- `arxiv>=2.1.0` - ArXiv API access
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing

### NLP & ML
- `nltk>=3.8.0` - Natural language processing
- `scikit-learn>=1.3.0` - Machine learning
- `gensim>=4.3.0` - Topic modeling

### Network Analysis
- `networkx>=3.1` - Network analysis
- `python-igraph>=0.11.0` - Fast network algorithms
- `community>=1.0.0` - Community detection

### Visualization
- `matplotlib>=3.7.0` - Plotting
- `seaborn>=0.12.0` - Statistical visualization
- `wordcloud>=1.9.0` - Word clouds
- `plotly>=5.17.0` - Interactive plots

### Document Generation
- `pylatex>=1.4.0` - LaTeX generation
- `bibtexparser>=1.4.0` - BibTeX handling

## Methodology

### Search Strategy
Papers are retrieved using ArXiv API with queries targeting:
- Keywords: edge computing, fog computing, MEC, edge AI, etc.
- Categories: cs.DC, cs.NI, cs.AI, cs.LG
- Year: 2025
- Sorted by: submission date (newest first)

### Analysis Pipeline
1. **Data Collection**: ArXiv API with rate limiting (3s delay)
2. **Preprocessing**: Text cleaning, normalization
3. **Enrichment**: Keyword extraction, type classification
4. **Analysis**: Parallel execution of analysis modules
5. **Visualization**: Publication-quality figure generation
6. **Paper Generation**: Automated LaTeX document creation

### Quality Assurance
- Data validation at each step
- Duplicate detection and removal
- Completeness checks (>90% required)
- Type consistency validation
- BibTeX format validation
- LaTeX compilation testing

## Research Paper Structure

The generated paper includes:

1. **Abstract**: Overview of findings
2. **Introduction**: Context and research questions
3. **Methodology**: Data collection and analysis methods
4. **Bibliometric Analysis**: Author, category, keyword analysis
5. **Thematic Analysis**: Topic modeling results
6. **Temporal Trends**: Publication evolution
7. **Network Analysis**: Collaboration patterns
8. **Statistical Analysis**: Quantitative findings
9. **Discussion**: Research gaps and opportunities
10. **Conclusion**: Key insights and future directions
11. **References**: Complete BibTeX bibliography

## Performance

### Typical Execution Time
- Data collection: 15-30 minutes (depends on paper count)
- Analysis: 5-10 minutes
- Visualization: 2-5 minutes
- Paper generation: 1-2 minutes
- **Total**: ~20-45 minutes

### Resource Usage
- Memory: ~2-4 GB (depends on paper count)
- Disk: ~500 MB (includes all outputs)
- CPU: Multi-core utilization for analysis

## Troubleshooting

### ArXiv API Issues
```python
# Increase delay if rate-limited
ARXIV_API_DELAY = 5.0  # seconds
```

### Memory Issues
```python
# Reduce max results if running out of memory
ARXIV_MAX_RESULTS = 1000
```

### LaTeX Compilation Errors
- Ensure all required packages are installed
- Check `.log` file in `output/paper/` directory
- Run pdflatex manually for detailed errors

### NLTK Data Missing
```bash
python -c "import nltk; nltk.download('all')"
```

## Citation

If you use this software in your research, please cite:

```bibtex
@software{arxiv_edge_analyzer_2025,
  title = {Edge of ArXiv: Automated Review Paper Generator},
  author = {ArXiv Analysis System},
  year = {2025},
  url = {https://github.com/yourusername/arxivedge}
}
```

## License

This project is licensed under the MIT License.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Acknowledgments

- ArXiv.org for providing open access to research
- NetworkX team for network analysis tools
- scikit-learn developers for ML algorithms
- Matplotlib/Seaborn teams for visualization

## Contact

For questions or issues:
- GitHub Issues: [Create an issue](https://github.com/yourusername/arxivedge/issues)
- Email: your.email@example.com

## Future Enhancements

- [ ] Interactive web dashboard (Dash/Streamlit)
- [ ] Integration with Semantic Scholar API for citations
- [ ] Support for other preprint servers (bioRxiv, medRxiv)
- [ ] Automated email reports
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Multi-language support
- [ ] Real-time monitoring dashboard
- [ ] Machine learning for impact prediction

---

**Version**: 1.0.0
**Last Updated**: 2025-11-15
**Status**: Production Ready
