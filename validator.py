# Independent check of a colouring. It does NOT trust the scheduler: it rebuilds
# the conflict pairs from the raw subject sets and confirms no conflicting pair
# shares a slot. Returns (is_valid, [violations]).
from graph_builder import conflicts


def validate(subjects, color):
    problems = []
    for a, b, shared in conflicts(subjects):
        if color[a] == color[b]:
            problems.append((a, b, shared))
    return len(problems) == 0, problems
