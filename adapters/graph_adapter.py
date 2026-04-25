import networkx as nx
import json
import os

from app.core.logger import get_logger
from app.core.graduation import DELTA_UPPER
logger = get_logger(__name__)

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
        if not self.graph.has_node(name):
            # Track chronological introduction for bootstrapping
            current_chars = sum(1 for n, d in self.graph.nodes(data=True) if d.get("type") == "character")
            attributes["introduction_order"] = current_chars + 1
            # Record the debut chapter once — never overwritten on subsequent updates
            if "last_seen_chapter" in attributes:
                attributes.setdefault("first_seen_chapter", attributes["last_seen_chapter"])
            
        self.graph.add_node(name, type="character", **attributes)

    def add_event(
        self,
        event_id: str,
        description: str,
        involved_entities: list,
        chapter_id: int = 0,
        pre_conditions: str = "",
        post_conditions: str = "",
        location: str = "Unknown",
        relation_type: str = "participant",
        intensity: int = 1,
    ):
        """Adds an event node (DEU) and edges to involved entities.

        Args:
            relation_type: Qualitative relationship type (e.g. 'hostile', 'friendly', 'combat').
            intensity: Narrative intensity weight 1-5 (1=minor, 5=climactic).
                       Used as the edge weight for weighted PageRank.
        """
        self.graph.add_node(
            event_id,
            type="event",
            description=description,
            chapter_id=chapter_id,
            pre_conditions=pre_conditions,
            post_conditions=post_conditions,
            location=location,
        )
        for entity in involved_entities:
            if self.graph.has_node(entity):
                self.graph.add_edge(
                    entity, event_id,
                    relation=relation_type,
                    chapter_id=chapter_id,
                    weight=float(intensity),
                )
                self.graph.add_edge(
                    event_id, entity,
                    relation="featured",
                    chapter_id=chapter_id,
                    weight=float(intensity),
                )

    def add_causal_edge(self, source_event_id: str, target_event_id: str, relation_type: str = "causes"):
        """Adds a directed causal edge between two event nodes."""
        if self.graph.has_node(source_event_id) and self.graph.has_node(target_event_id):
            if self.graph.nodes[source_event_id].get("type") == "event" and self.graph.nodes[target_event_id].get("type") == "event":
                self.graph.add_edge(source_event_id, target_event_id, relation=relation_type)

    def get_character_events(self, name: str) -> list:
        """Returns a chronological list of all events a character participated in."""
        if not self.graph.has_node(name):
            return []
            
        events = []
        for u, v, data in self.graph.out_edges(name, data=True):
            # Check the destination node is an event node (not another character).
            # We do NOT filter by relation label because add_event() stores the
            # actual relation_type ("hostile", "friendly", etc.) — not a literal
            # "participant" string — so the old label check silently dropped all
            # events added with an explicit relation_type.
            if self.graph.has_node(v) and self.graph.nodes[v].get("type") == "event":
                event_data = self.graph.nodes[v]
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

    def get_debut_prominence(self, name: str, debut_chapter_id: int) -> float:
        """Debut Prominence Quotient (DPQ): measures a character's local dominance
        within the debut chapter's interaction subgraph.

        Replaces the hardcoded top-5 bootstrapping heuristic.
        A character that drives >40% of the debut chapter's weighted interactions
        is granted a provisional score of 0.16 (above the graduation threshold)
        to survive their first-appearance voice assignment check.

        Returns a score in [0.0, 1.0].
        """
        # Collect all events in the debut chapter
        debut_event_ids = [
            n for n, d in self.graph.nodes(data=True)
            if d.get("type") == "event" and d.get("chapter_id") == debut_chapter_id
        ]
        if not debut_event_ids:
            return 0.0

        # Total weighted interactions in chapter
        total_weight = 0.0
        char_weight = 0.0
        for ev_id in debut_event_ids:
            for u, v, data in self.graph.edges(ev_id, data=True):
                w = data.get("weight", 1.0)
                total_weight += w
                if u == name or v == name:
                    char_weight += w

        if total_weight == 0:
            return 0.0
        return char_weight / total_weight

    def get_character_importance(self, name: str, current_chapter: int = 0, decay_rate: float = 0.05) -> float:
        """
        Calculates importance based on weighted PageRank plus Temporal Decay.

        Bootstrapping uses Debut Prominence Quotient (DPQ) instead of a hardcoded
        top-N list: a character that dominates their debut chapter's interactions
        earns a provisional score until graph topology accumulates sufficient history.
        """
        if not self.graph.has_node(name):
            return 0.0

        try:
            # Weighted PageRank — edges with higher intensity carry more authority
            pagerank_scores = nx.pagerank(self.graph, alpha=0.85, weight="weight")
            base_score = float(pagerank_scores.get(name, 0.0))

            # Find the most recent chapter this character participated in
            max_chapter = 0
            for u, v, data in self.graph.out_edges(name, data=True):
                edge_chap = data.get("chapter_id", 0)
                max_chapter = max(max_chapter, edge_chap)

            # Apply temporal decay: Score degrades as chapters pass without appearance
            if current_chapter > 0 and max_chapter > 0:
                age = max(0, current_chapter - max_chapter)
                temporal_multiplier = (1.0 - decay_rate) ** age
                score = base_score * temporal_multiplier
            else:
                score = base_score

            # Debut Prominence Quotient (DPQ) — algorithmic bootstrapping.
            # Triggers only in the character's DEBUT chapter, not on every appearance.
            first_seen_chapter = self.graph.nodes[name].get("first_seen_chapter", current_chapter)
            if first_seen_chapter == current_chapter:
                dpq = self.get_debut_prominence(name, debut_chapter_id=current_chapter)
                # A character dominating >40% of debut chapter interactions is provisionally graduated
                if dpq >= 0.40:
                    logger.debug(f"DPQ provisional graduation for '{name}': dpq={dpq:.2f}")
                    return max(score, DELTA_UPPER + 0.01)

            return score
        except Exception as e:
            logger.warning(f"Temporal PageRank failed: {e}, falling back to degree.")
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

    def save_graph(self):
        """Persists graph to JSON using write-to-temp + rename for atomicity.
        
        A direct open(path, 'w') truncates the file before writing, so a
        mid-write process kill would leave the graph corrupt with no recovery.
        Writing to a sibling .tmp file and then renaming is atomic on all
        major OS/filesystems (POSIX rename, Windows ReplaceFile).
        """
        import pathlib
        tmp_path = pathlib.Path(self.save_path).with_suffix(".tmp")
        data = nx.node_link_data(self.graph, edges="edges")
        with open(tmp_path, "w") as f:
            json.dump(data, f, indent=2)
        tmp_path.replace(self.save_path)

    def load_graph(self):
        """Loads graph from JSON if exists."""
        if os.path.exists(self.save_path):
            with open(self.save_path, "r") as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data, edges="edges")

# Instance mapping to preserve state across multiple stories simultaneously in memory
_graph_instances = {}

def get_graph_engine(story_uuid: str):
    global _graph_instances
    if story_uuid not in _graph_instances:
        _graph_instances[story_uuid] = GraphProvider(story_uuid)
    return _graph_instances[story_uuid]
