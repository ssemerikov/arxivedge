"""
Thematic analysis module using NLP and topic modeling.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from collections import Counter
from loguru import logger

# NLP libraries
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Try to import sentence transformers for BERT-based analysis
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, BERT-based analysis will be skipped")


class ThematicAnalyzer:
    """Perform thematic analysis on ArXiv papers."""

    def __init__(self, papers: List[Dict[str, Any]]):
        """
        Initialize thematic analyzer.

        Args:
            papers: List of paper dictionaries
        """
        self.papers = papers
        self.stop_words = set(stopwords.words('english'))

        # Add domain-specific stop words
        self.stop_words.update([
            'paper', 'propose', 'proposed', 'show', 'present', 'study',
            'based', 'using', 'used', 'approach', 'method', 'result',
            'also', 'however', 'moreover', 'furthermore',
        ])

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for analysis.

        Args:
            text: Input text

        Returns:
            str: Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep spaces
        import re
        text = re.sub(r'[^a-z\s]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def extract_topics_lda(self, n_topics: int = 10, max_features: int = 1000) -> Dict[str, Any]:
        """
        Extract topics using Latent Dirichlet Allocation (LDA).

        Args:
            n_topics: Number of topics to extract
            max_features: Maximum number of features for vectorization

        Returns:
            dict: Topic modeling results
        """
        logger.info(f"Extracting {n_topics} topics using LDA")

        # Prepare documents (titles + abstracts)
        documents = [
            self.preprocess_text(f"{p.get('title', '')} {p.get('abstract', '')}")
            for p in self.papers
        ]

        # Vectorize
        vectorizer = CountVectorizer(
            max_features=max_features,
            stop_words='english',
            min_df=2,
            max_df=0.8,
        )

        doc_term_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()

        # LDA model
        lda_model = LatentDirichletAllocation(
            n_components=n_topics,
            random_state=42,
            max_iter=50,
            learning_method='online',
        )

        lda_output = lda_model.fit_transform(doc_term_matrix)

        # Extract top words for each topic
        n_top_words = 15
        topics = {}
        for topic_idx, topic in enumerate(lda_model.components_):
            top_words_idx = topic.argsort()[-n_top_words:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            top_weights = [topic[i] for i in top_words_idx]

            topics[f"Topic {topic_idx + 1}"] = {
                "words": top_words,
                "weights": top_weights,
                "top_5_words": top_words[:5],
            }

        # Assign topics to papers
        paper_topics = []
        for idx, paper in enumerate(self.papers):
            topic_dist = lda_output[idx]
            dominant_topic = topic_dist.argmax()
            paper_topics.append({
                "arxiv_id": paper.get("arxiv_id"),
                "title": paper.get("title"),
                "dominant_topic": dominant_topic + 1,
                "topic_probability": topic_dist[dominant_topic],
            })

        results = {
            "n_topics": n_topics,
            "topics": topics,
            "paper_topics": paper_topics,
            "model_perplexity": lda_model.perplexity(doc_term_matrix),
        }

        logger.info("LDA topic extraction complete")
        return results

    def extract_topics_nmf(self, n_topics: int = 10, max_features: int = 1000) -> Dict[str, Any]:
        """
        Extract topics using Non-negative Matrix Factorization (NMF).

        Args:
            n_topics: Number of topics to extract
            max_features: Maximum number of features

        Returns:
            dict: NMF topic modeling results
        """
        logger.info(f"Extracting {n_topics} topics using NMF")

        # Prepare documents
        documents = [
            self.preprocess_text(f"{p.get('title', '')} {p.get('abstract', '')}")
            for p in self.papers
        ]

        # TF-IDF vectorization
        vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            min_df=2,
            max_df=0.8,
        )

        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()

        # NMF model
        nmf_model = NMF(
            n_components=n_topics,
            random_state=42,
            max_iter=200,
        )

        nmf_output = nmf_model.fit_transform(tfidf_matrix)

        # Extract top words for each topic
        n_top_words = 15
        topics = {}
        for topic_idx, topic in enumerate(nmf_model.components_):
            top_words_idx = topic.argsort()[-n_top_words:][::-1]
            top_words = [feature_names[i] for i in top_words_idx]
            top_weights = [topic[i] for i in top_words_idx]

            topics[f"Topic {topic_idx + 1}"] = {
                "words": top_words,
                "weights": top_weights,
                "top_5_words": top_words[:5],
            }

        results = {
            "n_topics": n_topics,
            "topics": topics,
        }

        logger.info("NMF topic extraction complete")
        return results

    def cluster_abstracts(self, n_clusters: int = 8) -> Dict[str, Any]:
        """
        Cluster papers based on abstract similarity.

        Args:
            n_clusters: Number of clusters

        Returns:
            dict: Clustering results
        """
        logger.info(f"Clustering abstracts into {n_clusters} clusters")

        # Prepare documents
        documents = [
            self.preprocess_text(p.get('abstract', ''))
            for p in self.papers
        ]

        # Vectorize
        vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            min_df=2,
            max_df=0.8,
        )

        tfidf_matrix = vectorizer.fit_transform(documents)

        # K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(tfidf_matrix)

        # Analyze clusters
        clusters = {}
        for i in range(n_clusters):
            cluster_papers = [
                self.papers[j] for j, label in enumerate(cluster_labels) if label == i
            ]

            # Get representative keywords for cluster
            cluster_docs = [documents[j] for j, label in enumerate(cluster_labels) if label == i]
            if cluster_docs:
                cluster_vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
                cluster_vectorizer.fit(cluster_docs)
                keywords = cluster_vectorizer.get_feature_names_out().tolist()
            else:
                keywords = []

            clusters[f"Cluster {i + 1}"] = {
                "size": len(cluster_papers),
                "keywords": keywords,
                "sample_papers": [
                    {"title": p.get("title"), "arxiv_id": p.get("arxiv_id")}
                    for p in cluster_papers[:3]
                ],
            }

        results = {
            "n_clusters": n_clusters,
            "clusters": clusters,
            "cluster_labels": cluster_labels.tolist(),
        }

        logger.info("Abstract clustering complete")
        return results

    def identify_emerging_topics(self, min_frequency: int = 3) -> Dict[str, Any]:
        """
        Identify emerging topics by analyzing recent papers.

        Args:
            min_frequency: Minimum frequency for a topic to be considered

        Returns:
            dict: Emerging topics analysis
        """
        logger.info("Identifying emerging topics")

        # Sort papers by date
        sorted_papers = sorted(
            self.papers,
            key=lambda p: p.get("published", ""),
            reverse=True
        )

        # Split into early and late periods
        mid_point = len(sorted_papers) // 2
        recent_papers = sorted_papers[:mid_point]
        earlier_papers = sorted_papers[mid_point:]

        # Extract keywords from both periods
        def get_keywords(papers):
            all_keywords = []
            for paper in papers:
                all_keywords.extend(paper.get("keywords", []))
            return Counter(all_keywords)

        recent_keywords = get_keywords(recent_papers)
        earlier_keywords = get_keywords(earlier_papers)

        # Find emerging keywords (more frequent in recent period)
        emerging = {}
        for keyword, recent_count in recent_keywords.items():
            if recent_count >= min_frequency:
                earlier_count = earlier_keywords.get(keyword, 0)
                growth_rate = (recent_count - earlier_count) / max(earlier_count, 1)

                if growth_rate > 0.5:  # At least 50% growth
                    emerging[keyword] = {
                        "recent_count": recent_count,
                        "earlier_count": earlier_count,
                        "growth_rate": growth_rate,
                    }

        # Sort by growth rate
        emerging_sorted = sorted(
            emerging.items(),
            key=lambda x: x[1]["growth_rate"],
            reverse=True
        )

        results = {
            "emerging_topics": dict(emerging_sorted[:20]),
            "recent_period_papers": len(recent_papers),
            "earlier_period_papers": len(earlier_papers),
        }

        logger.info(f"Found {len(emerging)} emerging topics")
        return results

    def analyze_research_themes(self) -> Dict[str, Any]:
        """
        Analyze research themes across papers.

        Returns:
            dict: Research theme analysis
        """
        logger.info("Analyzing research themes")

        # Define theme categories
        themes = {
            "AI and Machine Learning": [
                "machine learning", "deep learning", "neural network", "AI",
                "artificial intelligence", "federated learning", "reinforcement learning",
            ],
            "Resource Management": [
                "resource allocation", "scheduling", "optimization", "load balancing",
                "resource management", "orchestration",
            ],
            "Networking": [
                "5G", "6G", "network", "protocol", "routing", "SDN", "NFV",
                "communication", "latency", "bandwidth",
            ],
            "IoT and Applications": [
                "IoT", "Internet of Things", "smart city", "autonomous vehicle",
                "sensor", "healthcare", "industrial",
            ],
            "Security and Privacy": [
                "security", "privacy", "authentication", "encryption", "blockchain",
                "attack", "defense",
            ],
            "Energy Efficiency": [
                "energy", "power", "green", "sustainable", "battery",
                "energy efficiency", "energy consumption",
            ],
            "Offloading": [
                "offloading", "task offloading", "computation offloading",
                "migration", "placement",
            ],
            "Caching": [
                "caching", "cache", "content delivery", "CDN", "prefetching",
            ],
        }

        # Count theme occurrences
        theme_counts = Counter()
        paper_themes = []

        for paper in self.papers:
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            paper_theme_list = []

            for theme, keywords in themes.items():
                count = sum(1 for kw in keywords if kw.lower() in text)
                if count > 0:
                    theme_counts[theme] += 1
                    paper_theme_list.append(theme)

            paper_themes.append({
                "arxiv_id": paper.get("arxiv_id"),
                "themes": paper_theme_list,
            })

        results = {
            "theme_distribution": dict(theme_counts),
            "total_themes": len(themes),
            "paper_themes": paper_themes,
            "papers_per_theme": {
                theme: count for theme, count in theme_counts.most_common()
            },
        }

        logger.info(f"Theme distribution: {dict(theme_counts)}")
        return results

    def identify_research_themes(self) -> Dict[str, Any]:
        """
        Main method to discover research themes using NLP.

        Returns:
            dict: Comprehensive thematic analysis
        """
        logger.info("Identifying research themes")

        results = {
            "lda_topics": self.extract_topics_lda(n_topics=10),
            "nmf_topics": self.extract_topics_nmf(n_topics=8),
            "clusters": self.cluster_abstracts(n_clusters=8),
            "emerging_topics": self.identify_emerging_topics(),
            "research_themes": self.analyze_research_themes(),
        }

        logger.info("Thematic analysis complete")
        return results


def main():
    """Main function for testing thematic analysis."""
    print("Thematic analyzer module loaded successfully")


if __name__ == "__main__":
    main()
