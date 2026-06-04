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
        else:
            # On subsequent visits, merge new aliases rather than overwriting the node.
            # This preserves aliases from previous chapters and accumulates them.
            existing = dict(self.graph.nodes[name])
            new_aliases = set(attributes.pop("aliases", []))
            old_aliases = set(existing.get("aliases", []))
            merged_aliases = sorted(old_aliases | new_aliases)
            attributes["aliases"] = merged_aliases
            self.graph.nodes[name].update(attributes)

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
        # 1.1 Dual-timeline fields
        timeline_type: str = "present",
        narrative_order: int = 0,
        story_time_rank: "int | None" = None,
        story_time_relative: "str | None" = None,
        flashback_depth: int = 0,
        # 1.2 Spoiler & canonicity fields
        reveal_point: int = 0,
        spoiler_level: int = 0,
        is_canonical: bool = True,
        confidence: float = 1.0,
        # 1.6 Character roles
        character_roles: "dict | None" = None,
    ):
        """Adds an event node (DEU) and edges to involved entities.

        Args:
            relation_type: Qualitative relationship type (e.g. 'hostile', 'friendly', 'combat').
            intensity: Narrative intensity weight 1-5 (1=minor, 5=climactic).
                       Used as the edge weight for weighted PageRank.
            timeline_type: 'present' | 'flashback' | 'memory' | 'dream' | 'rumor' | 'imagined'
            narrative_order: Position within the chapter (1, 2, 3…)
            story_time_rank: Relative in-universe chronology; None if ambiguous.
            story_time_relative: Fallback description e.g. 'before the siege'.
            flashback_depth: 0=present, 1=flashback, 2=flashback-within-flashback.
            reveal_point: Chapter at which this event becomes spoiler-safe (0=immediate).
            spoiler_level: 0=safe, 1=mild spoiler, 2=major twist.
            is_canonical: False for imagined/misremembered/lied-about events.
            confidence: LLM-estimated extraction certainty (0.0–1.0).
            character_roles: Dict mapping entity_id → role string (protagonist/antagonist/
                             witness/cause/victim/bystander).
        """
        _roles = character_roles or {}
        self.graph.add_node(
            event_id,
            type="event",
            description=description,
            chapter_id=chapter_id,
            pre_conditions=pre_conditions,
            post_conditions=post_conditions,
            location=location,
            # 1.1
            timeline_type=timeline_type,
            narrative_order=narrative_order,
            story_time_rank=story_time_rank,
            story_time_relative=story_time_relative,
            flashback_depth=flashback_depth,
            # 1.2
            reveal_point=reveal_point,
            spoiler_level=spoiler_level,
            is_canonical=is_canonical,
            confidence=confidence,
        )
        for entity in involved_entities:
            if self.graph.has_node(entity):
                role = _roles.get(entity, "participant")
                self.graph.add_edge(
                    entity, event_id,
                    relation=relation_type,
                    chapter_id=chapter_id,
                    weight=float(intensity),
                    role=role,  # 1.6
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

    def add_arc(self, arc_id: str, label: str, event_ids: list, chapter_start: int, chapter_end: int):
        """Adds an arc node grouping several events."""
        self.graph.add_node(
            arc_id,
            type="arc",
            label=label,
            event_ids=event_ids,
            chapter_start=chapter_start,
            chapter_end=chapter_end
        )
        for ev_id in event_ids:
            if self.graph.has_node(ev_id):
                self.graph.add_edge(arc_id, ev_id, relation="contains")

    def add_knowledge_edge(self, char_id: str, event_id: str, edge_type: str = "knows"):
        """Explicitly tracks character knowledge or ignorance of an event.

        NOTE: This is a DiGraph — calling add_edge on an existing edge OVERWRITES
        all its attributes. We must never clobber a participant edge (which carries
        chapter_id, weight, role) with a bare knowledge edge.  If the char→event
        edge already exists and has a chapter_id (i.e. it's a proper participant
        edge), we skip adding the knowledge edge to avoid data loss.

        Args:
            char_id: Normalized character ID.
            event_id: The event node ID.
            edge_type: "knows" | "unaware_of"
        """
        if self.graph.has_node(char_id) and self.graph.has_node(event_id):
            # Guard: don't overwrite a rich participant edge with a bare knowledge edge.
            if self.graph.has_edge(char_id, event_id):
                existing = self.graph[char_id][event_id]
                if "chapter_id" in existing:
                    # Already a participant edge — preserve it, skip the knowledge edge.
                    return
            self.graph.add_edge(char_id, event_id, relation=edge_type)


    def add_scene(self, scene_id: str, chapter_id: int, location: str, summary: str):
        """Adds a scene node."""
        self.graph.add_node(
            scene_id,
            type="scene",
            chapter_id=chapter_id,
            location=location,
            summary=summary
        )

    def add_event_to_scene(self, event_id: str, scene_id: str):
        """Links an event to the scene it occurs in."""
        if self.graph.has_node(event_id) and self.graph.has_node(scene_id):
            self.graph.add_edge(event_id, scene_id, relation="OCCURS_IN")

    def add_or_update_character_edge(
        self,
        char_a: str,
        char_b: str,
        relation_type: str = "neutral",
        chapter_id: int = 0,
        intensity: int = 1,
    ):
        """Upserts a direct character-to-character edge with co-occurrence tracking.

        On first encounter: creates bidirectional edges (stored as two directed edges).
        On re-encounter: bumps co_occurrence_count, records newest relation_type, and
        accumulates the weight so high-frequency pairs rank higher in PageRank.

        Args:
            char_a: Normalized character ID of the first participant.
            char_b: Normalized character ID of the second participant.
            relation_type: Qualitative relationship label (e.g. 'friendly', 'hostile').
            chapter_id: Chapter where this co-occurrence was observed.
            intensity: Narrative intensity 1-5; added to cumulative edge weight.
        """
        for src, dst in [(char_a, char_b), (char_b, char_a)]:
            if not self.graph.has_node(src) or not self.graph.has_node(dst):
                continue
            if self.graph.has_edge(src, dst):
                edge_data = self.graph[src][dst]
                edge_data["co_occurrence_count"] = edge_data.get("co_occurrence_count", 1) + 1
                edge_data["last_seen_chapter"] = chapter_id
                edge_data["last_relation_type"] = relation_type
                edge_data["weight"] = edge_data.get("weight", 0.0) + float(intensity)
                # 1.9: append snapshot to history instead of overwriting
                history = edge_data.setdefault("relation_history", [])
                history.append({"chapter": chapter_id, "relation": relation_type})
            else:
                self.graph.add_edge(
                    src, dst,
                    edge_type="character_relation",
                    relation_type=relation_type,
                    last_relation_type=relation_type,
                    co_occurrence_count=1,
                    first_seen_chapter=chapter_id,
                    last_seen_chapter=chapter_id,
                    weight=float(intensity),
                    # 1.9: start relation history
                    relation_history=[{"chapter": chapter_id, "relation": relation_type}],
                )

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

    def compute_chapter_scores(
        self,
        current_chapter: int = 0,
        decay_rate: float = 0.05,
    ) -> dict:
        """B3: Computes importance scores for ALL characters in ONE PageRank call.

        Returns a dict mapping character_id -> score, applying the same temporal
        decay logic as get_character_importance(). Callers should invoke this once
        per chapter and read from the returned dict instead of calling
        get_character_importance() per character (which recomputes PageRank N times).
        """
        if not self.graph.nodes:
            return {}

        try:
            pagerank_scores = nx.pagerank(self.graph, alpha=0.85, weight="weight")
        except Exception as e:
            logger.warning(f"PageRank computation failed: {e}. Falling back to degree centrality.")
            pagerank_scores = {n: float(self.graph.degree(n)) for n in self.graph.nodes}

        result: dict = {}
        for node, data in self.graph.nodes(data=True):
            if data.get("type") != "character":
                continue

            base_score = float(pagerank_scores.get(node, 0.0))

            # Temporal decay: find the most recent chapter edge for this character
            max_chapter = 0
            for _, _, edge_data in self.graph.out_edges(node, data=True):
                max_chapter = max(max_chapter, edge_data.get("chapter_id", 0))

            if current_chapter > 0 and max_chapter > 0:
                age = max(0, current_chapter - max_chapter)
                score = base_score * ((1.0 - decay_rate) ** age)
            else:
                score = base_score

            # Debut Prominence Quotient (DPQ) — same logic as get_character_importance
            first_seen = data.get("first_seen_chapter", current_chapter)
            if first_seen == current_chapter:
                dpq = self.get_debut_prominence(node, debut_chapter_id=current_chapter)
                if dpq >= 0.40:
                    score = max(score, DELTA_UPPER + 0.01)

            result[node] = score

        return result

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

# Instance mapping to preserve state across multiple stories simultaneously in memory.
# Capped at MAX_CACHED_GRAPHS entries; the oldest entry is evicted when the cap is
# exceeded so long-running Streamlit sessions don't OOM on large story collections.
_graph_instances: dict = {}
_MAX_CACHED_GRAPHS = 5

def get_graph_engine(story_uuid: str) -> "GraphProvider":
    global _graph_instances
    if story_uuid not in _graph_instances:
        if len(_graph_instances) >= _MAX_CACHED_GRAPHS:
            # Evict the oldest entry (insertion-order guaranteed in Python 3.7+)
            oldest = next(iter(_graph_instances))
            logger.debug(f"Graph cache full — evicting story '{oldest}'")
            del _graph_instances[oldest]
        _graph_instances[story_uuid] = GraphProvider(story_uuid)
    return _graph_instances[story_uuid]


# 1.7  Dynamic PageRank threshold scaling
# M_base is the MAIN_CAST_THRESHOLD tuned for a small graph.
# As node count N grows, the threshold scales down via sqrt so late-series
# characters can still reach graduation, while the floor at DELTA_UPPER
# prevents the threshold from becoming trivially small.
_MAIN_CAST_BASE = 0.50  # same as graduation.MAIN_CAST_THRESHOLD for small N


def _dynamic_main_cast_threshold(node_count: int) -> float:
    """Return a dynamically scaled graduation threshold based on graph size."""
    return max(DELTA_UPPER, _MAIN_CAST_BASE / (node_count ** 0.5))


GraphProvider.get_dynamic_main_cast_threshold = staticmethod(_dynamic_main_cast_threshold)
