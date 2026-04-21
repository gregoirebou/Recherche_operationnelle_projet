from Graph import Graph

class TransportProblem:
    def __init__(self, file):
        self.n = 0  # nombre de fournisseurs
        self.m = 0  # nombre de clients
        self.couts = []       # matrice n x m des coûts unitaires
        self.provisions = []  # liste de taille n
        self.commandes = []   # liste de taille m
        self.proposition = [] # matrice n x m de la proposition de transport
        self.graph = None
        self.base = None
        self.load_from_file(file)
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
        self.graph = self.to_graph()

    def __str__(self):
        lignes = []

        # En-tête des colonnes
        header = "       " + "  ".join(f"{'C'+str(j+1):>5}" for j in range(self.m)) + "  | Provisions"
        lignes.append(header)
        lignes.append("-" * len(header))

        # Lignes fournisseurs : coûts + provision
        for i in range(self.n):
            row = f"P{i + 1:<4}  " + "  ".join(f"{self.couts[i][j]:>5}" for j in range(self.m))
            row += f"  | {self.provisions[i]}"
            lignes.append(row)

        lignes.append("-" * len(header))

        # Ligne des commandes
        lignes.append("Cmd    " + "  ".join(f"{self.commandes[j]:>5}" for j in range(self.m)))

        # Proposition si non vide
        if any(self.proposition[i][j] != 0 for i in range(self.n) for j in range(self.m)):
            lignes.append("\nProposition :")
            lignes.append("       " + "  ".join(f"{'C'+str(j+1):>5}" for j in range(self.m)))
            for i in range(self.n):
                row = f"P{i + 1:<4}  " + "  ".join(f"{self.proposition[i][j]:>5}" for j in range(self.m))
                lignes.append(row)

        return "\n".join(lignes)

    def NorthWest(self):
        cmd = self.commandes.copy()
        provisions = self.provisions.copy()
        for i in range(self.n):
            for j in range(self.m):
                if cmd[j] == 0:
                    continue

                val_max = min(cmd[j], provisions[i])
                self.proposition[i][j] = val_max
                cmd[j] -= val_max
                provisions[i] -= val_max

                if provisions[i] == 0:
                    break

    def get_capacity(self, is_row, index, cmd, provisions):
        if is_row:
            couts_dispo = [(self.couts[index][j], j) for j in range(self.m) if cmd[j] > 0]
            _, j_min = min(couts_dispo)
            return min(provisions[index], cmd[j_min]), j_min
        else:
            couts_dispo = [(self.t_couts[index][i], i) for i in range(self.n) if provisions[i] > 0]
            _, i_min = min(couts_dispo)
            return min(provisions[i_min], cmd[index]), i_min

    def BalasHammer(self):
        cmd = self.commandes.copy()
        provisions = self.provisions.copy()
        penalty_col = [0 for _ in range(self.m)]
        penalty_row = [0 for _ in range(self.n)]
        while any(val != 0 for val in cmd) or any(val2 != 0 for val2 in provisions):
            for i in range(self.n):
                if provisions[i] == 0:
                    penalty_row[i] = -1
                    continue
                couts_dispo = [self.couts[i][j] for j in range(self.m) if cmd[j] > 0]
                if len(couts_dispo) < 2:
                    penalty_row[i] = 0
                else:
                    s = sorted(couts_dispo)
                    penalty_row[i] = s[1] - s[0]

            for j in range(self.m):
                if cmd[j] == 0:
                    penalty_col[j] = -1
                    continue
                couts_dispo = [self.t_couts[j][i] for i in range(self.n) if provisions[i] > 0]
                if len(couts_dispo) < 2:
                    penalty_col[j] = 0
                else:
                    s = sorted(couts_dispo)
                    penalty_col[j] = s[1] - s[0]
            print(f"Pénalités lignes : {penalty_row}")
            print(f"Pénalités colonnes : {penalty_col}")

            max_penalty = max(max(penalty_col), max(penalty_row))
            candidates = [[],[]]
            if max_penalty in penalty_row:
                candidates[0].append(penalty_row.index(max_penalty))
            if max_penalty in penalty_col:
                candidates[1].append(penalty_col.index(max_penalty))
            print(f"Pénalité maximale : {max_penalty}")
            print(f"Candidats lignes : {candidates[0]}, Candidats colonnes : {candidates[1]}")

            all_candidates = []
            for i in candidates[0]:
                all_candidates.append((0, i, *self.get_capacity(True, i, cmd, provisions)))
            for j in candidates[1]:
                all_candidates.append((1, j, *self.get_capacity( False, j, cmd, provisions)))

            best_type, best_index, val_max_to_insert, other_index = max(all_candidates, key=lambda x: x[2])

            if best_type:
                self.proposition[other_index][best_index] = val_max_to_insert
                provisions[other_index] -= val_max_to_insert
                cmd[best_index] -= val_max_to_insert
                print(f"Colonne C{best_index + 1} sélectionnée → F{other_index + 1}C{best_index + 1} = {val_max_to_insert}")

            else:
                self.proposition[best_index][other_index] = val_max_to_insert
                provisions[best_index] -= val_max_to_insert
                cmd[other_index] -= val_max_to_insert
                print(f"Ligne P{best_index + 1} sélectionnée → P{best_index + 1}C{other_index + 1} = {val_max_to_insert}")

    def totalcost(self):
        total_cost = 0
        for i in range(self.n):
            for j in range(self.m):
                total_cost += self.proposition[i][j] * self.couts[i][j]
        return total_cost

    def to_graph(self):
        g = Graph()
        source = self.base if self.base else {(i, j) for i in range(self.n) for j in range(self.m) if self.proposition[i][j] > 0}
        for i, j in source:
            g.add_edge(f"P{i}", f"C{j}", self.proposition[i][j])
        return g

    def is_acyclic(self):
        return self.to_graph().is_acyclic()

    def fix_degeneracy(self):
        g = self.graph
        self.last_degenerate_edges = []
        while not g.is_connected():
            components = g.get_connected_components()
            comp1, comp2 = components[0], components[1]
            for node in comp1:
                if node.startswith("P"):
                    i = int(node[1:])
                    for node2 in comp2:
                        if node2.startswith("C"):
                            j = int(node2[1:])
                            self.proposition[i][j] = 0
                            g.add_edge(f"P{i}", f"C{j}", 0)
                            self.base.add((i, j))
                            self.last_degenerate_edges.append((i, j))
                            print(f"Ajout case dégénérée : P{i + 1}C{j + 1} = 0")
                            break
                    break

    def compute_potentials(self):
        u = [None] * self.n
        v = [None] * self.m
        u[0] = 0

        changed = True
        while changed:
            changed = False
            for i in range(self.n):
                for j in range(self.m):
                    if (i, j) in self.base:
                        if u[i] is not None and v[j] is None:
                            v[j] = self.couts[i][j] - u[i]
                            changed = True
                        elif v[j] is not None and u[i] is None:
                            u[i] = self.couts[i][j] - v[j]
                            changed = True

        # Vérification
        if None in u or None in v:
            print(f"AVERTISSEMENT : potentiels incomplets u={u} v={v}")
            print("La base n'est pas connexe, fix_degeneracy insuffisant.")
            return u, v

        print(f"Potentiels u : {u}")
        print(f"Potentiels v : {v}")
        return u, v

    def compute_marginal_costs(self, u, v):
        """Calcule les coûts marginaux et détecte la meilleure arête améliorante."""
        best, best_val = None, 0

        print("\nTable des coûts potentiels (u[i] + v[j]) :")
        for i in range(self.n):
            if u[i] is None:
                print(f"P{i + 1} : [None] * {self.m}")
                continue
            row = [u[i] + v[j] if v[j] is not None else None for j in range(self.m)]
            print(f"P{i + 1} : {row}")

        print("\nTable des coûts marginaux (c[i][j] - u[i] - v[j]) :")
        for i in range(self.n):
            row = []
            for j in range(self.m):
                if u[i] is None or v[j] is None:
                    row.append(None)
                    continue  # ← manquait le continue
                marginal = self.couts[i][j] - u[i] - v[j]
                row.append(marginal)
                if marginal < best_val:
                    best_val, best = marginal, (i, j)
            print(f"P{i + 1} : {row}")

        if best:
            print(f"\nMeilleure arête améliorante : P{best[0] + 1}C{best[1] + 1} (coût marginal = {best_val})")
        else:
            print("\nAucune arête améliorante, solution optimale.")
        return best

    def maximize_cycle(self, new_edge=None):
        g = self.to_graph()
        cycle = g.find_cycle()
        print(f"Cycle : {' -> '.join(cycle)} -> {cycle[0]}")

        raw = []
        for k in range(len(cycle)):
            node_a = cycle[k]
            node_b = cycle[(k + 1) % len(cycle)]
            if node_a.startswith("P"):
                i, j = int(node_a[1:]), int(node_b[1:])
            else:
                i, j = int(node_b[1:]), int(node_a[1:])
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
            print(f"  P{i + 1}C{j + 1} = {self.proposition[i][j]} ({signe})")

        delta = min(self.proposition[i][j] for i, j, s in values if s == "-")
        print(f"Delta = {delta}")

        # Mise à jour
        for i, j, signe in values:
            if signe == "+":
                self.proposition[i][j] += delta
            else:
                self.proposition[i][j] -= delta

        # Supprimer UNE case "-" à 0, en évitant new_edge si possible
        cases_a_supprimer = [(i, j) for i, j, s in values if s == "-" and self.proposition[i][j] == 0]

        # Préférer supprimer une case qui n'est pas new_edge
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
            print(f"Arête supprimée : P{i + 1}C{j + 1}")
        return delta

    def stepping_stone(self):
        self.graph = self.to_graph()
        self.base = {(i, j) for i in range(self.n) for j in range(self.m) if self.proposition[i][j] > 0}

        while True:
            print(f"\n--- Itération | base={self.base} | proposition={self.proposition} ---")
            self.graph = self.to_graph()

            while not self.graph.is_acyclic():
                self.maximize_cycle()
                self.graph = self.to_graph()

            self.last_degenerate_edges = []
            if not self.graph.is_connected():
                self.fix_degeneracy()

            u, v = self.compute_potentials()
            best = self.compute_marginal_costs(u, v)

            if best:
                i, j = best
                self.proposition[i][j] = 0
                self.base.add((i, j))
                print(f"Arête P{i+1}C{j+1} ajoutée à la proposition")
                delta = self.maximize_cycle(new_edge=(i, j))

                if delta == 0:
                    print("Delta=0 : suppression des arêtes dégénérées et nouvelle tentative de connexité")
                    for di, dj in self.last_degenerate_edges:
                        self.proposition[di][dj] = 0
                        self.base.discard((di, dj))
                        print(f"Arête dégénérée retirée : P{di+1}C{dj+1}")
            else:
                break
#
# Transport1 = TransportProblem("Probleme11.txt")
# Transport1.BalasHammer()
# print(Transport1)
# print(Transport1.totalcost())
#
# Transport1.stepping_stone()
# print(Transport1)
# print(Transport1.totalcost())


    