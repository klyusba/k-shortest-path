# -*- coding: utf-8 -*-
"""
A NetworkX based implementation of Yen's algorithm for computing K-shortest paths.
Yen's algorithm computes single-source K-shortest loopless paths for a
graph with non-negative edge cost. For more details, see:
http://en.m.wikipedia.org/wiki/Yen%27s_algorithm
"""
__author__ = 'Guilherme Maia <guilhermemm@gmail.com>'

__all__ = ['k_shortest_paths']

from heapq import heappush, heappop
from itertools import count

import networkx as nx


def k_shortest_paths(G, source, target, k=1, weight='weight'):
    """Returns the k-shortest paths from source to target in a weighted graph G.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node

    target : node
       Ending node

    k : integer, optional (default=1)
        The number of shortest paths to find

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight

    Returns
    -------
    lengths, paths : lists
       Returns a tuple with two lists.
       The first list stores the length of each k-shortest path.
       The second list stores each k-shortest path.

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    Examples
    --------
    >>> G=nx.complete_graph(5)
    >>> print(k_shortest_paths(G, 0, 4, 4))
    ([1, 2, 2, 2], [[0, 4], [0, 1, 4], [0, 2, 4], [0, 3, 4]])

    Notes
    ------
    Edge weight attributes must be numerical and non-negative.
    Distances are calculated as sums of weighted edges traversed.

    """
    if source == target:
        return [0, ], [[source, ]]

    length, path = nx.single_source_dijkstra(G, source, target, weight=weight)
    lengths = [length, ]
    paths = [path, ]
    c = count()
    B = []

    for i in range(1, k):
        for j in range(len(paths[-1]) - 1):
            spur_node = paths[-1][j]
            root_path = paths[-1][:j + 1]

            edges_removed = []
            for c_path in paths:
                if len(c_path) > j and root_path == c_path[:j + 1]:
                    u = c_path[j]
                    v = c_path[j + 1]
                    if G.has_edge(u, v):
                        edge_attr = G.edges[u, v]
                        G.remove_edge(u, v)
                        edges_removed.append((u, v, edge_attr))

            for n in range(len(root_path) - 1):
                node = root_path[n]
                # out-edges
                for v in list(G.successors(node)):  # change in iterations
                    edge_attr = G.edges[node, v]
                    G.remove_edge(node, v)
                    edges_removed.append((node, v, edge_attr))

                if G.is_directed():
                    # in-edges
                    for u in list(G.predecessors(node)):  # change in iterations
                        edge_attr = G.edges[u, node]
                        G.remove_edge(u, node)
                        edges_removed.append((u, node, edge_attr))

            try:
                spur_path_length, spur_path = nx.single_source_dijkstra(G, spur_node, target, weight=weight)
            except nx.NetworkXNoPath:
                spur_path_length, spur_path = 0, []

            G.add_edges_from(edges_removed)
            if spur_path:
                total_path = root_path[:-1] + spur_path
                total_path_length = get_path_length(G, root_path, weight) + spur_path_length
                heappush(B, (total_path_length, next(c), total_path))

        if B:
            (l, _, p) = heappop(B)
            lengths.append(l)
            paths.append(p)
        else:
            break

    return lengths, paths


def get_path_length(G, path, weight='weight'):
    length = 0
    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        length += G.edges[u, v].get(weight, 1)

    return length
