"""
Statistical analysis module for ArXiv papers.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from scipy import stats
from collections import Counter
from loguru import logger


class StatisticalAnalyzer:
    """Perform statistical analysis on ArXiv papers."""

    def __init__(self, papers: List[Dict[str, Any]]):
        """
        Initialize statistical analyzer.

        Args:
            papers: List of paper dictionaries
        """
        self.papers = papers
        self.df = self._create_dataframe()

    def _create_dataframe(self) -> pd.DataFrame:
        """Create pandas DataFrame for analysis."""
        from ..scraper.metadata_extractor import MetadataExtractor

        extractor = MetadataExtractor()
        return extractor.create_papers_dataframe(self.papers)

    def descriptive_statistics(self) -> Dict[str, Any]:
        """
        Calculate descriptive statistics.

        Returns:
            dict: Descriptive statistics
        """
        logger.info("Calculating descriptive statistics")

        # Author count statistics
        author_counts = [len(paper.get("authors", [])) for paper in self.papers]

        # Abstract length statistics
        abstract_lengths = [len(paper.get("abstract", "")) for paper in self.papers]

        # Title length statistics
        title_lengths = [len(paper.get("title", "")) for paper in self.papers]

        stats_dict = {
            "paper_count": {
                "total": len(self.papers),
            },
            "authors_per_paper": {
                "mean": float(np.mean(author_counts)) if author_counts else 0,
                "median": float(np.median(author_counts)) if author_counts else 0,
                "std": float(np.std(author_counts)) if author_counts else 0,
                "min": int(np.min(author_counts)) if author_counts else 0,
                "max": int(np.max(author_counts)) if author_counts else 0,
                "q25": float(np.percentile(author_counts, 25)) if author_counts else 0,
                "q75": float(np.percentile(author_counts, 75)) if author_counts else 0,
            },
            "abstract_length": {
                "mean": float(np.mean(abstract_lengths)) if abstract_lengths else 0,
                "median": float(np.median(abstract_lengths)) if abstract_lengths else 0,
                "std": float(np.std(abstract_lengths)) if abstract_lengths else 0,
                "min": int(np.min(abstract_lengths)) if abstract_lengths else 0,
                "max": int(np.max(abstract_lengths)) if abstract_lengths else 0,
            },
            "title_length": {
                "mean": float(np.mean(title_lengths)) if title_lengths else 0,
                "median": float(np.median(title_lengths)) if title_lengths else 0,
                "std": float(np.std(title_lengths)) if title_lengths else 0,
            },
        }

        logger.info("Descriptive statistics calculated")
        return stats_dict

    def correlation_analysis(self) -> Dict[str, Any]:
        """
        Analyze correlations between variables.

        Returns:
            dict: Correlation analysis results
        """
        logger.info("Performing correlation analysis")

        # Create numeric features for correlation
        numeric_data = []

        for paper in self.papers:
            numeric_data.append({
                "author_count": len(paper.get("authors", [])),
                "abstract_length": len(paper.get("abstract", "")),
                "title_length": len(paper.get("title", "")),
                "keyword_count": len(paper.get("keywords", [])),
                "category_count": len(paper.get("categories", [])),
            })

        df_numeric = pd.DataFrame(numeric_data)

        # Calculate correlation matrix
        corr_matrix = df_numeric.corr()

        # Find significant correlations
        significant_correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.3:  # Threshold for significance
                    significant_correlations.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": float(corr_value),
                    })

        stats_dict = {
            "correlation_matrix": corr_matrix.to_dict(),
            "significant_correlations": significant_correlations,
        }

        logger.info("Correlation analysis complete")
        return stats_dict

    def category_statistics(self) -> Dict[str, Any]:
        """
        Statistical analysis by category.

        Returns:
            dict: Category-based statistics
        """
        logger.info("Calculating category statistics")

        category_stats = {}

        # Get top categories
        all_categories = []
        for paper in self.papers:
            all_categories.extend(paper.get("categories", []))

        top_categories = [cat for cat, _ in Counter(all_categories).most_common(10)]

        # Calculate statistics for each category
        for category in top_categories:
            cat_papers = [
                paper for paper in self.papers
                if category in paper.get("categories", [])
            ]

            if not cat_papers:
                continue

            author_counts = [len(p.get("authors", [])) for p in cat_papers]

            category_stats[category] = {
                "n_papers": len(cat_papers),
                "mean_authors": float(np.mean(author_counts)) if author_counts else 0,
                "median_authors": float(np.median(author_counts)) if author_counts else 0,
            }

        logger.info(f"Calculated statistics for {len(category_stats)} categories")
        return category_stats

    def research_type_statistics(self) -> Dict[str, Any]:
        """
        Statistical analysis by research type.

        Returns:
            dict: Research type statistics
        """
        logger.info("Calculating research type statistics")

        research_type_stats = {}

        # Group by research type
        research_types = set(paper.get("research_type", "Other") for paper in self.papers)

        for rtype in research_types:
            rtype_papers = [
                paper for paper in self.papers
                if paper.get("research_type") == rtype
            ]

            if not rtype_papers:
                continue

            author_counts = [len(p.get("authors", [])) for p in rtype_papers]
            abstract_lengths = [len(p.get("abstract", "")) for p in rtype_papers]

            research_type_stats[rtype] = {
                "n_papers": len(rtype_papers),
                "percentage": (len(rtype_papers) / len(self.papers)) * 100,
                "mean_authors": float(np.mean(author_counts)) if author_counts else 0,
                "mean_abstract_length": float(np.mean(abstract_lengths)) if abstract_lengths else 0,
            }

        logger.info(f"Calculated statistics for {len(research_type_stats)} research types")
        return research_type_stats

    def hypothesis_testing(self) -> Dict[str, Any]:
        """
        Perform hypothesis tests.

        Returns:
            dict: Hypothesis testing results
        """
        logger.info("Performing hypothesis tests")

        results = {}

        # Test: Do Machine Learning papers have more authors than other types?
        ml_papers = [
            len(p.get("authors", [])) for p in self.papers
            if p.get("research_type") == "Machine Learning"
        ]
        other_papers = [
            len(p.get("authors", [])) for p in self.papers
            if p.get("research_type") != "Machine Learning"
        ]

        if ml_papers and other_papers:
            t_stat, p_value = stats.ttest_ind(ml_papers, other_papers)
            results["ml_vs_others_authors"] = {
                "test": "t-test",
                "hypothesis": "ML papers have different number of authors than others",
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "ml_mean": float(np.mean(ml_papers)),
                "others_mean": float(np.mean(other_papers)),
            }

        # Test: Chi-square for category distribution
        category_counts = Counter()
        for paper in self.papers:
            primary_cat = paper.get("primary_category")
            if primary_cat:
                category_counts[primary_cat] += 1

        if len(category_counts) > 1:
            observed = list(category_counts.values())
            # Expected: uniform distribution
            expected = [sum(observed) / len(observed)] * len(observed)

            chi2_stat, p_value = stats.chisquare(observed, expected)
            results["category_distribution"] = {
                "test": "chi-square",
                "hypothesis": "Categories are uniformly distributed",
                "chi2_statistic": float(chi2_stat),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
            }

        logger.info("Hypothesis testing complete")
        return results

    def trend_significance(self) -> Dict[str, Any]:
        """
        Test significance of temporal trends.

        Returns:
            dict: Trend significance tests
        """
        logger.info("Testing trend significance")

        if "month" not in self.df.columns:
            logger.warning("No temporal data available")
            return {}

        # Group by month and count papers
        monthly_counts = self.df.groupby(["year", "month"]).size().reset_index(name="count")

        if len(monthly_counts) < 3:
            logger.warning("Insufficient data for trend testing")
            return {}

        # Linear regression for trend
        x = np.arange(len(monthly_counts))
        y = monthly_counts["count"].values

        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        results = {
            "trend_test": {
                "slope": float(slope),
                "intercept": float(intercept),
                "r_squared": float(r_value ** 2),
                "p_value": float(p_value),
                "significant": p_value < 0.05,
                "std_error": float(std_err),
                "trend": "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable",
            }
        }

        logger.info("Trend significance testing complete")
        return results

    def outlier_detection(self) -> Dict[str, Any]:
        """
        Detect outliers in the dataset.

        Returns:
            dict: Outlier detection results
        """
        logger.info("Detecting outliers")

        # Detect papers with unusually high author counts
        author_counts = np.array([len(p.get("authors", [])) for p in self.papers])

        q1 = np.percentile(author_counts, 25)
        q3 = np.percentile(author_counts, 75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_papers = [
            {
                "arxiv_id": paper.get("arxiv_id"),
                "title": paper.get("title"),
                "author_count": len(paper.get("authors", [])),
            }
            for paper in self.papers
            if len(paper.get("authors", [])) > upper_bound or len(paper.get("authors", [])) < lower_bound
        ]

        results = {
            "author_count_outliers": {
                "n_outliers": len(outlier_papers),
                "outlier_papers": outlier_papers[:10],  # Top 10
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            }
        }

        logger.info(f"Found {len(outlier_papers)} outliers")
        return results

    def generate_statistical_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive statistical analysis.

        Returns:
            dict: Complete statistical analysis
        """
        logger.info("Generating comprehensive statistical analysis")

        analysis = {
            "descriptive_statistics": self.descriptive_statistics(),
            "correlation_analysis": self.correlation_analysis(),
            "category_statistics": self.category_statistics(),
            "research_type_statistics": self.research_type_statistics(),
            "hypothesis_testing": self.hypothesis_testing(),
            "trend_significance": self.trend_significance(),
            "outlier_detection": self.outlier_detection(),
        }

        logger.info("Statistical analysis complete")
        return analysis


def main():
    """Main function for testing statistical analysis."""
    print("Statistical analyzer module loaded successfully")


if __name__ == "__main__":
    main()
