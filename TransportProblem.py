from Graph import Graph
from collections import deque
import heapq


class TransportProblem:

    def __init__(self, file=None, from_data=None, verbose=True):
        self.n = 0
        self.m = 0
        self.couts = []
        self.provisions = []
        self.commandes = []
        self.proposition = []
        self.graph = None
        self.base = None
        self.verbose = verbose

        if file is not None:
            self.load_from_file(file)
        elif from_data is not None:
            self.n, self.couts, self.provisions, self.commandes = from_data
            self.m = self.n
            self.proposition = [[0] * self.m for _ in range(self.n)]
            self.graph = self._build_graph()
        else:
            raise ValueError("Veuillez fournir soit 'file' soit 'from_data'")

        self.t_couts = [list(col) for col in zip(*self.couts)]

    def load_from_file(self, filepath):
        with open(f"TransportFiles/{filepath}", 'r') as f:
            lignes = f.readlines()
        self.n, self.m = map(int, lignes[0].split())
        if len(lignes) < self.n + 2:
            raise ValueError(f"Fichier trop court : {len(lignes)} lignes pour {self.n} fournisseurs")
        for i in range(1, self.n + 1):
            valeurs = list(map(int, lignes[i].split()))
            self.couts.append(valeurs[:self.m])
            self.provisions.append(valeurs[self.m])
        self.commandes = list(map(int, lignes[self.n + 1].split()))
        self.proposition = [[0] * self.m for _ in range(self.n)]
        self.graph = self._build_graph()

    def __str__(self):
        lignes = []
        header = "       " + "  ".join(f"{'C'+str(j+1):>5}" for j in range(self.m)) + "  | Provisions"
        lignes.append(header)
        lignes.append("-" * len(header))
        for i in range(self.n):
            row = f"P{i + 1:<4}  " + "  ".join(f"{self.couts[i][j]:>5}" for j in range(self.m))
            row += f"  | {self.provisions[i]}"
            lignes.append(row)
        lignes.append("-" * len(header))
        lignes.append("Cmd    " + "  ".join(f"{self.commandes[j]:>5}" for j in range(self.m)))
        if any(self.proposition[i][j] != 0 for i in range(self.n) for j in range(self.m)):
            lignes.append("\nProposition :")
            lignes.append("       " + "  ".join(f"{'C'+str(j+1):>5}" for j in range(self.m)))
            for i in range(self.n):
                row = f"P{i + 1:<4}  " + "  ".join(f"{self.proposition[i][j]:>5}" for j in range(self.m))
                lignes.append(row)
        return "\n".join(lignes)

    def _build_graph(self):
        """Build graph from scratch (called once)."""
        g = Graph(verbose=self.verbose)
        source = self.base if self.base else {
            (i, j) for i in range(self.n) for j in range(self.m)
            if self.proposition[i][j] > 0
        }
        for i, j in source:
            g.add_edge(('P', i), ('C', j), self.proposition[i][j])
        return g

    # kept for backward-compat if anything external calls it
    def to_graph(self):
        return self._build_graph()

    def is_acyclic(self):
        return self._build_graph().is_acyclic()

    def NorthWest(self):
        cmd = self.commandes.copy()
        provisions = self.provisions.copy()
        i, j = 0, 0
        while i < self.n and j < self.m:
            val = min(cmd[j], provisions[i])
            self.proposition[i][j] = val
            cmd[j] -= val
            provisions[i] -= val
            if provisions[i] == 0:
                i += 1
            if cmd[j] == 0:
                j += 1

    def _get_capacity_row(self, i, active_cols, cmd, provisions):
        j_min = min(active_cols, key=lambda j: self.couts[i][j])
        return min(provisions[i], cmd[j_min]), j_min

    def _get_capacity_col(self, j, active_rows, cmd, provisions):
        i_min = min(active_rows, key=lambda i: self.t_couts[j][i])
        return min(provisions[i_min], cmd[j]), i_min

    def BalasHammer(self):
        cmd = self.commandes.copy()
        provisions = self.provisions.copy()
        active_rows = set(range(self.n))
        active_cols = set(range(self.m))
        penalty_row = [0] * self.n
        penalty_col = [0] * self.m

        while active_rows and active_cols:
            for i in active_rows:
                couts_dispo = [self.couts[i][j] for j in active_cols]
                if len(couts_dispo) < 2:
                    penalty_row[i] = 0
                else:
                    s = heapq.nsmallest(2, couts_dispo)
                    penalty_row[i] = s[1] - s[0]

            for j in active_cols:
                couts_dispo = [self.t_couts[j][i] for i in active_rows]
                if len(couts_dispo) < 2:
                    penalty_col[j] = 0
                else:
                    s = heapq.nsmallest(2, couts_dispo)
                    penalty_col[j] = s[1] - s[0]

            if self.verbose:
                print(f"Pénalités lignes : {penalty_row}")
                print(f"Pénalités colonnes : {penalty_col}")

            max_row_val = max(penalty_row[i] for i in active_rows)
            max_col_val = max(penalty_col[j] for j in active_cols)
            max_penalty = max(max_row_val, max_col_val)

            row_candidates = [i for i in active_rows if penalty_row[i] == max_penalty]
            col_candidates = [j for j in active_cols if penalty_col[j] == max_penalty]

            if self.verbose:
                print(f"Pénalité maximale : {max_penalty}")
                print(f"Candidats lignes : {row_candidates}, Candidats colonnes : {col_candidates}")

            all_candidates = []
            for i in row_candidates:
                all_candidates.append((0, i, *self._get_capacity_row(i, active_cols, cmd, provisions)))
            for j in col_candidates:
                all_candidates.append((1, j, *self._get_capacity_col(j, active_rows, cmd, provisions)))

            best_type, best_index, val_max, other_index = max(all_candidates, key=lambda x: x[2])

            if best_type == 1:
                self.proposition[other_index][best_index] = val_max
                provisions[other_index] -= val_max
                cmd[best_index] -= val_max
                if self.verbose:
                    print(f"Colonne C{best_index + 1} sélectionnée -> F{other_index + 1}C{best_index + 1} = {val_max}")
                if provisions[other_index] == 0:
                    active_rows.discard(other_index)
                if cmd[best_index] == 0:
                    active_cols.discard(best_index)
            else:
                self.proposition[best_index][other_index] = val_max
                provisions[best_index] -= val_max
                cmd[other_index] -= val_max
                if self.verbose:
                    print(f"Ligne P{best_index + 1} sélectionnée -> P{best_index + 1}C{other_index + 1} = {val_max}")
                if provisions[best_index] == 0:
                    active_rows.discard(best_index)
                if cmd[other_index] == 0:
                    active_cols.discard(other_index)

    def totalcost(self):
        if self.base:
            return sum(self.proposition[i][j] * self.couts[i][j] for i, j in self.base)
        return sum(
            self.proposition[i][j] * self.couts[i][j]
            for i in range(self.n) for j in range(self.m)
            if self.proposition[i][j] > 0
        )

    def fix_degeneracy(self):
        g = self.graph
        self.last_degenerate_edges = []
        while not g.is_connected():
            components = g.get_connected_components()
            comp1, comp2 = components[0], components[1]
            for node in comp1:
                if node[0] == "P":
                    i = node[1]
                    for node2 in comp2:
                        if node2[0] == "C":
                            j = node2[1]
                            self.proposition[i][j] = 0
                            g.add_edge(('P', i), ('C', j), 0)
                            self.base.add((i, j))
                            self.last_degenerate_edges.append((i, j))
                            if self.verbose:
                                print(f"Ajout case dégénérée : P{i + 1}C{j + 1} = 0")
                            break
                    break

    def compute_potentials(self):
        # Build adjacency lists restricted to basis cells
        row_adj = {i: [] for i in range(self.n)}
        col_adj = {j: [] for j in range(self.m)}
        for i, j in self.base:
            row_adj[i].append(j)
            col_adj[j].append(i)

        u = [None] * self.n
        v = [None] * self.m
        u[0] = 0

        queue = deque([('row', 0)])
        while queue:
            type, idx = queue.popleft()
            if type == 'row':
                i = idx
                for j in row_adj[i]:
                    if v[j] is None:
                        v[j] = self.couts[i][j] - u[i]
                        queue.append(('col', j))
            else:
                j = idx
                for i in col_adj[j]:
                    if u[i] is None:
                        u[i] = self.couts[i][j] - v[j]
                        queue.append(('row', i))

        if None in u or None in v:
            if self.verbose:
                print(f"AVERTISSEMENT : potentiels incomplets u={u} v={v}")
                print("La base n'est pas connexe, fix_degeneracy insuffisant.")
            return u, v

        if self.verbose:
            print(f"Potentiels u : {u}")
            print(f"Potentiels v : {v}")
        return u, v

    def compute_marginal_costs(self, u, v):
        best, best_val = None, 0

        if self.verbose:
            print("\nTable des coûts potentiels (u[i] + v[j]) :")
            for i in range(self.n):
                if u[i] is None:
                    print(f"P{i + 1} : [None] * {self.m}")
                    continue
                row = [u[i] + v[j] if v[j] is not None else None for j in range(self.m)]
                print(f"P{i + 1} : {row}")
            print("\nTable des coûts marginaux (c[i][j] - u[i] - v[j]) :")

        for i in range(self.n):
            if u[i] is None:
                continue
            row = []
            for j in range(self.m):
                if v[j] is None:
                    row.append(None)
                    continue
                marginal = self.couts[i][j] - u[i] - v[j]
                row.append(marginal)
                if marginal < best_val:
                    best_val, best = marginal, (i, j)
            if self.verbose:
                print(f"P{i + 1} : {row}")

        if self.verbose:
            if best:
                print(f"\nMeilleure arête améliorante : P{best[0] + 1}C{best[1] + 1} (coût marginal = {best_val})")
            else:
                print("\nAucune arête améliorante, solution optimale.")
        return best

    def _maximize_cycle(self, graph, new_edge=None):
        cycle = graph.find_cycle()
        cycle_str = [f"{n[0]}{n[1]}" for n in cycle]
        if self.verbose:
            print(f"Cycle : {' -> '.join(cycle_str)} -> {cycle_str[0]}")

        raw = []
        for k in range(len(cycle)):
            node_a = cycle[k]
            node_b = cycle[(k + 1) % len(cycle)]
            if node_a[0] == "P":
                i, j = node_a[1], node_b[1]
            else:
                i, j = node_b[1], node_a[1]
            raw.append((i, j, k))

        flip = False
        if new_edge:
            for i, j, k in raw:
                if (i, j) == new_edge and k % 2 == 1:
                    flip = True
                    break

        values = []
        for i, j, k in raw:
            signe = "+" if (k % 2 == 0) != flip else "-"
            values.append((i, j, signe))
            if self.verbose:
                print(f"  P{i + 1}C{j + 1} = {self.proposition[i][j]} ({signe})")

        delta = min(self.proposition[i][j] for i, j, s in values if s == "-")
        if self.verbose:
            print(f"Delta = {delta}")

        for i, j, signe in values:
            if signe == "+":
                self.proposition[i][j] += delta
            else:
                self.proposition[i][j] -= delta

        cases_a_supprimer = [(i, j) for i, j, s in values if s == "-" and self.proposition[i][j] == 0]
        case_supprimee = None
        for i, j in cases_a_supprimer:
            if (i, j) != new_edge:
                case_supprimee = (i, j)
                break
        if case_supprimee is None and cases_a_supprimer:
            case_supprimee = cases_a_supprimer[0]

        if case_supprimee:
            i, j = case_supprimee
            self.base.discard((i, j))
            graph.remove_edge(('P', i), ('C', j))  # incremental removal
            if self.verbose:
                print(f"Arête supprimée : P{i + 1}C{j + 1}")
        return delta

    # ------------------------------------------------------------------
    # Stepping-stone (main optimisation loop)
    # ------------------------------------------------------------------

    def stepping_stone(self):
        self.base = {
            (i, j) for i in range(self.n) for j in range(self.m)
            if self.proposition[i][j] > 0
        }
        self.graph = self._build_graph()  # single initial build

        while True:
            if self.verbose:
                print(f"\n--- Itération | base={self.base} | proposition={self.proposition} ---")

            # Remove any cycles in the current basis (initial step only in practice)
            while not self.graph.is_acyclic():
                self._maximize_cycle(self.graph)
                # graph is updated in place; no rebuild needed

            self.last_degenerate_edges = []
            if not self.graph.is_connected():
                self.fix_degeneracy()  # already updates self.graph in place

            u, v = self.compute_potentials()
            best = self.compute_marginal_costs(u, v)

            if best:
                i, j = best
                self.proposition[i][j] = 0
                self.base.add((i, j))
                self.graph.add_edge(('P', i), ('C', j), 0)  # incremental add
                if self.verbose:
                    print(f"Arête P{i+1}C{j+1} ajoutée à la proposition")

                delta = self._maximize_cycle(self.graph, new_edge=(i, j))
                # _maximize_cycle removes the leaving edge from self.graph

                if delta == 0:
                    if self.verbose:
                        print("Delta=0 : suppression des arêtes dégénérées et nouvelle tentative de connexité")
                    for di, dj in self.last_degenerate_edges:
                        self.proposition[di][dj] = 0
                        self.base.discard((di, dj))
                        self.graph.remove_edge(('P', di), ('C', dj))  # incremental removal
                        if self.verbose:
                            print(f"Arête dégénérée retirée : P{di+1}C{dj+1}")
            else:
                break
