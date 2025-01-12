from collections import deque
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Set

LOGGER = logging.getLogger("[G]")


@dataclass
class Graph:
    adj: Dict[int, Set[int]] = field(default_factory=dict)

    def add_edge(self, u: int, v: int) -> None:
        if u not in self.adj:
            self.adj[u] = set()
        if v not in self.adj:
            self.adj[v] = set()
        if v in self.adj[u]:
            # Already have the better edge
            return
        self.adj[u].add(v)

    def get_edges(self, u: int) -> Set[int]:
        if u in self.adj:
            return self.adj[u]
        return set()

    def get_leaves(self, u: int) -> List[int]:
        result = []
        in_ = set({u})
        q = deque([u])
        while len(q) > 0:
            u = q.popleft()
            edges = self.get_edges(u)
            if not edges:
                result += [u]
                continue
            LOGGER.info(f"{u} popped out!")
            for v in edges:
                if v not in in_:
                    in_.add(v)
                    q.append(v)
        return result
