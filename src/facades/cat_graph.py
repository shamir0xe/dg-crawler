from typing import Dict
from src.datastructure.graph.graph import Graph
from src.helpers.decorators.singleton import singleton


@singleton
class CatGraph:
    def __init__(self) -> None:
        self.g = Graph()

    def build_graph(self, data: Dict) -> None:
        if not "data" in data:
            raise Exception("Not a valid graph data")
        for key, value in data["data"].items():
            try:
                u = int(key)
            except Exception:
                continue
            if "parent_ids" in value:
                for parent in value["parent_ids"]:
                    try:
                        v = int(parent)
                    except Exception:
                        continue
                    self.g.add_edge(v, u)
            if "children" in value:
                for child in value["children"]:
                    try:
                        v = int(child)
                    except Exception:
                        continue
                    self.g.add_edge(u, v)
