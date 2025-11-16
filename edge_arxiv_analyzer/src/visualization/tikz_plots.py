"""
TikZ/PGFPlots visualization module for generating LaTeX-native figures.

This module generates publication-quality TikZ and PGFPlots code that can be
directly embedded in LaTeX documents, providing vector graphics that are
perfectly integrated with the document typography.
"""

from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from pathlib import Path
from loguru import logger

# Import configuration
from ..utils.config import Config, FIGURES_DIR


class TikZGenerator:
    """Generate LaTeX-native TikZ and PGFPlots visualizations."""

    def __init__(self, config: Config = None):
        """
        Initialize TikZ generator.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self.figures_dir = Path(FIGURES_DIR)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        if not isinstance(text, str):
            text = str(text)

        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def _save_tikz(self, content: str, filename: str):
        """
        Save TikZ code to file.

        Args:
            content: TikZ code
            filename: Base filename (without extension)
        """
        filepath = self.figures_dir / f"{filename}.tex"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Saved TikZ figure: {filepath}")

    def generate_temporal_trends(self, temporal_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for temporal publication trends.

        Args:
            temporal_analysis: Temporal analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ temporal trends plot")

        pub_trends = temporal_analysis.get("publication_trends", {})
        papers_by_month = pub_trends.get("papers_by_month", {})

        if not papers_by_month:
            logger.warning("No temporal data available")
            return ""

        # Prepare data
        months = sorted(papers_by_month.keys())
        counts = [papers_by_month[m] for m in months]

        # Generate coordinates
        coordinates = "\n            ".join([
            f"({i}, {count})" for i, count in enumerate(counts)
        ])

        # Generate x-tick labels
        month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b") for m in months]
        xtick_labels = ", ".join([f"{label}" for label in month_labels])

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        width=0.95\textwidth,
        height=7cm,
        xlabel={Month (2025)},
        ylabel={Number of Papers},
        grid=major,
        grid style={dashed, gray!30},
        legend pos=north west,
        xtick={%s},
        xticklabels={%s},
        xticklabel style={rotate=45, anchor=east},
        ymin=0,
        ymajorgrids=true,
        xmajorgrids=false,
    ]

        % Main trend line
        \addplot[
            color=edgeblue,
            mark=*,
            mark size=3pt,
            line width=1.5pt,
        ] coordinates {
            %s
        };
        \addlegendentry{Publications per Month}

    \end{axis}
\end{tikzpicture}""" % (
            ", ".join([str(i) for i in range(len(months))]),
            xtick_labels,
            coordinates
        )

        self._save_tikz(tikz_code, "temporal_trends")
        return tikz_code

    def generate_category_distribution(self, bibliometric_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for category distribution bar chart.

        Args:
            bibliometric_analysis: Bibliometric analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ category distribution plot")

        category_dist = bibliometric_analysis.get("category_distribution", {})

        if not category_dist:
            logger.warning("No category data available")
            return ""

        # Sort by count and take top 10
        sorted_categories = sorted(category_dist.items(), key=lambda x: x[1], reverse=True)[:10]
        categories, counts = zip(*sorted_categories)

        # Escape LaTeX special characters in category names
        categories = [self._escape_latex(cat) for cat in categories]

        # Generate coordinates
        coordinates = "\n            ".join([
            f"({count}, {i})" for i, count in enumerate(counts)
        ])

        # Generate y-tick labels
        ytick_labels = ", ".join([f"{cat}" for cat in categories])

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        xbar,
        width=0.9\textwidth,
        height=8cm,
        xlabel={Number of Papers},
        ylabel={ArXiv Category},
        ytick={%s},
        yticklabels={%s},
        xmin=0,
        grid=major,
        grid style={dashed, gray!30},
        bar width=0.6cm,
        nodes near coords,
        nodes near coords align={horizontal},
        every node near coord/.append style={font=\footnotesize},
    ]

        \addplot[
            fill=edgeblue,
            draw=edgeblue!80!black,
        ] coordinates {
            %s
        };

    \end{axis}
\end{tikzpicture}""" % (
            ", ".join([str(i) for i in range(len(categories))]),
            ytick_labels,
            coordinates
        )

        self._save_tikz(tikz_code, "category_distribution")
        return tikz_code

    def generate_author_productivity(self, bibliometric_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for top authors horizontal bar chart.

        Args:
            bibliometric_analysis: Bibliometric analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ author productivity plot")

        author_prod = bibliometric_analysis.get("author_productivity", {})
        paper_counts = author_prod.get("paper_counts", {})

        if not paper_counts:
            logger.warning("No author productivity data available")
            return ""

        # Sort and take top 15
        sorted_authors = sorted(paper_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        authors, counts = zip(*sorted_authors)

        # Escape author names
        authors = [self._escape_latex(author) for author in authors]

        # Generate coordinates
        coordinates = "\n            ".join([
            f"({count}, {i})" for i, count in enumerate(counts)
        ])

        # Generate y-tick labels
        ytick_labels = ", ".join([f"{author}" for author in authors])

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        xbar,
        width=0.9\textwidth,
        height=10cm,
        xlabel={Number of Papers},
        ylabel={Author},
        ytick={%s},
        yticklabels={%s},
        yticklabel style={font=\small},
        xmin=0,
        grid=major,
        grid style={dashed, gray!30},
        bar width=0.5cm,
        nodes near coords,
        nodes near coords align={horizontal},
        every node near coord/.append style={font=\footnotesize},
    ]

        \addplot[
            fill=edgeorange,
            draw=edgeorange!80!black,
        ] coordinates {
            %s
        };

    \end{axis}
\end{tikzpicture}""" % (
            ", ".join([str(i) for i in range(len(authors))]),
            ytick_labels,
            coordinates
        )

        self._save_tikz(tikz_code, "author_productivity")
        return tikz_code

    def generate_research_type_pie(self, bibliometric_analysis: Dict[str, Any]) -> str:
        """
        Generate TikZ code for research type distribution pie chart.

        Args:
            bibliometric_analysis: Bibliometric analysis results

        Returns:
            str: TikZ code
        """
        logger.info("Generating TikZ research type pie chart")

        research_types = bibliometric_analysis.get("research_types", {})

        if not research_types:
            logger.warning("No research type data available")
            return ""

        # Calculate percentages
        total = sum(research_types.values())
        types_data = [(rtype, count, count/total*100)
                      for rtype, count in research_types.items()]
        types_data.sort(key=lambda x: x[1], reverse=True)

        # Colors for different slices
        colors = ['edgeblue', 'edgeorange', 'edgegreen', 'edgered',
                  'edgepurple', 'edgebrown', 'edgepink', 'edgegray']

        # Generate pie slices
        angle_start = 0
        slices = []
        legend_entries = []

        for i, (rtype, count, percentage) in enumerate(types_data):
            angle_end = angle_start + percentage * 3.6  # Convert percentage to degrees
            angle_mid = (angle_start + angle_end) / 2

            color = colors[i % len(colors)]
            escaped_rtype = self._escape_latex(rtype)

            slices.append(f"""        % {escaped_rtype}
        \\fill[{color}] (0,0) -- ({angle_start}:2) arc ({angle_start}:{angle_end}:2) -- cycle;
        \\draw[black, thick] (0,0) -- ({angle_start}:2) arc ({angle_start}:{angle_end}:2) -- cycle;
        \\node at ({angle_mid}:2.7) {{\\small {percentage:.1f}\\%}};""")

            legend_entries.append(f"        \\node[fill={color}, minimum width=0.3cm, minimum height=0.3cm] at ({i*0.8}, -3.5) {{}}; \\node[anchor=west] at ({i*0.8+0.2}, -3.5) {{\\footnotesize {escaped_rtype} ({count})}};")

            angle_start = angle_end

        tikz_code = r"""\begin{tikzpicture}
    \begin{scope}
%s
    \end{scope}

    % Legend
    \begin{scope}[shift={(0, -1)}]
%s
    \end{scope}
\end{tikzpicture}""" % (
            "\n".join(slices),
            "\n".join(legend_entries)
        )

        self._save_tikz(tikz_code, "research_type_distribution")
        return tikz_code

    def generate_collaboration_histogram(self, bibliometric_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for collaboration statistics histogram.

        Args:
            bibliometric_analysis: Bibliometric analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ collaboration histogram")

        collaboration = bibliometric_analysis.get("collaboration_patterns", {})
        authors_per_paper = collaboration.get("authors_per_paper", [])

        if not authors_per_paper:
            logger.warning("No collaboration data available")
            return ""

        # Count frequency of each author count
        from collections import Counter
        author_counts = Counter(authors_per_paper)

        # Sort by number of authors
        sorted_counts = sorted(author_counts.items())
        num_authors, frequencies = zip(*sorted_counts) if sorted_counts else ([], [])

        # Generate coordinates
        coordinates = "\n            ".join([
            f"({n}, {freq})" for n, freq in zip(num_authors, frequencies)
        ])

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        ybar,
        width=0.9\textwidth,
        height=7cm,
        xlabel={Number of Authors per Paper},
        ylabel={Frequency},
        xtick=data,
        xmin=0,
        ymin=0,
        grid=major,
        grid style={dashed, gray!30},
        bar width=0.7cm,
        nodes near coords,
        every node near coord/.append style={font=\footnotesize},
    ]

        \addplot[
            fill=edgegreen,
            draw=edgegreen!80!black,
        ] coordinates {
            %s
        };

    \end{axis}
\end{tikzpicture}""" % coordinates

        self._save_tikz(tikz_code, "collaboration_statistics")
        return tikz_code

    def generate_topic_heatmap(self, thematic_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for topic-keyword heatmap.

        Args:
            thematic_analysis: Thematic analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ topic heatmap")

        lda_topics = thematic_analysis.get("lda_topics", [])

        if not lda_topics or len(lda_topics) == 0:
            logger.warning("No LDA topic data available")
            return ""

        # Take first 5 topics and top 8 words per topic
        topics_to_show = min(5, len(lda_topics))
        words_per_topic = 8

        # Build matrix data
        matrix_data = []
        y_labels = []
        x_labels = []

        for topic_idx in range(topics_to_show):
            topic = lda_topics[topic_idx]
            words = topic.get("words", [])[:words_per_topic]
            weights = topic.get("weights", [])[:words_per_topic]

            y_labels.append(f"Topic {topic_idx + 1}")

            if topic_idx == 0:
                x_labels = [self._escape_latex(w) for w in words]

            # Normalize weights to 0-1 range for this topic
            if weights:
                max_weight = max(weights)
                normalized = [w/max_weight if max_weight > 0 else 0 for w in weights]
                matrix_data.extend([
                    f"        ({word_idx}, {topic_idx}, {norm_weight:.3f})"
                    for word_idx, norm_weight in enumerate(normalized)
                ])

        # Generate coordinates
        coordinates = "\n".join(matrix_data)

        # Generate labels
        ytick_labels = ", ".join([f"{label}" for label in y_labels])
        xtick_labels = ", ".join(x_labels)

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        colormap/viridis,
        colorbar,
        colorbar style={
            ylabel={Relative Weight},
        },
        width=0.95\textwidth,
        height=8cm,
        xlabel={Top Keywords},
        ylabel={LDA Topics},
        xtick={%s},
        xticklabels={%s},
        xticklabel style={rotate=45, anchor=east, font=\small},
        ytick={%s},
        yticklabels={%s},
        point meta min=0,
        point meta max=1,
        enlargelimits=false,
        axis on top,
    ]

        \addplot[
            matrix plot*,
            mesh/cols=%d,
            point meta=explicit,
        ] coordinates {
%s
        };

    \end{axis}
\end{tikzpicture}""" % (
            ", ".join([str(i) for i in range(words_per_topic)]),
            xtick_labels,
            ", ".join([str(i) for i in range(topics_to_show)]),
            ytick_labels,
            words_per_topic,
            coordinates
        )

        self._save_tikz(tikz_code, "topic_heatmap")
        return tikz_code

    def generate_network_graph(self, network_analysis: Dict[str, Any]) -> str:
        """
        Generate TikZ code for co-authorship network visualization.

        Args:
            network_analysis: Network analysis results

        Returns:
            str: TikZ code
        """
        logger.info("Generating TikZ network graph")

        coauthor_metrics = network_analysis.get("coauthorship_metrics", {})
        top_authors = coauthor_metrics.get("top_betweenness_authors", [])[:15]

        if not top_authors:
            logger.warning("No network data available")
            return ""

        # Create a simple network visualization
        # For a real network, we'd need the actual edges from the NetworkX graph
        # Here we'll create a simplified circular layout

        num_nodes = len(top_authors)
        radius = 3.5

        nodes = []
        for i, author_data in enumerate(top_authors):
            author = author_data.get("author", f"Author {i+1}")
            author_escaped = self._escape_latex(author)

            # Calculate position on circle
            angle = i * (360 / num_nodes)

            # Scale node size by betweenness centrality
            betweenness = author_data.get("betweenness", 0)
            node_size = 0.3 + betweenness * 2  # Scale appropriately

            nodes.append(f"""        \\node[circle, fill=edgeblue, draw=edgeblue!80!black,
              minimum size={node_size}cm, font=\\tiny, text=white]
              (n{i}) at ({angle}:{radius}) {{}};
        \\node[font=\\scriptsize] at ({angle}:{radius+0.8}) {{{author_escaped}}};""")

        # Add some edges (simplified - connect adjacent nodes in circle)
        edges = []
        for i in range(num_nodes):
            next_i = (i + 1) % num_nodes
            edges.append(f"        \\draw[gray, opacity=0.3] (n{i}) -- (n{next_i});")

        tikz_code = r"""\begin{tikzpicture}[scale=0.8]
    % Nodes
%s

    % Edges
%s

    % Title annotation
    \node[font=\small, anchor=north] at (0, -5) {Top 15 Authors by Betweenness Centrality};
\end{tikzpicture}""" % (
            "\n".join(nodes),
            "\n".join(edges)
        )

        self._save_tikz(tikz_code, "collaboration_network")
        return tikz_code

    def generate_monthly_category_trends(self, temporal_analysis: Dict[str, Any]) -> str:
        """
        Generate PGFPlots code for monthly category trends.

        Args:
            temporal_analysis: Temporal analysis results

        Returns:
            str: TikZ/PGFPlots code
        """
        logger.info("Generating TikZ monthly category trends")

        category_trends = temporal_analysis.get("category_trends", {})

        if not category_trends:
            logger.warning("No category trend data available")
            return ""

        # Get top 5 categories
        top_categories = sorted(category_trends.items(),
                               key=lambda x: sum(x[1].values()),
                               reverse=True)[:5]

        if not top_categories:
            return ""

        # Get all months
        all_months = set()
        for _, monthly_data in top_categories:
            all_months.update(monthly_data.keys())
        months = sorted(all_months)

        # Colors for different categories
        colors = ['edgeblue', 'edgeorange', 'edgegreen', 'edgered', 'edgepurple']

        # Generate plots for each category
        plots = []
        for i, (category, monthly_data) in enumerate(top_categories):
            escaped_cat = self._escape_latex(category)
            color = colors[i % len(colors)]

            coordinates = " ".join([
                f"({month_idx}, {monthly_data.get(month, 0)})"
                for month_idx, month in enumerate(months)
            ])

            plots.append(f"""        \\addplot[
            color={color},
            mark=*,
            mark size=2pt,
            line width=1.2pt,
        ] coordinates {{{coordinates}}};
        \\addlegendentry{{{escaped_cat}}}""")

        # Generate month labels
        month_labels = [datetime.strptime(m, "%Y-%m").strftime("%b") for m in months]
        xtick_labels = ", ".join(month_labels)

        tikz_code = r"""\begin{tikzpicture}
    \begin{axis}[
        width=0.95\textwidth,
        height=8cm,
        xlabel={Month (2025)},
        ylabel={Number of Papers},
        grid=major,
        grid style={dashed, gray!30},
        legend pos=north west,
        xtick={%s},
        xticklabels={%s},
        xticklabel style={rotate=45, anchor=east},
        ymin=0,
    ]

%s

    \end{axis}
\end{tikzpicture}""" % (
            ", ".join([str(i) for i in range(len(months))]),
            xtick_labels,
            "\n".join(plots)
        )

        self._save_tikz(tikz_code, "monthly_category_trends")
        return tikz_code

    def generate_all_figures(self, analysis_results: Dict[str, Any]):
        """
        Generate all TikZ figures from analysis results.

        Args:
            analysis_results: Complete analysis results dictionary
        """
        logger.info("Generating all TikZ figures")

        bibliometric = analysis_results.get("bibliometric", {})
        thematic = analysis_results.get("thematic", {})
        temporal = analysis_results.get("temporal", {})
        network = analysis_results.get("network", {})

        # Generate each figure type
        self.generate_temporal_trends(temporal)
        self.generate_category_distribution(bibliometric)
        self.generate_author_productivity(bibliometric)
        self.generate_research_type_pie(bibliometric)
        self.generate_collaboration_histogram(bibliometric)
        self.generate_topic_heatmap(thematic)
        self.generate_network_graph(network)
        self.generate_monthly_category_trends(temporal)

        logger.info("All TikZ figures generated successfully")


def main():
    """Main function for testing TikZ generator."""
    print("TikZ visualization generator module loaded successfully")


if __name__ == "__main__":
    main()
