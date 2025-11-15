"""
LaTeX table generation module.
"""

from typing import List, Dict, Any
import pandas as pd
from loguru import logger
from ..utils.config import get_table_path


class TableGenerator:
    """Generate LaTeX tables for paper."""

    def __init__(self):
        """Initialize table generator."""
        pass

    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters.

        Args:
            text: Input text

        Returns:
            str: Escaped text
        """
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
            '\\': r'\textbackslash{}',
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def generate_top_authors_table(self, bibliometric: Dict[str, Any],
                                    top_n: int = 15) -> str:
        """
        Generate table of top authors.

        Args:
            bibliometric: Bibliometric analysis results
            top_n: Number of top authors to include

        Returns:
            str: LaTeX table code
        """
        logger.info(f"Generating top {top_n} authors table")

        author_prod = bibliometric.get("author_productivity", {})
        top_authors = author_prod.get("top_20_authors", [])[:top_n]

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Top " + str(top_n) + r" Most Prolific Authors in Edge Computing (2025)}")
        latex.append(r"\label{tab:top_authors}")
        latex.append(r"\begin{tabular}{clc}")
        latex.append(r"\toprule")
        latex.append(r"Rank & Author & Papers \\")
        latex.append(r"\midrule")

        for rank, (author, count) in enumerate(top_authors, 1):
            escaped_author = self._escape_latex(author)
            # Truncate long names
            if len(escaped_author) > 40:
                escaped_author = escaped_author[:37] + "..."
            latex.append(f"{rank} & {escaped_author} & {count} \\\\")

        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("top_authors")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved top authors table to {output_file}")
        return table_str

    def generate_category_distribution_table(self, bibliometric: Dict[str, Any],
                                              top_n: int = 10) -> str:
        """
        Generate category distribution table.

        Args:
            bibliometric: Bibliometric analysis results
            top_n: Number of categories to include

        Returns:
            str: LaTeX table code
        """
        logger.info(f"Generating category distribution table")

        cat_dist = bibliometric.get("category_distribution", {})
        top_categories = cat_dist.get("top_10_categories", [])[:top_n]
        total_papers = bibliometric.get("summary", {}).get("total_papers", 0)

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Distribution of Papers Across ArXiv Categories}")
        latex.append(r"\label{tab:category_distribution}")
        latex.append(r"\begin{tabular}{clcc}")
        latex.append(r"\toprule")
        latex.append(r"Rank & Category & Papers & Percentage \\")
        latex.append(r"\midrule")

        for rank, (category, count) in enumerate(top_categories, 1):
            percentage = (count / total_papers * 100) if total_papers > 0 else 0
            escaped_cat = self._escape_latex(category)
            latex.append(f"{rank} & {escaped_cat} & {count} & {percentage:.1f}\\% \\\\")

        latex.append(r"\midrule")
        latex.append(f"& \\textbf{{Total}} & \\textbf{{{total_papers}}} & \\textbf{{100.0}}\\% \\\\")
        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("category_distribution")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved category distribution table to {output_file}")
        return table_str

    def generate_keyword_frequency_table(self, bibliometric: Dict[str, Any],
                                          top_n: int = 20) -> str:
        """
        Generate keyword frequency table.

        Args:
            bibliometric: Bibliometric analysis results
            top_n: Number of keywords to include

        Returns:
            str: LaTeX table code
        """
        logger.info(f"Generating keyword frequency table")

        keywords_data = bibliometric.get("keywords", {})
        top_keywords = keywords_data.get("top_20_keywords", [])[:top_n]

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Most Frequent Keywords in Edge Computing Research (2025)}")
        latex.append(r"\label{tab:keyword_frequency}")
        latex.append(r"\begin{tabular}{clc}")
        latex.append(r"\toprule")
        latex.append(r"Rank & Keyword & Frequency \\")
        latex.append(r"\midrule")

        for rank, (keyword, count) in enumerate(top_keywords, 1):
            escaped_kw = self._escape_latex(keyword)
            latex.append(f"{rank} & {escaped_kw} & {count} \\\\")

        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("keyword_frequency")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved keyword frequency table to {output_file}")
        return table_str

    def generate_statistical_summary_table(self, statistical: Dict[str, Any]) -> str:
        """
        Generate statistical summary table.

        Args:
            statistical: Statistical analysis results

        Returns:
            str: LaTeX table code
        """
        logger.info("Generating statistical summary table")

        desc_stats = statistical.get("descriptive_statistics", {})

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Descriptive Statistics of Edge Computing Papers (2025)}")
        latex.append(r"\label{tab:statistical_summary}")
        latex.append(r"\begin{tabular}{lcc}")
        latex.append(r"\toprule")
        latex.append(r"Metric & Mean & Std. Dev. \\")
        latex.append(r"\midrule")

        # Authors per paper
        authors_stats = desc_stats.get("authors_per_paper", {})
        latex.append(f"Authors per Paper & {authors_stats.get('mean', 0):.2f} & "
                     f"{authors_stats.get('std', 0):.2f} \\\\")

        # Abstract length
        abstract_stats = desc_stats.get("abstract_length", {})
        latex.append(f"Abstract Length (chars) & {abstract_stats.get('mean', 0):.0f} & "
                     f"{abstract_stats.get('std', 0):.0f} \\\\")

        # Title length
        title_stats = desc_stats.get("title_length", {})
        latex.append(f"Title Length (chars) & {title_stats.get('mean', 0):.0f} & "
                     f"{title_stats.get('std', 0):.0f} \\\\")

        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("statistical_summary")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved statistical summary table to {output_file}")
        return table_str

    def generate_research_type_table(self, bibliometric: Dict[str, Any]) -> str:
        """
        Generate research type distribution table.

        Args:
            bibliometric: Bibliometric analysis results

        Returns:
            str: LaTeX table code
        """
        logger.info("Generating research type table")

        research_types = bibliometric.get("research_types", {})
        type_counts = research_types.get("research_type_counts", {})
        type_percentages = research_types.get("research_type_percentages", {})

        # Sort by count
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Distribution of Research Types in Edge Computing (2025)}")
        latex.append(r"\label{tab:research_types}")
        latex.append(r"\begin{tabular}{lcc}")
        latex.append(r"\toprule")
        latex.append(r"Research Type & Papers & Percentage \\")
        latex.append(r"\midrule")

        total = sum(type_counts.values())
        for rtype, count in sorted_types:
            percentage = type_percentages.get(rtype, 0)
            escaped_type = self._escape_latex(rtype)
            latex.append(f"{escaped_type} & {count} & {percentage:.1f}\\% \\\\")

        latex.append(r"\midrule")
        latex.append(f"\\textbf{{Total}} & \\textbf{{{total}}} & \\textbf{{100.0}}\\% \\\\")
        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("research_types")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved research type table to {output_file}")
        return table_str

    def generate_lda_topics_table(self, thematic: Dict[str, Any],
                                   top_n: int = 8) -> str:
        """
        Generate LDA topics table.

        Args:
            thematic: Thematic analysis results
            top_n: Number of topics to include

        Returns:
            str: LaTeX table code
        """
        logger.info("Generating LDA topics table")

        lda_topics = thematic.get("lda_topics", {})
        topics_data = lda_topics.get("topics", {})

        latex = []
        latex.append(r"\begin{table}[htbp]")
        latex.append(r"\centering")
        latex.append(r"\caption{Discovered Research Topics Using LDA Analysis}")
        latex.append(r"\label{tab:lda_topics}")
        latex.append(r"\begin{tabular}{cp{10cm}}")
        latex.append(r"\toprule")
        latex.append(r"Topic & Top Keywords \\")
        latex.append(r"\midrule")

        for topic_name, topic_info in list(topics_data.items())[:top_n]:
            top_words = topic_info.get("top_5_words", [])
            keywords_str = ", ".join([self._escape_latex(w) for w in top_words])
            escaped_name = self._escape_latex(topic_name)
            latex.append(f"{escaped_name} & {keywords_str} \\\\")

        latex.append(r"\bottomrule")
        latex.append(r"\end{tabular}")
        latex.append(r"\end{table}")

        table_str = "\n".join(latex)

        # Save to file
        output_file = get_table_path("lda_topics")
        with open(output_file, 'w') as f:
            f.write(table_str)

        logger.info(f"Saved LDA topics table to {output_file}")
        return table_str

    def generate_all_tables(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generate all LaTeX tables.

        Args:
            analysis_results: Complete analysis results

        Returns:
            list: List of generated table LaTeX code
        """
        logger.info("Generating all tables")

        tables = []

        if "bibliometric" in analysis_results:
            tables.append(self.generate_top_authors_table(analysis_results["bibliometric"]))
            tables.append(self.generate_category_distribution_table(analysis_results["bibliometric"]))
            tables.append(self.generate_keyword_frequency_table(analysis_results["bibliometric"]))
            tables.append(self.generate_research_type_table(analysis_results["bibliometric"]))

        if "statistical" in analysis_results:
            tables.append(self.generate_statistical_summary_table(analysis_results["statistical"]))

        if "thematic" in analysis_results:
            tables.append(self.generate_lda_topics_table(analysis_results["thematic"]))

        logger.info(f"Generated {len(tables)} tables")
        return tables


def main():
    """Main function for testing table generation."""
    print("Table generator module loaded successfully")


if __name__ == "__main__":
    main()
