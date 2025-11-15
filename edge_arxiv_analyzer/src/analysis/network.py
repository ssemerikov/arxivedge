"""
Network analysis module for co-authorship and collaboration networks.
"""

from typing import List, Dict, Any, Tuple
import networkx as nx
from collections import Counter, defaultdict
import numpy as np
from loguru import logger


class NetworkAnalyzer:
    """Perform network analysis on ArXiv papers."""

    def __init__(self, papers: List[Dict[str, Any]]):
        """
        Initialize network analyzer.

        Args:
            papers: List of paper dictionaries
        """
        self.papers = papers
        self.coauthor_graph = None
        self.keyword_graph = None

    def build_coauthorship_network(self, min_collaborations: int = 1) -> nx.Graph:
        """
        Build co-authorship network.

        Args:
            min_collaborations: Minimum collaborations to include edge

        Returns:
            networkx.Graph: Co-authorship network
        """
        logger.info("Building co-authorship network")

        G = nx.Graph()

        # Count co-authorships
        coauthor_counts = Counter()

        for paper in self.papers:
            authors = paper.get("authors", [])

            # Add all authors as nodes
            for author in authors:
                if not G.has_node(author):
                    G.add_node(author, papers=1)
                else:
                    G.nodes[author]["papers"] += 1

            # Add edges for co-authorships
            if len(authors) > 1:
                for i, author1 in enumerate(authors):
                    for author2 in authors[i + 1:]:
                        edge = tuple(sorted([author1, author2]))
                        coauthor_counts[edge] += 1

        # Add edges with weights
        for (author1, author2), weight in coauthor_counts.items():
            if weight >= min_collaborations:
                G.add_edge(author1, author2, weight=weight)

        logger.info(f"Built network with {G.number_of_nodes()} authors and {G.number_of_edges()} collaborations")
        self.coauthor_graph = G
        return G

    def analyze_coauthorship_network(self) -> Dict[str, Any]:
        """
        Analyze co-authorship network metrics.

        Returns:
            dict: Network analysis metrics
        """
        if self.coauthor_graph is None:
            self.build_coauthorship_network()

        G = self.coauthor_graph
        logger.info("Analyzing co-authorship network")

        # Basic metrics
        n_nodes = G.number_of_nodes()
        n_edges = G.number_of_edges()

        stats = {
            "n_authors": n_nodes,
            "n_collaborations": n_edges,
            "density": nx.density(G) if n_nodes > 1 else 0,
            "n_components": nx.number_connected_components(G),
        }

        # Degree statistics
        degrees = dict(G.degree())
        if degrees:
            stats["avg_degree"] = np.mean(list(degrees.values()))
            stats["max_degree"] = max(degrees.values())
            stats["min_degree"] = min(degrees.values())

        # Get largest component
        if n_nodes > 0:
            largest_cc = max(nx.connected_components(G), key=len)
            largest_subgraph = G.subgraph(largest_cc)

            stats["largest_component_size"] = len(largest_cc)
            stats["largest_component_edges"] = largest_subgraph.number_of_edges()

            # Calculate metrics on largest component
            if len(largest_cc) > 1:
                stats["avg_clustering"] = nx.average_clustering(largest_subgraph)

                # Calculate centrality measures (on sample if too large)
                if len(largest_cc) <= 1000:
                    betweenness = nx.betweenness_centrality(largest_subgraph)
                    closeness = nx.closeness_centrality(largest_subgraph)
                    eigenvector = nx.eigenvector_centrality(largest_subgraph, max_iter=100)

                    # Top authors by centrality
                    stats["top_betweenness"] = sorted(
                        betweenness.items(), key=lambda x: x[1], reverse=True
                    )[:10]
                    stats["top_closeness"] = sorted(
                        closeness.items(), key=lambda x: x[1], reverse=True
                    )[:10]
                    stats["top_eigenvector"] = sorted(
                        eigenvector.items(), key=lambda x: x[1], reverse=True
                    )[:10]

        logger.info("Co-authorship network analysis complete")
        return stats

    def identify_research_communities(self, min_size: int = 3) -> Dict[str, Any]:
        """
        Identify research communities using community detection.

        Args:
            min_size: Minimum community size

        Returns:
            dict: Community detection results
        """
        if self.coauthor_graph is None:
            self.build_coauthorship_network()

        G = self.coauthor_graph
        logger.info("Identifying research communities")

        # Use Louvain algorithm for community detection
        try:
            import community as community_louvain
            communities = community_louvain.best_partition(G)
        except ImportError:
            logger.warning("python-louvain not available, using connected components instead")
            communities = {}
            for i, component in enumerate(nx.connected_components(G)):
                for node in component:
                    communities[node] = i

        # Organize communities
        community_groups = defaultdict(list)
        for author, comm_id in communities.items():
            community_groups[comm_id].append(author)

        # Filter by size and analyze
        significant_communities = {
            comm_id: members
            for comm_id, members in community_groups.items()
            if len(members) >= min_size
        }

        # Get top papers for each community
        community_info = {}
        for comm_id, members in significant_communities.items():
            # Find papers authored by community members
            community_papers = [
                paper for paper in self.papers
                if any(author in members for author in paper.get("authors", []))
            ]

            # Get common categories
            categories = []
            for paper in community_papers:
                categories.extend(paper.get("categories", []))

            category_counts = Counter(categories)

            community_info[f"Community {comm_id}"] = {
                "size": len(members),
                "n_papers": len(community_papers),
                "top_members": members[:10],
                "top_categories": category_counts.most_common(5),
            }

        stats = {
            "n_communities": len(significant_communities),
            "communities": community_info,
            "modularity": nx.algorithms.community.modularity(
                G, [set(members) for members in significant_communities.values()]
            ) if significant_communities else 0,
        }

        logger.info(f"Identified {len(significant_communities)} significant communities")
        return stats

    def build_keyword_network(self, min_cooccurrence: int = 2) -> nx.Graph:
        """
        Build keyword co-occurrence network.

        Args:
            min_cooccurrence: Minimum co-occurrences to include edge

        Returns:
            networkx.Graph: Keyword network
        """
        logger.info("Building keyword co-occurrence network")

        G = nx.Graph()

        # Count keyword co-occurrences
        keyword_pairs = Counter()

        for paper in self.papers:
            keywords = paper.get("keywords", [])

            # Add nodes
            for kw in keywords:
                if not G.has_node(kw):
                    G.add_node(kw, count=1)
                else:
                    G.nodes[kw]["count"] += 1

            # Add edges for co-occurrences
            if len(keywords) > 1:
                for i, kw1 in enumerate(keywords):
                    for kw2 in keywords[i + 1:]:
                        edge = tuple(sorted([kw1, kw2]))
                        keyword_pairs[edge] += 1

        # Add edges with weights
        for (kw1, kw2), weight in keyword_pairs.items():
            if weight >= min_cooccurrence:
                G.add_edge(kw1, kw2, weight=weight)

        logger.info(f"Built keyword network with {G.number_of_nodes()} keywords and {G.number_of_edges()} edges")
        self.keyword_graph = G
        return G

    def analyze_keyword_network(self) -> Dict[str, Any]:
        """
        Analyze keyword co-occurrence network.

        Returns:
            dict: Keyword network metrics
        """
        if self.keyword_graph is None:
            self.build_keyword_network()

        G = self.keyword_graph
        logger.info("Analyzing keyword network")

        stats = {
            "n_keywords": G.number_of_nodes(),
            "n_connections": G.number_of_edges(),
            "density": nx.density(G) if G.number_of_nodes() > 1 else 0,
        }

        # Degree statistics
        degrees = dict(G.degree())
        if degrees:
            stats["avg_degree"] = np.mean(list(degrees.values()))

            # Top keywords by degree (most connected)
            stats["top_connected_keywords"] = sorted(
                degrees.items(), key=lambda x: x[1], reverse=True
            )[:20]

        # Get keyword clusters
        if G.number_of_nodes() > 0:
            components = list(nx.connected_components(G))
            stats["n_keyword_clusters"] = len(components)
            stats["largest_cluster_size"] = len(max(components, key=len)) if components else 0

        logger.info("Keyword network analysis complete")
        return stats

    def export_network(self, output_file: str, network_type: str = "coauthor"):
        """
        Export network to GraphML format.

        Args:
            output_file: Output file path
            network_type: Type of network ('coauthor' or 'keyword')
        """
        if network_type == "coauthor":
            if self.coauthor_graph is None:
                self.build_coauthorship_network()
            G = self.coauthor_graph
        elif network_type == "keyword":
            if self.keyword_graph is None:
                self.build_keyword_network()
            G = self.keyword_graph
        else:
            raise ValueError(f"Unknown network type: {network_type}")

        nx.write_graphml(G, output_file)
        logger.info(f"Exported {network_type} network to {output_file}")

    def generate_network_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive network analysis.

        Returns:
            dict: Complete network analysis
        """
        logger.info("Generating comprehensive network analysis")

        analysis = {
            "coauthorship_network": self.analyze_coauthorship_network(),
            "research_communities": self.identify_research_communities(),
            "keyword_network": self.analyze_keyword_network(),
        }

        logger.info("Network analysis complete")
        return analysis


def main():
    """Main function for testing network analysis."""
    print("Network analyzer module loaded successfully")


if __name__ == "__main__":
    main()
