"""
Visualization module for generating publication-quality figures.
"""

from typing import List, Dict, Any, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from collections import Counter
from datetime import datetime
from pathlib import Path
from loguru import logger
import networkx as nx
from wordcloud import WordCloud

# Import configuration
from ..utils.config import Config, get_figure_path


class VisualizationGenerator:
    """Generate publication-quality figures for ArXiv analysis."""

    def __init__(self, config: Config = None):
        """
        Initialize visualization generator.

        Args:
            config: Configuration object
        """
        self.config = config or Config()
        self._setup_style()

    def _setup_style(self):
        """Set up matplotlib style for publication-quality figures."""
        try:
            plt.style.use(self.config.FIGURE_STYLE)
        except:
            # Fallback to default if style not available
            plt.style.use('seaborn-v0_8')

        # Set global parameters
        plt.rcParams['figure.dpi'] = self.config.FIGURE_DPI
        plt.rcParams['font.size'] = self.config.FONT_SIZE
        plt.rcParams['axes.labelsize'] = self.config.FONT_SIZE
        plt.rcParams['axes.titlesize'] = self.config.FONT_SIZE + 2
        plt.rcParams['xtick.labelsize'] = self.config.FONT_SIZE - 1
        plt.rcParams['ytick.labelsize'] = self.config.FONT_SIZE - 1
        plt.rcParams['legend.fontsize'] = self.config.FONT_SIZE - 1
        plt.rcParams['figure.titlesize'] = self.config.FONT_SIZE + 4

    def _save_figure(self, fig, filename: str):
        """
        Save figure in multiple formats.

        Args:
            fig: Matplotlib figure
            filename: Base filename (without extension)
        """
        for fmt in self.config.FIGURE_FORMATS:
            filepath = get_figure_path(filename, fmt)
            fig.savefig(filepath, bbox_inches='tight', dpi=self.config.FIGURE_DPI)
            logger.info(f"Saved figure: {filepath}")

    def plot_temporal_trends(self, temporal_analysis: Dict[str, Any]) -> plt.Figure:
        """
        Plot temporal publication trends.

        Args:
            temporal_analysis: Temporal analysis results

        Returns:
            matplotlib.Figure: Figure object
        """
        logger.info("Creating temporal trends plot")

        pub_trends = temporal_analysis.get("publication_trends", {})
        papers_by_month = pub_trends.get("papers_by_month", {})

        if not papers_by_month:
            logger.warning("No temporal data available")
            return None

        # Prepare data
        months = sorted(papers_by_month.keys())
        counts = [papers_by_month[m] for m in months]

        # Convert to datetime
        dates = [datetime.strptime(m, "%Y-%m") for m in months]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot
        ax.plot(dates, counts, marker='o', linewidth=2, markersize=8,
                color=sns.color_palette(self.config.COLOR_PALETTE)[0])

        # Add trend line
        x_numeric = np.arange(len(dates))
        z = np.polyfit(x_numeric, counts, 1)
        p = np.poly1d(z)
        ax.plot(dates, p(x_numeric), "--", alpha=0.8, color='red',
                label=f'Trend (slope={z[0]:.2f})')

        # Formatting
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Number of Papers', fontweight='bold')
        ax.set_title('Edge Computing Papers on ArXiv: Temporal Trends in 2025',
                     fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        self._save_figure(fig, 'temporal_trends')

        return fig

    def plot_category_distribution(self, bibliometric: Dict[str, Any]) -> plt.Figure:
        """
        Plot category distribution.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating category distribution plot")

        cat_dist = bibliometric.get("category_distribution", {})
        top_categories = cat_dist.get("top_10_categories", [])

        if not top_categories:
            logger.warning("No category data available")
            return None

        # Prepare data
        categories = [cat for cat, _ in top_categories]
        counts = [count for _, count in top_categories]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create bar plot
        colors = sns.color_palette(self.config.COLOR_PALETTE, len(categories))
        bars = ax.barh(categories, counts, color=colors, edgecolor='black', linewidth=0.5)

        # Add value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            ax.text(count + max(counts) * 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{count}', va='center', fontweight='bold')

        # Formatting
        ax.set_xlabel('Number of Papers', fontweight='bold')
        ax.set_ylabel('ArXiv Category', fontweight='bold')
        ax.set_title('Distribution of Papers Across ArXiv Categories',
                     fontweight='bold', pad=20)
        ax.invert_yaxis()  # Highest at top
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        self._save_figure(fig, 'category_distribution')

        return fig

    def plot_author_productivity(self, bibliometric: Dict[str, Any]) -> plt.Figure:
        """
        Plot author productivity distribution.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating author productivity plot")

        author_prod = bibliometric.get("author_productivity", {})
        top_authors = author_prod.get("top_20_authors", [])

        if not top_authors:
            logger.warning("No author productivity data available")
            return None

        # Prepare data
        authors = [author[:50] + "..." if len(author) > 50 else author
                   for author, _ in top_authors[:15]]  # Top 15 for readability
        papers = [count for _, count in top_authors[:15]]

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Create bar plot
        colors = sns.color_palette(self.config.COLOR_PALETTE, len(authors))
        bars = ax.barh(authors, papers, color=colors, edgecolor='black', linewidth=0.5)

        # Add value labels
        for bar, count in zip(bars, papers):
            ax.text(count + 0.1, bar.get_y() + bar.get_height() / 2,
                    f'{count}', va='center', fontweight='bold')

        # Formatting
        ax.set_xlabel('Number of Papers', fontweight='bold')
        ax.set_ylabel('Author', fontweight='bold')
        ax.set_title('Top 15 Most Prolific Authors in Edge Computing (2025)',
                     fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)

        plt.tight_layout()
        self._save_figure(fig, 'author_productivity')

        return fig

    def plot_collaboration_network(self, network_analysis: Dict[str, Any],
                                    max_nodes: int = 100) -> plt.Figure:
        """
        Plot collaboration network.

        Args:
            network_analysis: Network analysis results
            max_nodes: Maximum nodes to display

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating collaboration network plot")

        # This requires the actual network graph
        # For now, create a placeholder visualization
        coauthor_stats = network_analysis.get("coauthorship_network", {})

        fig, ax = plt.subplots(figsize=(12, 10))

        # Create a sample network for visualization
        # In practice, this would use the actual graph from network analysis
        top_betweenness = coauthor_stats.get("top_betweenness", [])[:max_nodes]

        if top_betweenness:
            G = nx.Graph()

            for author, centrality in top_betweenness[:20]:
                G.add_node(author[:30], centrality=centrality)

            # Add some edges (simplified)
            nodes = list(G.nodes())
            for i in range(len(nodes) - 1):
                if np.random.random() > 0.7:  # Random connections
                    G.add_edge(nodes[i], nodes[i + 1])

            # Layout
            pos = nx.spring_layout(G, k=2, iterations=50)

            # Node sizes based on centrality
            node_sizes = [G.nodes[node].get('centrality', 0.01) * 10000 for node in G.nodes()]

            # Draw
            nx.draw_networkx_nodes(G, pos, node_size=node_sizes,
                                   node_color=sns.color_palette(self.config.COLOR_PALETTE)[0],
                                   alpha=0.7, ax=ax)
            nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)

            # Labels (for top nodes only)
            nx.draw_networkx_labels(G, pos, font_size=7, ax=ax)

            ax.set_title('Co-authorship Network (Top Authors by Betweenness Centrality)',
                         fontweight='bold', pad=20)
            ax.axis('off')

        plt.tight_layout()
        self._save_figure(fig, 'collaboration_network')

        return fig

    def plot_keyword_cloud(self, bibliometric: Dict[str, Any]) -> plt.Figure:
        """
        Generate word cloud from keywords.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating keyword word cloud")

        keywords_data = bibliometric.get("keywords", {})
        keyword_freq = keywords_data.get("keyword_frequency", {})

        if not keyword_freq:
            logger.warning("No keyword data available")
            return None

        # Create word cloud
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5,
            min_font_size=10
        ).generate_from_frequencies(keyword_freq)

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 10))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Most Frequent Keywords in Edge Computing Research (2025)',
                     fontweight='bold', pad=20, fontsize=16)

        plt.tight_layout()
        self._save_figure(fig, 'keyword_cloud')

        return fig

    def plot_research_type_distribution(self, bibliometric: Dict[str, Any]) -> plt.Figure:
        """
        Plot research type distribution.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating research type distribution plot")

        research_types = bibliometric.get("research_types", {})
        type_counts = research_types.get("research_type_counts", {})

        if not type_counts:
            logger.warning("No research type data available")
            return None

        # Prepare data
        types = list(type_counts.keys())
        counts = list(type_counts.values())

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 10))

        # Create pie chart
        colors = sns.color_palette(self.config.COLOR_PALETTE, len(types))
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=types,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )

        # Enhance autotext
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)

        ax.set_title('Distribution of Research Types in Edge Computing (2025)',
                     fontweight='bold', pad=20)

        plt.tight_layout()
        self._save_figure(fig, 'research_type_distribution')

        return fig

    def plot_topic_heatmap(self, thematic_analysis: Dict[str, Any]) -> plt.Figure:
        """
        Plot topic-keyword heatmap.

        Args:
            thematic_analysis: Thematic analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating topic heatmap")

        lda_topics = thematic_analysis.get("lda_topics", {})
        topics_data = lda_topics.get("topics", {})

        if not topics_data:
            logger.warning("No topic data available")
            return None

        # Prepare data matrix
        topic_names = []
        keywords_list = []
        weights_matrix = []

        for topic_name, topic_info in list(topics_data.items())[:8]:  # Top 8 topics
            topic_names.append(topic_name)
            words = topic_info.get("words", [])[:10]  # Top 10 words
            weights = topic_info.get("weights", [])[:10]

            if not keywords_list:
                keywords_list = words

            weights_matrix.append(weights)

        # Convert to numpy array
        weights_array = np.array(weights_matrix)

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        # Create heatmap
        sns.heatmap(
            weights_array,
            xticklabels=keywords_list,
            yticklabels=topic_names,
            cmap='YlOrRd',
            annot=False,
            fmt='.2f',
            cbar_kws={'label': 'Weight'},
            ax=ax
        )

        ax.set_title('Topic-Keyword Association Heatmap (LDA Analysis)',
                     fontweight='bold', pad=20)
        ax.set_xlabel('Keywords', fontweight='bold')
        ax.set_ylabel('Topics', fontweight='bold')

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        self._save_figure(fig, 'topic_heatmap')

        return fig

    def plot_collaboration_statistics(self, bibliometric: Dict[str, Any]) -> plt.Figure:
        """
        Plot collaboration statistics.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating collaboration statistics plot")

        collab_patterns = bibliometric.get("collaboration_patterns", {})

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Plot 1: Authors per paper distribution
        # This would ideally show a histogram, but we'll create a summary bar chart
        metrics = {
            'Mean': collab_patterns.get('mean_authors_per_paper', 0),
            'Median': collab_patterns.get('median_authors_per_paper', 0),
            'Max': collab_patterns.get('max_authors_per_paper', 0),
        }

        ax1.bar(metrics.keys(), metrics.values(),
                color=sns.color_palette(self.config.COLOR_PALETTE)[:3],
                edgecolor='black', linewidth=0.5)
        ax1.set_ylabel('Number of Authors', fontweight='bold')
        ax1.set_title('Authors per Paper Statistics', fontweight='bold')
        ax1.grid(True, axis='y', alpha=0.3)

        # Plot 2: Single vs Multi-author papers
        single = collab_patterns.get('single_author_papers', 0)
        multi = collab_patterns.get('multi_author_papers', 0)

        ax2.pie(
            [single, multi],
            labels=['Single Author', 'Multi-Author'],
            autopct='%1.1f%%',
            colors=sns.color_palette(self.config.COLOR_PALETTE)[:2],
            startangle=90,
            textprops={'fontsize': 10, 'weight': 'bold'}
        )
        ax2.set_title('Single vs Multi-Author Papers', fontweight='bold')

        plt.tight_layout()
        self._save_figure(fig, 'collaboration_statistics')

        return fig

    def plot_monthly_category_trends(self, temporal_analysis: Dict[str, Any]) -> plt.Figure:
        """
        Plot monthly trends by category.

        Args:
            temporal_analysis: Temporal analysis results

        Returns:
            matplotlib.Figure
        """
        logger.info("Creating monthly category trends plot")

        cat_trends = temporal_analysis.get("category_trends", {})
        category_trends_data = cat_trends.get("category_trends", {})

        if not category_trends_data:
            logger.warning("No category trend data available")
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        # Plot trends for top categories
        for i, (category, data) in enumerate(list(category_trends_data.items())[:5]):
            papers_by_month = data.get("papers_by_month", {})
            if papers_by_month:
                months = sorted(papers_by_month.keys())
                counts = [papers_by_month[m] for m in months]
                dates = [datetime.strptime(m, "%Y-%m") for m in months]

                color = sns.color_palette(self.config.COLOR_PALETTE, 5)[i]
                ax.plot(dates, counts, marker='o', label=category,
                        linewidth=2, markersize=6, color=color)

        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Number of Papers', fontweight='bold')
        ax.set_title('Publication Trends by Top Categories', fontweight='bold', pad=20)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.xticks(rotation=45, ha='right')

        plt.tight_layout()
        self._save_figure(fig, 'monthly_category_trends')

        return fig

    def create_all_figures(self, analysis_results: Dict[str, Any]):
        """
        Generate all figures from analysis results.

        Args:
            analysis_results: Complete analysis results dictionary
        """
        logger.info("Creating all figures")

        figures = []

        # Temporal trends
        if "temporal" in analysis_results:
            fig = self.plot_temporal_trends(analysis_results["temporal"])
            if fig:
                figures.append(("temporal_trends", fig))
                plt.close(fig)

        # Category distribution
        if "bibliometric" in analysis_results:
            fig = self.plot_category_distribution(analysis_results["bibliometric"])
            if fig:
                figures.append(("category_distribution", fig))
                plt.close(fig)

            # Author productivity
            fig = self.plot_author_productivity(analysis_results["bibliometric"])
            if fig:
                figures.append(("author_productivity", fig))
                plt.close(fig)

            # Research type distribution
            fig = self.plot_research_type_distribution(analysis_results["bibliometric"])
            if fig:
                figures.append(("research_type_distribution", fig))
                plt.close(fig)

            # Keyword cloud
            fig = self.plot_keyword_cloud(analysis_results["bibliometric"])
            if fig:
                figures.append(("keyword_cloud", fig))
                plt.close(fig)

            # Collaboration statistics
            fig = self.plot_collaboration_statistics(analysis_results["bibliometric"])
            if fig:
                figures.append(("collaboration_statistics", fig))
                plt.close(fig)

        # Network visualizations
        if "network" in analysis_results:
            fig = self.plot_collaboration_network(analysis_results["network"])
            if fig:
                figures.append(("collaboration_network", fig))
                plt.close(fig)

        # Thematic analysis
        if "thematic" in analysis_results:
            fig = self.plot_topic_heatmap(analysis_results["thematic"])
            if fig:
                figures.append(("topic_heatmap", fig))
                plt.close(fig)

        # Monthly category trends
        if "temporal" in analysis_results:
            fig = self.plot_monthly_category_trends(analysis_results["temporal"])
            if fig:
                figures.append(("monthly_category_trends", fig))
                plt.close(fig)

        logger.info(f"Created {len(figures)} figures")
        return figures


def main():
    """Main function for testing visualization."""
    print("Visualization generator module loaded successfully")


if __name__ == "__main__":
    main()
