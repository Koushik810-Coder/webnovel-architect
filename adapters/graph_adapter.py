import networkx as nx
import json
import os

class GraphProvider:
    def __init__(self, story_uuid: str):
        self.story_uuid = story_uuid
        self.graph = nx.DiGraph()
        
        # Ensure directory exists before setting save path
        from app.core.story_manager import StoryManager
        story_dir = os.path.join(StoryManager.DATA_DIR, story_uuid)
        os.makedirs(story_dir, exist_ok=True)
        
        self.save_path = os.path.join(story_dir, "story_graph.json")
        self.load_graph()

    def add_character(self, name: str, attributes: dict):
        """Adds or updates a character node."""
        self.graph.add_node(name, type="character", **attributes)
        self.save_graph()

    def add_event(self, event_id: str, description: str, involved_entities: list, chapter_id: int = 0):
        """Adds an event node and edges to involved entities."""
        self.graph.add_node(event_id, type="event", description=description, chapter_id=chapter_id)
        for entity in involved_entities:
            if self.graph.has_node(entity):
                self.graph.add_edge(entity, event_id, relation="participant", chapter_id=chapter_id)
                self.graph.add_edge(event_id, entity, relation="featured", chapter_id=chapter_id)
        self.save_graph()

    def get_character_importance(self, name: str, current_chapter: int = 0, decay_rate: float = 0.05) -> float:
        """
        Calculates importance based on PageRank.
        Applies a temporal decay based on how old the connection is relative to the current_chapter.
        """
        if not self.graph.has_node(name):
            return 0.0
        
        try:
            # Calculate base PageRank
            pagerank_scores = nx.pagerank(self.graph, alpha=0.85)
            base_score = float(pagerank_scores.get(name, 0.0))
            
            # Find the most recent event for this character to apply decay
            max_chapter = 0
            for u, v, data in self.graph.out_edges(name, data=True):
                edge_chap = data.get("chapter_id", 0)
                max_chapter = max(max_chapter, edge_chap)
                
            # Compute multiplier
            if current_chapter > 0 and max_chapter > 0:
                age = max(0, current_chapter - max_chapter)
                temporal_multiplier = (1.0 - decay_rate) ** age
                return base_score * temporal_multiplier
                
            return base_score
        except Exception as e:
            print(f"Temporal PageRank failed: {e}, falling back to degree.")
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

# Instance mapping to preserve state across multiple stories simultaneously in memory
_graph_instances = {}

def get_graph_engine(story_uuid: str):
    global _graph_instances
    if story_uuid not in _graph_instances:
        _graph_instances[story_uuid] = GraphProvider(story_uuid)
    return _graph_instances[story_uuid]
