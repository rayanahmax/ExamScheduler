# Builds the conflict graph from "subject -> set of students".
# Two subjects conflict when their student sets intersect (A n B != empty).
# Pure standard library, no UI.
from itertools import combinations


def conflicts(subjects):
    """Every conflicting pair as (a, b, [shared students]), in a fixed order."""
    out = []
    for a, b in combinations(sorted(subjects), 2):
        shared = subjects[a] & subjects[b]
        if shared:
            out.append((a, b, sorted(shared)))
    return out


def adjacency(subjects):
    """Undirected graph as an adjacency list: subject -> set of conflicting subjects."""
    adj = {s: set() for s in subjects}
    for a, b, _ in conflicts(subjects):
        adj[a].add(b)
        adj[b].add(a)
    return adj


def degrees(adj):
    """Degree of each vertex = number of subjects it conflicts with."""
    return {v: len(adj[v]) for v in adj}
