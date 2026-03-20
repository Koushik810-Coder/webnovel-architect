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

    def add_event(self, event_id: str, description: str, involved_entities: list, chapter_id: int = 0, pre_conditions: str = "", post_conditions: str = "", location: str = "Unknown"):
        """Adds an event node (DEU) and edges to involved entities."""
        self.graph.add_node(
            event_id, 
            type="event", 
            description=description, 
            chapter_id=chapter_id,
            pre_conditions=pre_conditions,
            post_conditions=post_conditions,
            location=location
        )
        for entity in involved_entities:
            if self.graph.has_node(entity):
                self.graph.add_edge(entity, event_id, relation="participant", chapter_id=chapter_id)
                self.graph.add_edge(event_id, entity, relation="featured", chapter_id=chapter_id)
        self.save_graph()

    def add_causal_edge(self, source_event_id: str, target_event_id: str, relation_type: str = "causes"):
        """Adds a directed causal edge between two event nodes."""
        if self.graph.has_node(source_event_id) and self.graph.has_node(target_event_id):
            if self.graph.nodes[source_event_id].get("type") == "event" and self.graph.nodes[target_event_id].get("type") == "event":
                self.graph.add_edge(source_event_id, target_event_id, relation=relation_type)
                self.save_graph()

    def get_character_events(self, name: str) -> list:
        """Returns a chronological list of all events a character participated in."""
        if not self.graph.has_node(name):
            return []
            
        events = []
        for u, v, data in self.graph.out_edges(name, data=True):
            if data.get("relation") == "participant" and self.graph.has_node(v):
                event_data = self.graph.nodes[v]
                if event_data.get("type") == "event":
                    events.append({
                        "id": v,
                        "description": event_data.get("description", ""),
                        "chapter_id": event_data.get("chapter_id", 0)
                    })
                    
        # Sort chronologically by chapter_id
        events.sort(key=lambda x: x["chapter_id"])
        return events

    def get_event_chain(self, start_event_id: str, max_depth: int = 10) -> list:
        """
        Traverses 'causes' edges to return a causal chain of events originating from the start node.
        Returns a list of event dictionaries, ordered by causality.
        """
        if not self.graph.has_node(start_event_id) or self.graph.nodes[start_event_id].get("type") != "event":
            return []
            
        chain = []
        current = start_event_id
        depth = 0
        
        while current and depth < max_depth:
            # Add current event to chain
            event_data = self.graph.nodes[current]
            chain.append({
                "id": current,
                "description": event_data.get("description", ""),
                "chapter_id": event_data.get("chapter_id", 0)
            })
            
            # Find the next event caused by this one
            next_event = None
            for u, v, data in self.graph.out_edges(current, data=True):
                if data.get("relation") == "causes" and self.graph.has_node(v) and self.graph.nodes[v].get("type") == "event":
                    # Avoid cycles
                    if not any(e["id"] == v for e in chain):
                        next_event = v
                        break # Only following the first causal link for this simple chain extraction
                        
            current = next_event
            depth += 1
            
        return chain

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

    def merge_characters(self, source_id: str, target_id: str):
        """
        Retroactively merges an alias (source) into a canonical character (target).
        Transfers all edges (event participations) and updates attributes.
        """
        if not self.graph.has_node(source_id) or not self.graph.has_node(target_id):
            return
            
        # Target inherits any "newer" last_seen_chapter from the source
        src_data = self.graph.nodes[source_id]
        tgt_data = self.graph.nodes[target_id]
        
        if "last_seen_chapter" in src_data and "last_seen_chapter" in tgt_data:
            tgt_data["last_seen_chapter"] = max(src_data["last_seen_chapter"], tgt_data["last_seen_chapter"])

        # Transfer Out-Edges (Character -> Event relationship: "participant")
        for u, v, data in list(self.graph.out_edges(source_id, data=True)):
            if not self.graph.has_edge(target_id, v):
                self.graph.add_edge(target_id, v, **data)

        # Transfer In-Edges (Event -> Character relationship: "featured")
        for u, v, data in list(self.graph.in_edges(source_id, data=True)):
            if not self.graph.has_edge(u, target_id):
                self.graph.add_edge(u, target_id, **data)

        # Remove the obsolete alias node
        self.graph.remove_node(source_id)
        self.save_graph()

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
