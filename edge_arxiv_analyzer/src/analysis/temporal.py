"""
Temporal analysis module for time-series analysis of publications.
"""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from loguru import logger


class TemporalAnalyzer:
    """Perform temporal analysis on ArXiv papers."""

    def __init__(self, papers: List[Dict[str, Any]]):
        """
        Initialize temporal analyzer.

        Args:
            papers: List of paper dictionaries
        """
        self.papers = papers
        self.df = self._create_dataframe()

    def _create_dataframe(self) -> pd.DataFrame:
        """Create pandas DataFrame with temporal data."""
        data = []
        for paper in self.papers:
            data.append({
                "arxiv_id": paper.get("arxiv_id"),
                "title": paper.get("title"),
                "published": paper.get("published"),
                "year": paper.get("year"),
                "month": paper.get("month"),
                "primary_category": paper.get("primary_category"),
                "research_type": paper.get("research_type", "Other"),
            })

        df = pd.DataFrame(data)
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"])
            df["week"] = df["published"].dt.isocalendar().week
            df["day_of_year"] = df["published"].dt.dayofyear

        return df

    def analyze_publication_trends(self) -> Dict[str, Any]:
        """
        Analyze publication trends over time.

        Returns:
            dict: Publication trend statistics
        """
        logger.info("Analyzing publication trends")

        # Papers per month
        papers_by_month = self.df.groupby(["year", "month"]).size().to_dict()

        # Papers per week
        if "published" in self.df.columns:
            self.df["year_week"] = self.df["published"].dt.strftime("%Y-%W")
            papers_by_week = self.df.groupby("year_week").size().to_dict()
        else:
            papers_by_week = {}

        # Calculate growth trends
        monthly_counts = sorted(papers_by_month.items())
        if len(monthly_counts) > 1:
            # Simple linear trend
            x = np.arange(len(monthly_counts))
            y = np.array([count for _, count in monthly_counts])
            if len(y) > 0:
                trend_slope = np.polyfit(x, y, 1)[0] if len(y) > 1 else 0
            else:
                trend_slope = 0
        else:
            trend_slope = 0

        stats = {
            "papers_by_month": {f"{y}-{m:02d}": count for (y, m), count in papers_by_month.items()},
            "papers_by_week": papers_by_week,
            "total_papers": len(self.papers),
            "trend_slope": float(trend_slope),
            "trend_direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
        }

        # Find peak months
        if papers_by_month:
            peak_month = max(papers_by_month.items(), key=lambda x: x[1])
            stats["peak_month"] = {
                "period": f"{peak_month[0][0]}-{peak_month[0][1]:02d}",
                "count": peak_month[1],
            }

        logger.info(f"Publication trend: {stats['trend_direction']}")
        return stats

    def analyze_seasonal_patterns(self) -> Dict[str, Any]:
        """
        Analyze seasonal patterns in publications.

        Returns:
            dict: Seasonal pattern statistics
        """
        logger.info("Analyzing seasonal patterns")

        if "month" not in self.df.columns or self.df["month"].isna().all():
            logger.warning("No month data available for seasonal analysis")
            return {}

        # Papers by month of year (aggregated across years)
        papers_by_month_of_year = self.df.groupby("month").size().to_dict()

        # Papers by quarter
        self.df["quarter"] = ((self.df["month"] - 1) // 3) + 1
        papers_by_quarter = self.df.groupby("quarter").size().to_dict()

        # Calculate seasonality index
        mean_monthly = np.mean(list(papers_by_month_of_year.values()))
        seasonality_index = {
            month: (count / mean_monthly - 1) * 100
            for month, count in papers_by_month_of_year.items()
        }

        stats = {
            "papers_by_month_of_year": papers_by_month_of_year,
            "papers_by_quarter": papers_by_quarter,
            "seasonality_index": seasonality_index,
            "most_active_month": max(papers_by_month_of_year.items(), key=lambda x: x[1])[0] if papers_by_month_of_year else None,
            "least_active_month": min(papers_by_month_of_year.items(), key=lambda x: x[1])[0] if papers_by_month_of_year else None,
        }

        logger.info(f"Most active month: {stats.get('most_active_month')}")
        return stats

    def analyze_category_trends(self) -> Dict[str, Any]:
        """
        Analyze how different categories trend over time.

        Returns:
            dict: Category trend statistics
        """
        logger.info("Analyzing category trends over time")

        if "primary_category" not in self.df.columns:
            logger.warning("No category data available")
            return {}

        # Get top categories
        top_categories = self.df["primary_category"].value_counts().head(10).index.tolist()

        category_trends = {}
        for category in top_categories:
            cat_df = self.df[self.df["primary_category"] == category]
            by_month = cat_df.groupby(["year", "month"]).size().to_dict()

            category_trends[category] = {
                "total_papers": len(cat_df),
                "papers_by_month": {f"{y}-{m:02d}": count for (y, m), count in by_month.items()},
            }

        stats = {
            "category_trends": category_trends,
            "top_categories": top_categories,
        }

        logger.info(f"Analyzed trends for {len(top_categories)} categories")
        return stats

    def analyze_research_type_evolution(self) -> Dict[str, Any]:
        """
        Analyze how research types evolve over time.

        Returns:
            dict: Research type evolution statistics
        """
        logger.info("Analyzing research type evolution")

        if "research_type" not in self.df.columns:
            logger.warning("No research type data available")
            return {}

        research_type_trends = {}
        research_types = self.df["research_type"].unique()

        for rtype in research_types:
            rtype_df = self.df[self.df["research_type"] == rtype]
            by_month = rtype_df.groupby(["year", "month"]).size().to_dict()

            research_type_trends[rtype] = {
                "total_papers": len(rtype_df),
                "papers_by_month": {f"{y}-{m:02d}": count for (y, m), count in by_month.items()},
            }

        stats = {
            "research_type_trends": research_type_trends,
            "research_types": list(research_types),
        }

        logger.info(f"Analyzed evolution of {len(research_types)} research types")
        return stats

    def forecast_trends(self, periods: int = 6) -> Dict[str, Any]:
        """
        Simple forecast of publication trends.

        Args:
            periods: Number of periods to forecast

        Returns:
            dict: Forecast statistics
        """
        logger.info(f"Forecasting trends for {periods} periods")

        # Get monthly counts as time series
        monthly_data = self.df.groupby(["year", "month"]).size().reset_index(name="count")

        if len(monthly_data) < 3:
            logger.warning("Insufficient data for forecasting")
            return {"forecast": [], "method": "insufficient_data"}

        # Simple linear extrapolation
        x = np.arange(len(monthly_data))
        y = monthly_data["count"].values

        # Fit linear trend
        coeffs = np.polyfit(x, y, 1)
        trend_line = np.poly1d(coeffs)

        # Forecast
        future_x = np.arange(len(monthly_data), len(monthly_data) + periods)
        forecast_values = trend_line(future_x)

        # Ensure non-negative forecasts
        forecast_values = np.maximum(forecast_values, 0)

        stats = {
            "forecast": forecast_values.tolist(),
            "method": "linear_extrapolation",
            "trend_coefficient": float(coeffs[0]),
            "intercept": float(coeffs[1]),
        }

        logger.info("Trend forecasting complete")
        return stats

    def calculate_growth_metrics(self) -> Dict[str, Any]:
        """
        Calculate various growth metrics.

        Returns:
            dict: Growth metrics
        """
        logger.info("Calculating growth metrics")

        monthly_data = self.df.groupby(["year", "month"]).size().reset_index(name="count")

        if len(monthly_data) < 2:
            logger.warning("Insufficient data for growth metrics")
            return {}

        counts = monthly_data["count"].values

        # Calculate month-over-month growth
        mom_growth = []
        for i in range(1, len(counts)):
            if counts[i - 1] > 0:
                growth = ((counts[i] - counts[i - 1]) / counts[i - 1]) * 100
                mom_growth.append(growth)

        stats = {
            "average_monthly_growth": float(np.mean(mom_growth)) if mom_growth else 0,
            "median_monthly_growth": float(np.median(mom_growth)) if mom_growth else 0,
            "max_monthly_growth": float(np.max(mom_growth)) if mom_growth else 0,
            "min_monthly_growth": float(np.min(mom_growth)) if mom_growth else 0,
            "volatility": float(np.std(mom_growth)) if mom_growth else 0,
        }

        logger.info(f"Average monthly growth: {stats['average_monthly_growth']:.2f}%")
        return stats

    def generate_temporal_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive temporal analysis.

        Returns:
            dict: Complete temporal analysis
        """
        logger.info("Generating comprehensive temporal analysis")

        analysis = {
            "publication_trends": self.analyze_publication_trends(),
            "seasonal_patterns": self.analyze_seasonal_patterns(),
            "category_trends": self.analyze_category_trends(),
            "research_type_evolution": self.analyze_research_type_evolution(),
            "growth_metrics": self.calculate_growth_metrics(),
            "forecast": self.forecast_trends(periods=6),
        }

        logger.info("Temporal analysis complete")
        return analysis


def main():
    """Main function for testing temporal analysis."""
    print("Temporal analyzer module loaded successfully")


if __name__ == "__main__":
    main()
