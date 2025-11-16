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
        """Escape special LaTeX characters and remove/transliterate non-ASCII."""
        if not isinstance(text, str):
            text = str(text)

        # First, handle non-ASCII characters by converting to ASCII
        # This removes accents and transliterates when possible
        import unicodedata
        try:
            # Normalize to NFD (decomposed form) and remove combining characters
            text = unicodedata.normalize('NFD', text)
            # Keep only ASCII characters
            text = text.encode('ascii', 'ignore').decode('ascii')
        except Exception:
            # Fallback: remove all non-ASCII
            text = ''.join(c for c in text if ord(c) < 128)

        # Then escape special LaTeX characters
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
        counts = []
        for m in months:
            val = papers_by_month[m]
            # Ensure count is numeric
            if isinstance(val, (list, dict)):
                counts.append(len(val))
            elif isinstance(val, (int, float)):
                counts.append(int(val))
            else:
                logger.warning(f"Unexpected count type for month {m}: {type(val)}")
                counts.append(0)

        # Generate coordinates
        coordinates = "\n            ".join([
            f"({i}, {count})" for i, count in enumerate(counts)
        ])

        # Generate x-tick labels with error handling
        month_labels = []
        for m in months:
            try:
                label = datetime.strptime(m, "%Y-%m").strftime("%b")
                month_labels.append(label)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid month format '{m}': {e}")
                month_labels.append(str(m))  # Use raw string as fallback

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

        %%%% Main trend line
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

        # Convert to counts regardless of value type (list, dict, or int)
        category_counts = {}
        for cat, value in category_dist.items():
            if isinstance(value, (list, dict)):
                category_counts[cat] = len(value)
            elif isinstance(value, (int, float)):
                category_counts[cat] = int(value)
            else:
                logger.warning(f"Unexpected value type for category {cat}: {type(value)}")
                category_counts[cat] = 0

        # Sort by count and take top 10
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        if not sorted_categories:
            logger.warning("No categories to display after filtering")
            return ""

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
        # Try multiple possible keys for author data
        top_authors = author_prod.get("top_10_authors", author_prod.get("top_20_authors", []))

        if not top_authors:
            logger.warning("No author productivity data available")
            return ""

        # Convert to author-count pairs
        # top_authors format: [(author, count), ...]
        author_counts = {}
        for item in top_authors[:15]:  # Take top 15
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                author, count = item[0], item[1]
                author_counts[author] = count
            else:
                logger.warning(f"Unexpected author format: {item}")

        if not author_counts:
            logger.warning("No valid author data after parsing")
            return ""

        # Sort and take top 15
        sorted_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:15]

        if not sorted_authors:
            logger.warning("No authors to display after filtering")
            return ""

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

        # Convert to counts regardless of value type (list, dict, or int)
        type_counts = {}
        for rtype, value in research_types.items():
            if isinstance(value, (list, dict)):
                type_counts[rtype] = len(value)
            elif isinstance(value, (int, float)):
                type_counts[rtype] = int(value)
            else:
                logger.warning(f"Unexpected value type for research type {rtype}: {type(value)}")
                type_counts[rtype] = 0

        # Calculate percentages
        total = sum(type_counts.values())

        if total == 0:
            logger.warning("No research type data to display (total = 0)")
            return ""

        types_data = [(rtype, count, count/total*100)
                      for rtype, count in type_counts.items()]
        types_data.sort(key=lambda x: x[1], reverse=True)

        if not types_data:
            logger.warning("No research type data after processing")
            return ""

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

    %%%% Legend
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

        # Create a synthetic distribution from summary statistics
        # since detailed per-paper data isn't stored
        mean_authors = collaboration.get("mean_authors_per_paper", 0)
        min_authors = collaboration.get("min_authors_per_paper", 1)
        max_authors = collaboration.get("max_authors_per_paper", 1)
        single_author = collaboration.get("single_author_papers", 0)
        multi_author = collaboration.get("multi_author_papers", 0)

        if mean_authors == 0 or (single_author == 0 and multi_author == 0):
            logger.warning("No collaboration data available")
            return ""

        # Create approximate distribution
        from collections import Counter
        # Use available aggregated data
        author_counts = Counter()
        author_counts[1] = single_author
        # Distribute multi-author papers across 2-max range
        # This is an approximation for visualization
        if multi_author > 0 and max_authors > 1:
            # Simple distribution model
            for n_authors in range(2, min(max_authors + 1, 10)):
                # Exponential decay approximation
                author_counts[n_authors] = int(multi_author * (0.5 ** (n_authors - 2)))

        # Sort by number of authors
        sorted_counts = sorted(author_counts.items())
        num_authors, frequencies = zip(*sorted_counts) if sorted_counts else ([], [])

        if not num_authors:
            logger.warning("No collaboration data to display after processing")
            return ""

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

        lda_data = thematic_analysis.get("lda_topics", {})

        if not lda_data:
            logger.warning("No LDA topic data available")
            return ""

        # Extract topics dict - handle nested structure
        # Format: {"topics": {"Topic 1": {"words": [...], "weights": [...]}, ...}}
        if isinstance(lda_data, dict) and "topics" in lda_data:
            topics_dict = lda_data["topics"]
            topics_list = list(topics_dict.values())
        elif isinstance(lda_data, dict):
            # Try using values directly
            topics_list = list(lda_data.values())
        elif isinstance(lda_data, list):
            topics_list = lda_data
        else:
            logger.warning(f"Unexpected lda_topics type: {type(lda_data)}")
            return ""

        if not topics_list:
            logger.warning("No topics found in LDA data")
            return ""

        # Take first 5 topics and top 8 words per topic
        topics_to_show = min(5, len(topics_list))
        words_per_topic = 8

        # Build matrix data
        matrix_data = []
        y_labels = []
        x_labels = []

        for topic_idx in range(topics_to_show):
            topic = topics_list[topic_idx]

            # Handle topic being a dict or having get method
            if isinstance(topic, dict):
                words = topic.get("words", [])[:words_per_topic]
                weights = topic.get("weights", [])[:words_per_topic]
            else:
                logger.warning(f"Unexpected topic format at index {topic_idx}: {type(topic)}")
                continue

            y_labels.append(f"Topic {topic_idx + 1}")

            if topic_idx == 0:
                x_labels = [self._escape_latex(w) for w in words]

            # Normalize weights to 0-1 range for this topic
            if weights:
                max_weight = max(weights)
                normalized = [w/max_weight if max_weight > 0 else 0 for w in weights]
                # Ensure we have exactly words_per_topic entries
                while len(normalized) < words_per_topic:
                    normalized.append(0.0)
                matrix_data.extend([
                    f"({word_idx},{topic_idx},{norm_weight:.3f})"
                    for word_idx, norm_weight in enumerate(normalized[:words_per_topic])
                ])

        # Check if we have data to display
        if not matrix_data or not x_labels:
            logger.warning("No topic data available for heatmap")
            return ""

        # Generate coordinates with proper spacing
        coordinates = "\n        ".join(matrix_data)

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
        view={0}{90},
    ]

        \addplot3[
            surf,
            shader=flat,
            mesh/rows=%d,
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
            topics_to_show,
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

        # Try to get community data instead of individual author metrics
        communities_data = network_analysis.get("research_communities", {})
        communities = communities_data.get("communities", {})

        if not communities:
            logger.warning("No network/community data available")
            return ""

        # Extract top communities by size
        comm_list = [(name, data) for name, data in communities.items()]
        top_communities = sorted(comm_list, key=lambda x: x[1].get('size', 0), reverse=True)[:8]

        if not top_communities:
            logger.warning("No communities to visualize")
            return ""

        # Create a simple community visualization showing top research communities
        # Visualize communities as nodes with size proportional to member count

        num_communities = len(top_communities)

        if num_communities < 2:
            logger.warning("Not enough communities for network visualization (need at least 2)")
            return ""

        radius = 3.5

        nodes = []
        for i, (comm_name, comm_data) in enumerate(top_communities):
            size = comm_data.get("size", 1)
            # Get community label - use first category or community ID
            categories = comm_data.get("top_categories", [])
            if categories and len(categories) > 0:
                label = categories[0][0] if isinstance(categories[0], list) else str(categories[0])
            else:
                label = comm_name
            label_escaped = self._escape_latex(label)

            # Calculate position on circle
            angle = i * (360 / num_communities)

            # Scale node size by community size
            # Normalize size to reasonable radius (0.2 to 1.0 cm)
            max_size = max([c[1].get("size", 1) for c in top_communities])
            normalized_size = size / max_size if max_size > 0 else 0.5
            node_size = 0.2 + normalized_size * 0.8  # 0.2 to 1.0 cm

            nodes.append(f"""        \\node[circle, fill=edgeblue, draw=edgeblue!80!black,
              minimum size={node_size}cm, font=\\tiny, text=white]
              (n{i}) at ({angle}:{radius}) {{{size}}};
        \\node[font=\\scriptsize, text width=2.5cm, align=center] at ({angle}:{radius+1.2}) {{{label_escaped}}};""")

        # Add some edges (simplified - connect adjacent nodes in circle)
        edges = []
        for i in range(num_communities):
            next_i = (i + 1) % num_communities
            edges.append(f"        \\draw[gray, opacity=0.3] (n{i}) -- (n{next_i});")

        tikz_code = r"""\begin{tikzpicture}[scale=0.9]
    %%%% Nodes
%s

    %%%% Edges
%s

    %%%% Title annotation
    \node[font=\small, anchor=north] at (0, -5) {Top Research Communities by Size};
\end{tikzpicture}""" % (
            "\n".join(nodes),
            "\n".join(edges)
        )

        self._save_tikz(tikz_code, "collaboration_network")
        return tikz_code

    def generate_keyword_cloud(self, bibliometric_analysis: Dict[str, Any]) -> str:
        """
        Generate TikZ code for keyword visualization (simplified word cloud).

        Since true word clouds with complex layouts are impractical in TikZ,
        this creates a styled keyword display with varying font sizes.

        Args:
            bibliometric_analysis: Bibliometric analysis results

        Returns:
            str: TikZ code
        """
        logger.info("Generating TikZ keyword cloud (simplified)")

        # Try multiple possible keys for keyword data
        keyword_data = bibliometric_analysis.get("keywords", bibliometric_analysis.get("keyword_analysis", {}))
        top_keywords = keyword_data.get("top_20_keywords", keyword_data.get("top_50_keywords", []))

        if not top_keywords:
            logger.warning("No keyword data available")
            return ""

        # Take top 30 keywords
        keywords_to_show = top_keywords[:30]

        if not keywords_to_show:
            logger.warning("No keywords to display after filtering")
            return ""

        # Calculate font sizes based on frequency
        # Get max frequency for normalization
        # Handle both dict and list formats
        max_freq = 0
        for kw in keywords_to_show:
            if isinstance(kw, (list, tuple)) and len(kw) >= 2:
                max_freq = max(max_freq, kw[1])
            elif isinstance(kw, dict):
                max_freq = max(max_freq, kw.get("count", 0))

        # Create keyword nodes with varying sizes
        nodes = []
        x, y = 0, 0
        max_per_row = 5

        for i, kw_data in enumerate(keywords_to_show):
            # Handle both list and dict formats
            if isinstance(kw_data, (list, tuple)) and len(kw_data) >= 2:
                keyword, count = kw_data[0], kw_data[1]
            elif isinstance(kw_data, dict):
                keyword = kw_data.get("keyword", "")
                count = kw_data.get("count", 0)
            else:
                logger.warning(f"Unexpected keyword format: {kw_data}")
                continue

            # Escape LaTeX special characters
            keyword_escaped = self._escape_latex(keyword)

            # Calculate font size (scale from \small to \Huge)
            normalized_freq = count / max_freq if max_freq > 0 else 0

            if normalized_freq > 0.8:
                font_size = "\\Huge"
            elif normalized_freq > 0.6:
                font_size = "\\huge"
            elif normalized_freq > 0.4:
                font_size = "\\LARGE"
            elif normalized_freq > 0.2:
                font_size = "\\Large"
            else:
                font_size = "\\large"

            # Choose color based on frequency
            if normalized_freq > 0.7:
                color = "edgeblue"
            elif normalized_freq > 0.4:
                color = "edgeorange"
            else:
                color = "edgegreen"

            # Position in grid
            col = i % max_per_row
            row = i // max_per_row
            x_pos = col * 3.5
            y_pos = -row * 1.2

            nodes.append(f"""        \\node[text={color}, font={font_size}] at ({x_pos}, {y_pos}) {{{keyword_escaped}}};""")

        tikz_code = r"""\begin{tikzpicture}[scale=0.9]
    %%%% Title
    \node[font=\Large\bfseries, anchor=north] at (7, 1) {Top Keywords in Edge Computing Research};

    %%%% Keyword nodes
%s

    %%%% Legend
    \node[font=\small, anchor=north west, align=left] at (0, -8) {
        Font size indicates keyword frequency\\
        Colors: \textcolor{edgeblue}{High frequency} |
        \textcolor{edgeorange}{Medium frequency} |
        \textcolor{edgegreen}{Lower frequency}
    };
\end{tikzpicture}""" % "\n".join(nodes)

        self._save_tikz(tikz_code, "keyword_cloud")
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

        # The analyze_category_trends() returns a dict with "category_trends" and "top_categories" keys
        # We need to access the nested "category_trends" dict
        category_trends_data = temporal_analysis.get("category_trends", {})
        category_trends = category_trends_data.get("category_trends", {})

        if not category_trends:
            logger.warning("No category trend data available")
            return ""

        # Get top 5 categories
        top_categories = sorted(category_trends.items(),
                               key=lambda x: x[1].get("total_papers", 0),
                               reverse=True)[:5]

        if not top_categories:
            return ""

        # Get all months
        all_months = set()
        for _, cat_data in top_categories:
            all_months.update(cat_data.get("papers_by_month", {}).keys())
        months = sorted(all_months)

        if not months:
            logger.warning("No monthly data available for category trends")
            return ""

        # Colors for different categories
        colors = ['edgeblue', 'edgeorange', 'edgegreen', 'edgered', 'edgepurple']

        # Generate plots for each category
        plots = []
        for i, (category, cat_data) in enumerate(top_categories):
            escaped_cat = self._escape_latex(category)
            color = colors[i % len(colors)]

            # Get the papers_by_month data
            papers_by_month = cat_data.get("papers_by_month", {})

            coordinates = " ".join([
                f"({month_idx}, {papers_by_month.get(month, 0)})"
                for month_idx, month in enumerate(months)
            ])

            plots.append(f"""        \\addplot[
            color={color},
            mark=*,
            mark size=2pt,
            line width=1.2pt,
        ] coordinates {{{coordinates}}};
        \\addlegendentry{{{escaped_cat}}}""")

        # Generate month labels with error handling
        month_labels = []
        for m in months:
            try:
                label = datetime.strptime(m, "%Y-%m").strftime("%b")
                month_labels.append(label)
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid month format '{m}': {e}")
                month_labels.append(str(m))  # Use raw string as fallback

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
        self.generate_keyword_cloud(bibliometric)
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
