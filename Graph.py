class Graph:
    def __init__(self):
        self.graph = {}

    def add_vertex(self, vertex):
        if vertex not in self.graph:
            self.graph[vertex] = []

    def add_edge(self, start, end, weight):
        self.add_vertex(start)
        self.add_vertex(end)
        self.graph[start].append((end, weight))
        self.graph[end].append((start, weight))  # non orienté

    def bfs(self, start):
        visited = {start: None}  # sommet: parent
        queue = [start]
        cycle = None
        while queue:
            node = queue.pop(0)
            for neighbor, _ in self.graph[node]:
                if neighbor not in visited:
                    visited[neighbor] = node
                    queue.append(neighbor)
                elif visited[node] != neighbor:
                    cycle = (node, neighbor)
        return visited, cycle

    def is_connected(self):
        start = next(iter(self.graph))
        visited, _ = self.bfs(start)
        if len(visited) == len(self.graph):
            print("Proposition connexe")
            return True
        components = self.get_connected_components()
        print(f"Proposition non connexe : {len(components)} sous-graphes")
        for idx, comp in enumerate(components):
            print(f"  Sous-graphe {idx + 1} : {comp}")
        return False

    def is_acyclic(self):
        start = next(iter(self.graph))
        visited, cycle = self.bfs(start)
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
            visited, _ = self.bfs(start)
            components.append(set(visited.keys()))
            unvisited -= set(visited.keys())
        return components

    def find_cycle(self):
        """Retourne le cycle complet sous forme de liste de sommets."""
        start = next(iter(self.graph))
        visited = {start: None}
        queue = [start]
        cycle_edge = None

        while queue and not cycle_edge:
            node = queue.pop(0)
            for neighbor, _ in self.graph[node]:
                if neighbor not in visited:
                    visited[neighbor] = node
                    queue.append(neighbor)
                elif visited[node] != neighbor:
                    cycle_edge = (node, neighbor)
                    break

        if not cycle_edge:
            return None

        # Reconstruire le chemin de chaque nœud jusqu'à la racine
        def path_to_root(node):
            path = []
            while node is not None:
                path.append(node)
                node = visited[node]
            return path

        path_a = path_to_root(cycle_edge[0])
        path_b = path_to_root(cycle_edge[1])

        # Trouver l'ancêtre commun
        set_a = {n: i for i, n in enumerate(path_a)}
        for i, n in enumerate(path_b):
            if n in set_a:
                return path_a[:set_a[n] + 1] + path_b[:i][::-1]

