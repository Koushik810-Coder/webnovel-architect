import networkx as nx
import json
import os

class GraphProvider:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.save_path = "story_graph.json"
        self.load_graph()

    def add_character(self, name: str, attributes: dict):
        """Adds or updates a character node."""
        self.graph.add_node(name, type="character", **attributes)
        self.save_graph()

    def add_event(self, event_id: str, description: str, involved_entities: list):
        """Adds an event node and edges to involved entities."""
        self.graph.add_node(event_id, type="event", description=description)
        for entity in involved_entities:
            if self.graph.has_node(entity):
                self.graph.add_edge(entity, event_id, relation="participant")
                self.graph.add_edge(event_id, entity, relation="featured")
        self.save_graph()

    def get_character_importance(self, name: str) -> float:
        """
        Calculates importance based on PageRank or Degree Centrality.
        """
        if not self.graph.has_node(name):
            return 0.0
        
        try:
            # Calculate PageRank for the entire graph
            # Note: PageRank requires a directed graph (which we have)
            # alpha=0.85 is standard damping factor
            pagerank_scores = nx.pagerank(self.graph, alpha=0.85)
            return pagerank_scores.get(name, 0.0)
        except Exception as e:
            print(f"PageRank failed: {e}, falling back to degree.")
            return float(self.graph.degree(name))

    def save_graph(self):
        """Persists graph to JSON (Simple backup)."""
        data = nx.node_link_data(self.graph)
        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_graph(self):
        """Loads graph from JSON if exists."""
        if os.path.exists(self.save_path):
            with open(self.save_path, "r") as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data)

# Factory equivalent (singleton for now)
_graph_instance = None

def get_graph_engine():
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = GraphProvider()
    return _graph_instance
