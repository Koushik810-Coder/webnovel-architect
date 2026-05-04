import hashlib
import json
import networkx as nx

def compute_node_hash(graph: nx.DiGraph, node_id: str) -> str:
    """
    Computes a deterministic SHA256 hash representing a node's state
    and its immediate neighborhood (incident edges and adjacent nodes' basic info).
    This ensures that if anything relevant to the node's wiki page changes,
    the hash will change, invalidating the cache.
    """
    state_dict = {}

    if graph.has_node(node_id):
        # 1. Node's own attributes
        node_data = dict(graph.nodes[node_id])
        
        # 2. In-edges and source node info
        in_edges = []
        for u, v, data in graph.in_edges(node_id, data=True):
            in_edges.append({
                "source": u,
                "edge_data": data,
                "source_type": graph.nodes[u].get("type", "")
            })
            
        # 3. Out-edges and target node info
        out_edges = []
        for u, v, data in graph.out_edges(node_id, data=True):
            out_edges.append({
                "target": v,
                "edge_data": data,
                "target_type": graph.nodes[v].get("type", "")
            })
            
        in_edges.sort(key=lambda x: json.dumps(x, sort_keys=True))
        out_edges.sort(key=lambda x: json.dumps(x, sort_keys=True))
        
        state_dict = {
            "node_id": node_id,
            "node_data": node_data,
            "in_edges": in_edges,
            "out_edges": out_edges
        }
    else:
        # Fallback for locations which might not be nodes themselves but properties on events
        events_at_location = []
        for u, data in graph.nodes(data=True):
            if data.get("type") == "event" and data.get("location") == node_id:
                events_at_location.append({"id": u, "data": data})
        
        if not events_at_location:
            return ""
            
        events_at_location.sort(key=lambda x: json.dumps(x, sort_keys=True))
        state_dict = {
            "location_id": node_id,
            "events": events_at_location
        }
        
    state_json = json.dumps(state_dict, sort_keys=True)
    return hashlib.sha256(state_json.encode("utf-8")).hexdigest()
