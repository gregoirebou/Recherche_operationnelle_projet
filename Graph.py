from collections import deque


class Graph:
    def __init__(self, verbose=True):
        self.graph = {}
        self.verbose = verbose

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, start, end, weight):
        self.add_vertex(start)
        self.add_vertex(end)
        self.graph[start].append((end, weight))
        self.graph[end].append((start, weight))

    def remove_edge(self, start, end):
        if start in self.graph:
            self.graph[start] = [(n, w) for n, w in self.graph[start] if n != end]
        if end in self.graph:
            self.graph[end] = [(n, w) for n, w in self.graph[end] if n != start]

    def _bfs(self, start):
        visited = {start: None}
        queue = deque([start])
        cycle = None
        while queue:
            node = queue.popleft()
            for neighbor, _ in self.graph[node]:
                if neighbor not in visited:
                    visited[neighbor] = node
                    queue.append(neighbor)
                elif visited[node] != neighbor and cycle is None:
                    cycle = (node, neighbor)
        return visited, cycle

    def is_connected(self):
        if not self.graph:
            return True
        start = next(iter(self.graph))
        visited, _ = self._bfs(start)
        if len(visited) == len(self.graph):
            if self.verbose:
                print("Proposition connexe")
            return True
        components = self.get_connected_components()
        if self.verbose:
            print(f"Proposition non connexe : {len(components)} sous-graphes")
            for idx, comp in enumerate(components):
                print(f"  Sous-graphe {idx + 1} : {comp}")
        return False

    def is_acyclic(self):
        if not self.graph:
            return True
        start = next(iter(self.graph))
        _, cycle = self._bfs(start)
        if self.verbose:
            if cycle:
                print(f"Cycle détecté entre {cycle[0]} et {cycle[1]}")
            else:
                print("Proposition acyclique")
        return cycle is None

    def get_connected_components(self):
        unvisited = set(self.graph.keys())
        components = []
        while unvisited:
            start = next(iter(unvisited))
            visited, _ = self._bfs(start)
            comp = set(visited.keys())
            components.append(comp)
            unvisited -= comp
        return components

    def find_cycle(self):
        if not self.graph:
            return None

        start = next(iter(self.graph))
        visited = {start: None}
        queue = deque([start])
        cycle_edge = None

        while queue and not cycle_edge:
            node = queue.popleft()
            for neighbor, _ in self.graph[node]:
                if neighbor not in visited:
                    visited[neighbor] = node
                    queue.append(neighbor)
                elif visited[node] != neighbor:
                    cycle_edge = (node, neighbor)
                    break

        if not cycle_edge:
            return None

        def path_to_root(node):
            path = []
            while node is not None:
                path.append(node)
                node = visited[node]
            return path

        path_a = path_to_root(cycle_edge[0])
        path_b = path_to_root(cycle_edge[1])

        set_a = {n: i for i, n in enumerate(path_a)}
        for i, n in enumerate(path_b):
            if n in set_a:
                return path_a[:set_a[n] + 1] + path_b[:i][::-1]

        return None
