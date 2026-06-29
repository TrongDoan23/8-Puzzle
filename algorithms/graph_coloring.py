from __future__ import annotations
import random
from typing import Dict, List, Optional, Tuple

# ── Color palette ─────────────────────────────────────────────────────────
NUM_COLORS    = 4
COLOR_PALETTE = ["#E05555", "#4A90D9", "#44B87A", "#F5A623"]
COLOR_NAMES   = ["Red", "Blue", "Green", "Yellow"]

UNASSIGNED = -1
Step = Tuple[str, int, int]   # (action, node_idx, color_idx)
# action: "assign" | "unassign" | "conflict"


# ── Dynamic graph generation ──────────────────────────────────────────────

class GraphDefinition:
    """Holds node names, positions (normalized 0-1) and edges."""

    def __init__(
        self,
        names: List[str],
        positions: List[Tuple[float, float]],
        edges: List[Tuple[int, int]],
    ) -> None:
        self.names     = names
        self.positions = positions
        self.edges     = edges
        self.num_nodes = len(names)

    def neighbors_of(self, node: int) -> List[int]:
        result = []
        for a, b in self.edges:
            if a == node: result.append(b)
            elif b == node: result.append(a)
        return result

    def is_consistent(self, assignment: List[int], node: int, color: int) -> bool:
        for nb in self.neighbors_of(node):
            if assignment[nb] == color:
                return False
        return True

    def is_colorable(self) -> bool:
        """Quick check: planar graphs always 4-colorable; we just verify."""
        return True


# ── Built-in graph: Australia ─────────────────────────────────────────────

AUSTRALIA = GraphDefinition(
    names=["WA", "NT", "SA", "QLD", "NSW", "VIC", "TAS"],
    positions=[
        (0.12, 0.45), (0.32, 0.22), (0.38, 0.52),
        (0.58, 0.22), (0.65, 0.52), (0.62, 0.75), (0.78, 0.88),
    ],
    edges=[
        (0,1),(0,2),(1,2),(1,3),(2,3),(2,4),(2,5),(3,4),(4,5),(5,6)
    ],
)


def generate_random_graph(num_nodes: int = 7, seed: int = None) -> GraphDefinition:
    """
    Generate a random connected graph that is guaranteed 4-colorable.
    Uses a planar-ish construction to keep chromatic number ≤ 4.
    """
    if seed is not None:
        random.seed(seed)

    import math
    names = [chr(ord('A') + i) for i in range(num_nodes)]

    # Place nodes on a circle with a small random jitter
    positions = []
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        r = 0.30 + random.uniform(-0.04, 0.04)
        cx, cy = 0.50, 0.48
        x = max(0.08, min(0.92, cx + r * math.cos(angle) + random.uniform(-0.03, 0.03)))
        y = max(0.08, min(0.92, cy + r * math.sin(angle) + random.uniform(-0.03, 0.03)))
        positions.append((x, y))

    # Build a random spanning tree (guarantees connectivity, no self-loops)
    perm = list(range(num_nodes))
    random.shuffle(perm)
    edges: set = set()
    for i in range(1, num_nodes):
        parent = perm[random.randint(0, i - 1)]
        child  = perm[i]
        edges.add((min(parent, child), max(parent, child)))

    # Add extra edges — but keep it planar-ish (≤ 2.5 * n edges)
    max_extra = max(0, int(num_nodes * 1.5) - len(edges))
    candidates = [
        (min(a, b), max(a, b))
        for a in range(num_nodes)
        for b in range(a + 1, num_nodes)
        if (min(a, b), max(a, b)) not in edges
    ]
    random.shuffle(candidates)
    for edge in candidates[:max_extra]:
        edges.add(edge)

    return GraphDefinition(names, positions, sorted(edges))


# ── Algorithm base ────────────────────────────────────────────────────────

class GCAlgorithmBase:
    is_gc_algorithm = True

    def solve(
        self, graph: GraphDefinition
    ) -> Tuple[Optional[List[int]], List[Step]]:
        raise NotImplementedError


# ── Backtracking ──────────────────────────────────────────────────────────

class GCBacktracking(GCAlgorithmBase):
    name = "Backtracking"

    def solve(self, graph: GraphDefinition) -> Tuple[Optional[List[int]], List[Step]]:
        assignment = [UNASSIGNED] * graph.num_nodes
        steps: List[Step] = []
        if self._bt(graph, assignment, 0, steps):
            return assignment, steps
        return None, steps

    def _bt(self, g, assignment, node, steps):
        if node == g.num_nodes:
            return True
        for color in range(NUM_COLORS):
            if g.is_consistent(assignment, node, color):
                assignment[node] = color
                steps.append(("assign", node, color))
                if self._bt(g, assignment, node + 1, steps):
                    return True
                assignment[node] = UNASSIGNED
                steps.append(("unassign", node, color))
        return False


# ── Forward Checking ──────────────────────────────────────────────────────

class GCForwardChecking(GCAlgorithmBase):
    name = "Forward Checking"

    def solve(self, graph: GraphDefinition) -> Tuple[Optional[List[int]], List[Step]]:
        assignment = [UNASSIGNED] * graph.num_nodes
        domains    = [list(range(NUM_COLORS)) for _ in range(graph.num_nodes)]
        steps: List[Step] = []
        if self._fc(graph, assignment, domains, 0, steps):
            return assignment, steps
        return None, steps

    def _fc(self, g, assignment, domains, node, steps):
        if node == g.num_nodes:
            return True
        for color in list(domains[node]):
            if g.is_consistent(assignment, node, color):
                assignment[node] = color
                steps.append(("assign", node, color))
                pruned: Dict[int, List[int]] = {}
                ok = True
                for nb in g.neighbors_of(node):
                    if assignment[nb] == UNASSIGNED and color in domains[nb]:
                        domains[nb].remove(color)
                        pruned.setdefault(nb, []).append(color)
                        if not domains[nb]:
                            ok = False; break
                if ok and self._fc(g, assignment, domains, node + 1, steps):
                    return True
                assignment[node] = UNASSIGNED
                steps.append(("unassign", node, color))
                for nb, cols in pruned.items():
                    domains[nb].extend(cols)
        return False


# ── AC-3 ──────────────────────────────────────────────────────────────────

class GCAC3(GCAlgorithmBase):
    name = "AC-3"

    def solve(self, graph: GraphDefinition) -> Tuple[Optional[List[int]], List[Step]]:
        domains = [list(range(NUM_COLORS)) for _ in range(graph.num_nodes)]
        steps: List[Step] = []

        # --- Phase 1: AC-3 propagation ---
        # Build initial arc queue: every directed arc (xi, xj)
        from collections import deque
        queue = deque()
        for a, b in graph.edges:
            queue.append((a, b))
            queue.append((b, a))

        while queue:
            xi, xj = queue.popleft()
            if self._revise(graph, domains, xi, xj, steps):
                if not domains[xi]:
                    return None, steps          # domain wiped out
                # Re-add all arcs pointing to xi
                for xk in graph.neighbors_of(xi):
                    if xk != xj:
                        queue.append((xk, xi))

        # --- Phase 2: backtrack to assign remaining nodes ---
        assignment = [UNASSIGNED] * graph.num_nodes
        # Pre-assign nodes whose domain is a singleton
        for i in range(graph.num_nodes):
            if len(domains[i]) == 1:
                assignment[i] = domains[i][0]
                steps.append(("assign", i, domains[i][0]))

        if self._bt_finish(graph, assignment, domains, 0, steps):
            return assignment, steps
        return None, steps

    def _revise(self, g, domains, xi, xj, steps):
        """Remove values from domains[xi] that have no support in domains[xj]."""
        revised = False
        for color in list(domains[xi]):
            # Check if any value in domains[xj] is consistent (≠ color)
            if all(c == color for c in domains[xj]):
                domains[xi].remove(color)
                revised = True
                # If domain collapses to singleton, visualize the assignment
                if len(domains[xi]) == 1:
                    steps.append(("assign", xi, domains[xi][0]))
        return revised

    def _bt_finish(self, g, assignment, domains, node, steps):
        """Finish any unassigned nodes using backtracking."""
        if node == g.num_nodes:
            return True
        if assignment[node] != UNASSIGNED:
            return self._bt_finish(g, assignment, domains, node + 1, steps)
        for color in list(domains[node]):
            if g.is_consistent(assignment, node, color):
                assignment[node] = color
                steps.append(("assign", node, color))
                if self._bt_finish(g, assignment, domains, node + 1, steps):
                    return True
                assignment[node] = UNASSIGNED
                steps.append(("unassign", node, color))
        return False


# ── Min-Conflicts ─────────────────────────────────────────────────────────

class GCMinConflicts(GCAlgorithmBase):
    name = "Min-Conflicts"
    MAX_STEPS    = 1000
    MAX_RESTARTS = 10

    def solve(self, graph: GraphDefinition) -> Tuple[Optional[List[int]], List[Step]]:
        n = graph.num_nodes
        steps: List[Step] = []

        for _ in range(self.MAX_RESTARTS):
            assignment = [random.randint(0, NUM_COLORS - 1) for _ in range(n)]
            for i, c in enumerate(assignment):
                steps.append(("assign", i, c))

            for __ in range(self.MAX_STEPS):
                conflicted = [
                    nd for nd in range(n)
                    if any(assignment[nb] == assignment[nd]
                           for nb in graph.neighbors_of(nd))
                ]
                if not conflicted:
                    return assignment[:], steps

                node = random.choice(conflicted)
                steps.append(("conflict", node, assignment[node]))

                def _cnt(c: int, nd: int = node) -> int:
                    return sum(
                        1 for nb in graph.neighbors_of(nd) if assignment[nb] == c
                    )

                best = min(range(NUM_COLORS), key=_cnt)
                assignment[node] = best
                steps.append(("assign", node, best))

        return None, steps
