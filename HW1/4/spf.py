#!/usr/bin/env python
import json


import collections
import heapq

def shortestPath_cal(edges, source, sink):
    # create a weighted DAG - {node:[(cost,neighbour), ...]}
    graph = collections.defaultdict(list)
    for l, r, c in edges:
        graph[l].append((c,r))
    # create a priority queue and hash set to store visited nodes
    queue, visited = [(0, source, [])], set()
    heapq.heapify(queue)
    # traverse graph with BFS
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        # visit the node if it was not visited before
        if node not in visited:
            visited.add(node)
            path = path + [node]
            # hit the sink
            if node == sink:
                return (cost, path)
            # visit neighbours
            for c, neighbour in graph[node]:
                if neighbour not in visited:
                    heapq.heappush(queue, (cost+c, neighbour, path))
    return float("inf")



def shortestPath(g):
    l = len(g)

    edges = []

    # append edges
    for i in range(l):
        for j in range(l):
            if g[i][j]!=0: edges.append((i+1, j+1, g[i][j]))

    # calculate path
    path_map = {}
    for i in range(l):
        path = {}
        for j in range(l):
            path[str(j+1)] = shortestPath_cal(edges,i+1,j+1)[1]
        path_map[str(i+1)] = path

    # dump paths
    with open('./spf.json', 'w') as f:
        json.dump(path_map, f)

    return path_map