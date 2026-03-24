"""
Interactive object graph visualization.

Drop-in enhancement for objgraph that produces an interactive HTML page
where you can filter, hide, and collapse nodes.

Usage:
    import objgraph_interactive as oi

    # Show references from an object
    oi.show_refs(my_obj, max_depth=3)

    # Show backreferences to an object
    oi.show_backrefs(my_obj, max_depth=3)

    # From a previously saved JSON file
    oi.serve("graph.json")

    # Just write the HTML file without serving
    oi.show_refs(my_obj, filename="graph.html", serve=False)
"""

import gc
import json
import http.server
import io
import os
import sys
import tempfile
import types
import webbrowser
from pathlib import Path

_HTML_PATH = Path(__file__).parent / "interactive_objgraph.html"

# ── graph walking ──────────────────────────────────────────────────────

def _short_repr(obj, max_len=60):
    try:
        r = repr(obj)
    except Exception:
        r = "<?>"
    if len(r) > max_len:
        r = r[:max_len - 3] + "..."
    return r


def _type_name(obj):
    t = type(obj).__name__
    mod = getattr(type(obj), "__module__", None)
    if mod and mod not in ("builtins", "__builtin__"):
        t = f"{mod}.{t}"
    return t


def _walk_refs(root, max_depth=3, max_nodes=200, too_many=10,
               filter_func=None, direction="refs"):
    """Walk references (or back-references) and return (nodes, edges)."""
    seen = {}          # id -> node dict
    edges = []         # list of {source, target}
    queue = [(root, 0)]
    node_id_map = {}   # id(obj) -> stable str id

    def _nid(obj):
        oid = id(obj)
        if oid not in node_id_map:
            node_id_map[oid] = f"n{len(node_id_map)}"
        return node_id_map[oid]

    while queue and len(seen) < max_nodes:
        obj, depth = queue.pop(0)
        oid = id(obj)
        if oid in seen:
            continue

        nid = _nid(obj)
        seen[oid] = {
            "id": nid,
            "type": _type_name(obj),
            "label": _short_repr(obj),
            "depth": depth,
            "is_root": (obj is root),
        }

        if depth >= max_depth:
            continue

        if direction == "refs":
            children = gc.get_referents(obj)
        else:
            children = gc.get_referrers(obj)
            # filter out this frame and internal objects
            children = [
                c for c in children
                if not isinstance(c, types.FrameType) and c is not seen
            ]

        if filter_func:
            children = [c for c in children if filter_func(c)]

        if len(children) > too_many:
            children = children[:too_many]

        for child in children:
            cid = _nid(child)
            if direction == "refs":
                edges.append({"source": nid, "target": cid})
            else:
                edges.append({"source": cid, "target": nid})
            if id(child) not in seen:
                queue.append((child, depth + 1))

    return list(seen.values()), edges


def _build_graph_json(obj, max_depth=3, max_nodes=200, too_many=10,
                      filter_func=None, direction="refs", extra_label=""):
    nodes, edges = _walk_refs(
        obj,
        max_depth=max_depth,
        max_nodes=max_nodes,
        too_many=too_many,
        filter_func=filter_func,
        direction=direction,
    )
    return {
        "meta": {
            "direction": direction,
            "root_type": _type_name(obj),
            "extra_label": extra_label,
            "max_depth": max_depth,
        },
        "nodes": nodes,
        "edges": edges,
    }


# ── public API ─────────────────────────────────────────────────────────

def show_refs(obj, max_depth=3, filename=None, serve=True, **kw):
    """Visualize outgoing references from *obj*."""
    data = _build_graph_json(obj, max_depth=max_depth, direction="refs", **kw)
    return _output(data, filename=filename, serve=serve)


def show_backrefs(obj, max_depth=3, filename=None, serve=True, **kw):
    """Visualize incoming references to *obj*."""
    data = _build_graph_json(obj, max_depth=max_depth, direction="backrefs", **kw)
    return _output(data, filename=filename, serve=serve)


def show_graph(graph_json, filename=None, serve=True):
    """Visualize a pre-built graph dict or JSON string."""
    if isinstance(graph_json, str):
        graph_json = json.loads(graph_json)
    return _output(graph_json, filename=filename, serve=serve)


# ── output helpers ─────────────────────────────────────────────────────

def _output(data, filename=None, serve=True):
    html_template = _HTML_PATH.read_text()
    # Inject JSON data into the template
    json_blob = json.dumps(data, default=str)
    html = html_template.replace(
        "/* __GRAPH_DATA_PLACEHOLDER__ */",
        f"window.__GRAPH_DATA__ = {json_blob};",
    )

    if filename:
        Path(filename).write_text(html)
        path = str(Path(filename).resolve())
    else:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".html", prefix="objgraph_", delete=False, mode="w"
        )
        tmp.write(html)
        tmp.close()
        path = tmp.name

    if serve:
        webbrowser.open(f"file://{path}")
        print(f"Opened {path}")
    else:
        print(f"Written to {path}")

    return path


# ── demo ───────────────────────────────────────────────────────────────

def demo():
    """Generate a sample graph to showcase the viewer."""

    class Animal:
        def __init__(self, name, friends=None):
            self.name = name
            self.friends = friends or []

    class Zoo:
        def __init__(self, animals):
            self.animals = animals
            self.index = {a.name: a for a in animals}

    cat = Animal("cat")
    dog = Animal("dog", friends=[cat])
    parrot = Animal("parrot", friends=[cat, dog])
    zoo = Zoo([cat, dog, parrot])

    print("Generating demo graph for Zoo object …")
    return show_refs(zoo, max_depth=4, extra_label="Zoo demo")


if __name__ == "__main__":
    demo()
