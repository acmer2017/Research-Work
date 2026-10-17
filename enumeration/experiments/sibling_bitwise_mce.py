#!/usr/bin/env python3
"""Semantic experiment for sibling bit-slicing and exact (P,X) factoring.

Uses Python integers, scalar packing and explicit prefix lists. This is not a
performance implementation, a concurrent implementation or a memory bound.
Only the standard library is required. See README.md for the output contract.
"""

import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path
import random


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def graph(n, edges):
    adj = [0] * n
    for u, v in edges:
        assert 0 <= u < n and 0 <= v < n and u != v
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def oracle(adj):
    """Examine every nonempty vertex subset, independently of BK's tree."""
    full = (1 << len(adj)) - 1
    out = []
    for chosen in range(1, full + 1):
        if any(chosen & ~(adj[v] | (1 << v)) for v in vertices(chosen)):
            continue
        extensions = full
        for v in vertices(chosen):
            extensions &= adj[v]
        if not extensions:
            out.append(chosen)
    return sorted(out)


def extension_order(adj, p, x):
    # The same deterministic maximum-score pivot is used in every algorithm.
    pivot = max(vertices(p | x), key=lambda v: ((p & adj[v]).bit_count(), -v))
    return list(vertices(p & ~adj[pivot]))


def serial_bk(adj):
    out = []
    nodes = 0

    def dfs(r, p, x):
        nonlocal nodes
        nodes += 1
        if not (p | x):
            out.append(r)
            return
        for q in extension_order(adj, p, x):
            bit = 1 << q
            dfs(r | bit, p & adj[q], x & adj[q])
            p &= ~bit
            x |= bit

    dfs(0, (1 << len(adj)) - 1, 0)
    return sorted(out), nodes


def bit_sliced_bk(adj, width, factor=False):
    """Depth-first batches of children, with vertex-major lane masks.

    A state is (prefixes, P, X). `factor` only groups exact (P,X) matches
    inside a batch. Multiple prefixes never become one clique by union.
    """
    assert 1 <= width <= 64
    n = len(adj)
    out = []
    stats = dict(physical_states=0, logical_states=0, batches=0,
                 packed_children=0, merged_states=0, max_prefix_labels=0)

    def intersect_children(descriptors):
        # Each descriptor has its own earlier-ext correction already applied.
        mp, mx, a = [0] * n, [0] * n, [0] * n
        for lane, (_, p, x, q) in enumerate(descriptors):
            flag = 1 << lane
            for v in vertices(p):
                mp[v] |= flag
            for v in vertices(x):
                mx[v] |= flag
            for v in vertices(adj[q]):
                a[v] |= flag
        for v in range(n):
            mp[v] &= a[v]
            mx[v] &= a[v]
        children = []
        for lane, (prefixes, _, _, _) in enumerate(descriptors):
            p = sum(1 << v for v in range(n) if mp[v] & (1 << lane))
            x = sum(1 << v for v in range(n) if mx[v] & (1 << lane))
            children.append((prefixes, p, x))
        stats['batches'] += 1
        stats['packed_children'] += len(descriptors)
        return children

    def visit(states):
        if factor:
            groups = defaultdict(list)
            for prefixes, p, x in states:
                groups[p, x].extend(prefixes)
            stats['merged_states'] += len(states) - len(groups)
            states = [(labels, p, x) for (p, x), labels in groups.items()]

        descriptors = []
        for prefixes, p, x in states:
            stats['physical_states'] += 1
            stats['logical_states'] += len(prefixes)
            stats['max_prefix_labels'] = max(stats['max_prefix_labels'], len(prefixes))
            if not (p | x):
                out.extend(prefixes)
                continue
            earlier = 0
            for q in extension_order(adj, p, x):
                bit = 1 << q
                labels = [r | bit for r in prefixes]
                descriptors.append((labels, p & ~earlier, x | earlier, q))
                earlier |= bit
                if len(descriptors) == width:
                    visit(intersect_children(descriptors))
                    descriptors = []
        if descriptors:
            visit(intersect_children(descriptors))

    visit([([0], (1 << n) - 1, 0)])
    return sorted(out), stats


def cases(exhaustive_n, random_cases, seed):
    for n in range(1, exhaustive_n + 1):
        possible = list(combinations(range(n), 2))
        for code in range(1 << len(possible)):
            yield 'exhaustive', graph(n, [e for i, e in enumerate(possible) if code >> i & 1])
    rng = random.Random(seed)
    for _ in range(random_cases):
        n = rng.randint(6, 10)
        density = rng.choice([0.05, 0.2, 0.5, 0.8, 0.95])
        yield 'random', graph(n, [e for e in combinations(range(n), 2)
                                  if rng.random() < density])


def validate(exhaustive_n, random_cases, widths, seed):
    checked = defaultdict(int)
    comparisons = 0
    for kind, adj in cases(exhaustive_n, random_cases, seed):
        expected = oracle(adj)
        baseline, nodes = serial_bk(adj)
        assert baseline == expected, (kind, adj, 'serial')
        assert len(baseline) == len(set(baseline))
        for width in widths:
            for factor in (False, True):
                actual, stats = bit_sliced_bk(adj, width, factor)
                assert actual == expected, (kind, adj, width, factor)
                assert len(actual) == len(set(actual)), 'duplicate result'
                assert stats['logical_states'] == nodes, 'changed canonical search'
                if not factor:
                    assert stats['physical_states'] == nodes
                comparisons += 1
        checked[kind] += 1

    examples = {}
    fixtures = {
        'triangle_with_leaf': graph(4, [(0, 1), (0, 2), (1, 2), (2, 3)]),
        'complete_graph_8': graph(8, list(combinations(range(8), 2))),
        'complete_3_partite_3_3_3': graph(9, [(u, v) for u, v in combinations(range(9), 2)
                                             if u // 3 != v // 3]),
    }
    for name, adj in fixtures.items():
        expected = oracle(adj)
        original, nodes = serial_bk(adj)
        item = dict(results=len(expected), output_vertex_ids=sum(r.bit_count() for r in expected),
                    serial_states=nodes)
        assert original == expected
        for factor in (False, True):
            result, stats = bit_sliced_bk(adj, max(widths), factor)
            assert result == expected and len(result) == len(set(result))
            assert stats['logical_states'] == nodes
            item['factored' if factor else 'bit_sliced'] = stats
        examples[name] = item
    return dict(seed=seed, exhaustive_up_to_n=exhaustive_n, cases=dict(checked),
                widths=widths, batched_result_comparisons=comparisons,
                passed=True, examples=examples,
                limitations=['Semantic validation only; no speedup measurements.',
                             'Explicit prefix lists may grow with output size.',
                             'No concurrency, SIMD intrinsic or GPU implementation.',
                             'No approximate-neighborhood grouping or work/span bound.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exhaustive-n', type=int, default=5, choices=range(1, 7))
    parser.add_argument('--random-cases', type=int, default=300)
    parser.add_argument('--widths', type=int, nargs='+', default=[1, 2, 4, 8, 64])
    parser.add_argument('--seed', type=int, default=20261017)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert all(1 <= w <= 64 for w in args.widths)
    report = validate(args.exhaustive_n, args.random_cases, args.widths, args.seed)
    encoded = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(encoded)
    print(encoded)


if __name__ == '__main__':
    main()
