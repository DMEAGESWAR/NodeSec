import json


def build_graph_json(nodes, edges, chains):
    """Unified graph output builder. Produces the standard graph JSON format."""
    return {
        "nodes": [
            {
                "id": str(n.id) if hasattr(n, "id") else n.get("id", ""),
                "type": n.node_type if hasattr(n, "node_type") else n.get("node_type", ""),
                "data": {
                    "label": n.label if hasattr(n, "label") else n.get("label", ""),
                    "ip": n.ip if hasattr(n, "ip") else n.get("ip"),
                    "port": n.port if hasattr(n, "port") else n.get("port"),
                    "severity": n.severity if hasattr(n, "severity") else n.get("severity", "low"),
                    "raw_data": n.raw_data if hasattr(n, "raw_data") else n.get("raw_data", {}),
                },
            }
            for n in nodes
        ],
        "edges": [
            {
                "id": str(e.id) if hasattr(e, "id") else e.get("id", ""),
                "source": str(e.source_node_id) if hasattr(e, "source_node_id") else e.get("source_node_id", e.get("source", "")),
                "target": str(e.target_node_id) if hasattr(e, "target_node_id") else e.get("target_node_id", e.get("target", "")),
                "type": e.relationship_type if hasattr(e, "relationship_type") else e.get("relationship_type", ""),
            }
            for e in edges
        ],
        "chains": chains,
    }