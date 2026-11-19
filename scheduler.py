# Greedy graph colouring. Colours become examination time slots.
# Order vertices by descending degree (alphabetical tie-break so the result
# is fixed), then give each vertex the smallest colour no neighbour already has.
# Greedy gives a VALID colouring, not necessarily the fewest colours.
from graph_builder import adjacency, conflicts, degrees


def order_by_degree(adj):
    deg = degrees(adj)
    return sorted(adj, key=lambda v: (-deg[v], v))


def greedy_color(adj):
    color = {}
    for v in order_by_degree(adj):
        used = {color[n] for n in adj[v] if n in color}
        c = 1
        while c in used:
            c += 1
        color[v] = c
    return color


def by_slot(color):
    """Group subjects by their colour/slot: slot number -> sorted subjects."""
    groups = {}
    for subject, c in color.items():
        groups.setdefault(c, []).append(subject)
    return {c: sorted(v) for c, v in groups.items()}


def schedule(subjects):
    """Run the whole scheduling step: build graph, colour it. Returns adj, color."""
    adj = adjacency(subjects)
    return adj, greedy_color(adj)


if __name__ == "__main__":
    from sample_data import SUBJECTS
    from validator import validate

    adj = adjacency(SUBJECTS)
    deg = degrees(adj)
    color = greedy_color(adj)
    pairs = conflicts(SUBJECTS)

    print("Subjects :", len(SUBJECTS))
    print("Students :", len({s for v in SUBJECTS.values() for s in v}))
    print("Conflicts:", len(pairs))
    print("\nConflict pairs (subject A, subject B, shared students):")
    for a, b, shared in pairs:
        print("  %-12s <-> %-12s  %s" % (a, b, shared))
    print("\nVertex degrees:")
    for v in order_by_degree(adj):
        print("  %-12s degree %d" % (v, deg[v]))
    print("  Handshaking check: sum(deg) = %d, edges = %d" % (sum(deg.values()), len(pairs)))
    print("\nGreedy colouring (subject -> slot):")
    for v in order_by_degree(adj):
        print("  %-12s slot %d" % (v, color[v]))
    print("\nSlots used:", max(color.values()))
    ok, probs = validate(SUBJECTS, color)
    print("Valid (no conflict shares a slot):", ok)
    if probs:
        print("Violations:", probs)

