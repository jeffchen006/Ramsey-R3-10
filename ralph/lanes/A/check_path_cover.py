#!/usr/bin/env python3
"""Reconstruct C's P4 cover without importing its generator or using its joins."""

import argparse
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
from check_graph import alpha, parse_graph6, to_graph6, triangle_free


@dataclass(frozen=True)
class Layout:
    core: int
    side: int
    census_size: int
    window_alpha: int
    edges_lo: int
    edges_hi: int
    deg_lo: int
    deg_hi: int
    codegree: int

    @property
    def size(self):
        return self.core + 2 * self.side + 2


CONTROL = Layout(7, 1, 3, 3, 15, 19, 2, 4, 4)
TARGET = Layout(20, 2, 191, 6, 73, 81, 3, 7, 6)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def canonical(records, labelg):
    if not records:
        return []
    process = subprocess.run([labelg, "-q"], input="\n".join(records) + "\n",
                             text=True, stdout=subprocess.PIPE, check=True)
    output = process.stdout.splitlines()
    if len(output) != len(records):
        raise ValueError("labelg did not return one label per graph")
    return output


def induced(adj, vertices):
    translated = {old: new for new, old in enumerate(vertices)}
    return tuple(sum(1 << translated[other] for other in bits(adj[old]) if other in translated)
                 for old in vertices)


@lru_cache(maxsize=65536)
def refine(adj):
    neighbors = [tuple(bits(row)) for row in adj]
    colors = [0] * len(adj)
    while True:
        signatures = [(colors[index], tuple(sorted(colors[v] for v in row)))
                      for index, row in enumerate(neighbors)]
        palette = {key: index for index, key in enumerate(sorted(set(signatures)))}
        new_colors = [palette[signature] for signature in signatures]
        if new_colors == colors:
            return tuple(colors), tuple(sorted(signatures))
        colors = new_colors


def all_maps(source, target):
    source_colors, source_sig = refine(source)
    target_colors, target_sig = refine(target)
    if source_sig != target_sig:
        return
    order = len(target)
    pools = [sum(1 << vertex for vertex in range(order) if target_colors[vertex] == color)
             for color in source_colors]
    schedule = sorted(range(order), key=lambda vertex: pools[vertex].bit_count())
    image = [-1] * order
    singletons = sum(pool.bit_count() == 1 for pool in pools)
    fixed = schedule[:singletons]
    used = 0
    for vertex in fixed:
        image[vertex] = pools[vertex].bit_length() - 1
        used |= pools[vertex]
    if any(((source[first] >> second) ^ (target[image[first]] >> image[second])) & 1
           for first, second in combinations(fixed, 2)):
        return

    def extend(index, used):
        if index == order:
            yield tuple(image)
            return
        source_vertex = schedule[index]
        options = pools[source_vertex] & ~used
        for previous in schedule[:index]:
            adjacent = target[image[previous]]
            options &= adjacent if (source[source_vertex] >> previous) & 1 else ~adjacent
        for target_vertex in bits(options):
            image[source_vertex] = target_vertex
            yield from extend(index + 1, used | (1 << target_vertex))

    yield from extend(singletons, used)


def assert_distinct(graphs):
    buckets = defaultdict(list)
    for adj in graphs:
        collision = buckets[refine(adj)[1]]
        if any(next(all_maps(adj, other), None) is not None for other in collision):
            raise ValueError("isomorphic graphs assigned different catalogue keys")
        collision.append(adj)


def map_side(masks, mapping):
    return tuple(sorted(sum(1 << mapping[vertex] for vertex in bits(mask)) for mask in masks))


def window_types(census_path, labelg, layout, sample):
    originals = census_path.read_text().splitlines()
    census = [tuple(parse_graph6(line)) for line in originals]
    if len(census) != layout.census_size:
        raise ValueError("wrong census cardinality")
    assert_distinct(census)
    marked_windows = []
    for adj in census:
        if (len(adj) != layout.core + layout.side or not triangle_free(adj)
                or alpha(adj) > layout.window_alpha):
            raise ValueError("invalid census member")
        for marked in combinations(range(len(adj)), layout.side):
            if any((adj[first] >> second) & 1 or (adj[first] & adj[second]).bit_count() >= layout.codegree
                   for first, second in combinations(marked, 2)):
                continue
            core_vertices = [vertex for vertex in range(len(adj)) if vertex not in marked]
            core = induced(adj, core_vertices)
            marks = tuple(sum(1 << index for index, target in enumerate(core_vertices) if (adj[vertex] >> target) & 1)
                          for vertex in marked)
            marked_windows.append((core, marks))
    unique_cores = sorted({core for core, _ in marked_windows})
    labels = dict(zip(unique_cores, canonical([to_graph6(core) for core in unique_cores], labelg)))
    representatives = {label: tuple(parse_graph6(label)) for label in set(labels.values())}
    assert_distinct(representatives.values())
    selected = sorted(representatives)
    if sample:
        selected = [selected[index * len(selected) // sample] for index in range(min(sample, len(selected)))]
    accepted = set(selected)
    grouped = defaultdict(set)
    for core, marked in marked_windows:
        if labels[core] in accepted:
            grouped[core].add(marked)
    side_types = defaultdict(set)
    for core, marks in grouped.items():
        label = labels[core]
        mappings = False
        for mapping in all_maps(core, representatives[label]):
            mappings = True
            side_types[label].update(map_side(marked, mapping) for marked in marks)
        if not mappings:
            raise ValueError("marked-core representative lacks a verified isomorphism")
    print(f"census {len(census)}; marked placements {len(marked_windows)}; "
          f"core classes {'up to ' if sample else ''}{len(representatives)}; replayed {len(selected)}", flush=True)
    return [(representatives[label], sorted(side_types[label])) for label in selected]


def joined(core, first, second, layout):
    if first > second:
        raise ValueError("sides must be in canonical order")
    root_first, root_last = layout.size - 2, layout.size - 1
    first_vertices = range(layout.core, layout.core + layout.side)
    second_vertices = range(layout.core + layout.side, root_first)
    occupied = list(core) + [0] * (layout.size - layout.core)

    def insert(adj, source, target):
        adj[source] |= 1 << target
        adj[target] |= 1 << source

    insert(occupied, root_first, root_last)
    for vertex, mask in zip(range(layout.core, root_first), first + second):
        insert(occupied, vertex, root_last if vertex in first_vertices else root_first)
        for neighbor in bits(mask):
            insert(occupied, vertex, neighbor)
    if any(not layout.deg_lo <= row.bit_count() <= layout.deg_hi for row in occupied[:layout.core]):
        return
    base_edges = sum(row.bit_count() for row in occupied) // 2
    legal_edges = [(source, target) for source in first_vertices for target in second_vertices
                   if not (occupied[source] & occupied[target])]
    for count in range(max(0, layout.edges_lo - base_edges),
                       min(len(legal_edges), layout.edges_hi - base_edges) + 1):
        for optional in combinations(legal_edges, count):
            adj = occupied.copy()
            for source, target in optional:
                insert(adj, source, target)
            if any(not layout.deg_lo <= row.bit_count() <= layout.deg_hi for row in adj[layout.core:]):
                continue
            if any((adj[source] & adj[target]).bit_count() > layout.codegree
                   for source, target in combinations(range(layout.size), 2)):
                continue
            if alpha(adj) <= layout.window_alpha + 1:
                yield to_graph6(adj)


def planted_paths(results, labelg):
    adj = tuple(sum(1 << ((vertex + offset) % 21) for offset in (-6, -4, -1, 1, 4, 6))
                for vertex in range(21))
    if not triangle_free(adj) or alpha(adj) != 6:
        raise ValueError("bad planted C21 control")
    residues = []
    for start in range(21):
        for step in (-5, 5):
            path = [(start + step * index) % 21 for index in range(4)]
            if any((adj[first] & adj[second]).bit_count() != 4 for first, second in zip(path, path[1:])):
                raise ValueError("bad codegree along the planted path")
            middle_left, middle_right = path[1:3]
            closed = adj[middle_left] | adj[middle_right] | (1 << middle_left) | (1 << middle_right)
            residues.append(to_graph6(induced(adj, list(bits(((1 << 21) - 1) ^ closed)))))
    if not set(canonical(residues, labelg)) <= set(canonical(sorted(results), labelg)):
        raise ValueError("a planted C21 path residue is missing from reconstruction")
    print(f"PASS planted paths {len(residues)}/{len(residues)}", flush=True)


def check_list(results, catalogue):
    listed = catalogue.read_text().splitlines()
    actual = set(listed)
    extra = actual - results
    missing = results - actual
    if extra or missing:
        raise ValueError(f"cover mismatch: missing={len(missing)} extraneous={len(extra)} "
                         f"first missing={min(missing, default='-')} first extraneous={min(extra, default='-')}")
    if listed != sorted(actual):
        raise ValueError("duplicate or unsorted cover rows")
    print(f"PASS exact set: {len(results)} rows, input SHA-256 {sha256(catalogue.read_bytes()).hexdigest()}")


def main():
    flags = argparse.ArgumentParser(description=__doc__)
    flags.add_argument("census", type=Path)
    flags.add_argument("catalogue", type=Path, nargs="?")
    flags.add_argument("--labelg", required=True)
    flags.add_argument("--control", action="store_true")
    flags.add_argument("--sample", type=int, default=0)
    flags.add_argument("--output", type=Path)
    args = flags.parse_args()
    if args.sample < 0 or (args.sample and args.control):
        flags.error("use a positive target sample or an exhaustive control")
    layout = CONTROL if args.control else TARGET
    results = set()
    for core, side_types in window_types(args.census, args.labelg, layout, args.sample):
        for first, second in combinations_with_replacement(side_types, 2):
            results.update(joined(core, first, second, layout))
    if args.control:
        planted_paths(results, args.labelg)
    if args.catalogue is not None:
        check_list(results, args.catalogue)
    if args.output is not None:
        args.output.write_text("".join(line + "\n" for line in sorted(results)))
    print(f"{'SAMPLE' if args.sample else 'FULL'} reconstructed rows {len(results)}")


if __name__ == "__main__":
    main()
