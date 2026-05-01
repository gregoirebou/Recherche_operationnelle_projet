# Rapport d'étude de la complexité

---

## 4. Analyse de la complexité par fonction

Cette section détaille la complexité de chaque fonction importante du programme.
On travaille avec des problèmes de transport carrés (n fournisseurs, n clients).
Le graphe de transport associé possède donc **2n sommets** (n nœuds P et n nœuds C)
et sa base contient au plus **2n − 1 arêtes** (proposition non dégénérée).
On note |B| = |base| ≤ 2n − 1 = O(n) la taille courante de la base.

---

### 4.1 Classe `Graph` — structure de données du graphe biparti

#### `add_edge(start, end, weight)` — **O(1)**

```
add_vertex(start)          → O(1) amortisé (hash-map)
add_vertex(end)            → O(1) amortisé
graph[start].append(...)   → O(1) amortisé
graph[end].append(...)     → O(1) amortisé
```

Chaque sommet est représenté par une clé de dictionnaire et une liste d'adjacence.
L'ajout d'une arête effectue deux insertions de liste : coût constant.

---

#### `remove_edge(start, end)` — **O(deg)**

```
graph[start] = [x for x in graph[start] if x != end]   → O(deg(start))
graph[end]   = [x for x in graph[end]   if x != start] → O(deg(end))
```

Le parcours linéaire de la liste d'adjacence est nécessaire pour retirer l'arête.
Dans le graphe de transport, le degré maximal d'un sommet est borné par n
(un fournisseur peut être connecté à au plus n clients). Donc **O(n)** en pratique.

---

#### `_bfs(start)` — **O(V + E) = O(n)**

```
visited = {start: None}        → O(1)
queue = deque([start])         → O(1)
while queue:                   → au plus V itérations
    node = queue.popleft()     → O(1)
    for neighbor in graph[node]: → O(deg(node))
        ...                    → O(1) par voisin
```

BFS standard sur le graphe de transport : V = 2n sommets, E = O(n) arêtes dans la base.
Chaque sommet et chaque arête est traité au plus une fois : **O(V + E) = O(n)**.

---

#### `is_acyclic()` — **O(n)**

Appelle `_bfs` une seule fois depuis un sommet source.
Retourne `True` si aucun arc de retour n'est détecté pendant le parcours.
Complexité identique à `_bfs` : **O(n)**.

---

#### `is_connected()` — **O(n)**

Appelle `_bfs` une seule fois. Si tous les sommets sont atteints, le graphe est connexe.
Sinon appelle `get_connected_components()` (O(n)) pour l'affichage.
Complexité totale : **O(n)**.

---

#### `get_connected_components()` — **O(n)**

```
unvisited = set(graph.keys())          → O(n)
while unvisited:                       → au plus n itérations au total
    visited, _ = _bfs(start)          → O(n) cumulé sur toutes les composantes
    unvisited -= comp                  → O(|comp|)
```

Chaque nœud est visité exactement une fois au total sur l'ensemble des BFS.
Le coût total est **O(V + E) = O(n)**, quelle que soit la structure en composantes.

---

#### `find_cycle()` — **O(n)**

```
BFS depuis un sommet source         → O(n)
path_to_root(node_a)               → O(longueur chemin) ≤ O(2n) = O(n)
path_to_root(node_b)               → O(n)
Construction du cycle               → O(n)
```

La phase de BFS coûte O(n). La reconstruction du cycle depuis les deux extrémités
vers la racine BFS parcourt des chemins de longueur au plus 2n.
Complexité totale : **O(n)**.

---

### 4.2 Classe `TransportProblem` — algorithmes de résolution

#### `load_from_file()` — **O(n²)**

```
Lecture des n lignes de coûts       → O(n lignes × n valeurs) = O(n²)
Lecture des provisions et commandes → O(n)
Initialisation proposition          → O(n²)  (matrice n×n à zéro)
```

Le stockage de la matrice des coûts domine : **O(n²)**.

---

#### `NorthWest()` — **O(n)**

```
i = 0, j = 0
while i < n and j < m:           → au plus n + m − 1 = 2n − 1 itérations
    val = min(cmd[j], provisions[i])  → O(1)
    proposition[i][j] = val           → O(1)
    i++ ou j++                        → O(1)
```

À chaque itération, soit i soit j est incrémenté. Comme i ≤ n et j ≤ n,
la boucle effectue au plus 2n − 1 tours. Toutes les opérations internes sont O(1).
Complexité : **O(n)**.

---

#### `BalasHammer()` — **O(n³)**

La boucle principale s'exécute au plus 2n − 1 fois (une ligne ou colonne est éliminée
à chaque itération). Soit r et c le nombre de lignes et colonnes actives à l'itération k.

**Par itération :**

```
for i in active_rows:                          → r itérations
    heapq.nsmallest(2, couts[i][j] for j in active_cols)  → O(c)
    → coût total pénalités lignes : O(r × c)

for j in active_cols:                          → c itérations
    heapq.nsmallest(2, couts[i][j] for i in active_rows)  → O(r)
    → coût total pénalités colonnes : O(r × c)

Recherche du max + sélection de la case       → O(r + c) = O(n)
```

Coût par itération : **O(r × c)**.

**Coût total :**

Dans le pire des cas (une seule dimension décroît), la somme est :
```
Σ_{k=0}^{2n-2} (n − k/2)² ≈ O(n³)
```

En pratique, lignes et colonnes s'éliminent de façon alternée, ramenant le comportement
effectif vers **O(n²)** en moyenne — ce qui explique les exposants mesurés
entre 2,04 et 3,20. La **complexité dans le pire des cas est O(n³)**.

---

#### `totalcost()` — **O(n)**

```
sum(proposition[i][j] * couts[i][j] for i, j in base)  → O(|B|) = O(n)
```

Itération sur la base uniquement (au plus 2n − 1 termes) : **O(n)**.

---

#### `_build_graph()` — **O(n)**

```
Création du graphe vide             → O(1)
for i, j in source (≤ |B|):        → O(|B|) = O(n)
    g.add_edge(...)                 → O(1)
```

Complexité : **O(n)**.

---

#### `compute_potentials()` — **O(n)**

```
Construction row_adj, col_adj       → O(|B|) = O(n)
BFS sur le graphe de base :
    V = 2n sommets, E = |B| = O(n) arêtes
    → O(V + E) = O(n)
```

La propagation des potentiels u[i] et v[j] suit un parcours BFS sur l'arbre de base.
Chaque nœud est traité une fois. Complexité : **O(n)**.

---

#### `compute_marginal_costs(u, v)` — **O(n²)**

```
for i in range(n):         → n itérations
    for j in range(m):     → n itérations
        marginal = couts[i][j] - u[i] - v[j]   → O(1)
        if marginal < best_val: ...             → O(1)
```

La double boucle parcourt la totalité de la matrice n × n pour identifier la meilleure
arête améliorante. C'est la **fonction dominante par itération du marche-pied** : **O(n²)**.

---

#### `fix_degeneracy()` — **O(n²) dans le pire des cas**

```
while not g.is_connected():        → au plus n − 1 appels (max n − 1 arêtes à ajouter)
    components = get_connected_components()  → O(n)
    trouver (i, j) connectant deux composantes → O(n)
    g.add_edge(...)                → O(1)
```

À chaque appel, une arête est ajoutée. Il faut au plus n − 1 arêtes pour rendre le graphe
connexe (arbre couvrant). Chaque itération coûte O(n). Total : **O(n²)**.
En pratique ce cas est rare et l'appel unique domine.

---

#### `_maximize_cycle(graph, new_edge)` — **O(n)**

```
graph.find_cycle()                 → O(n)
Parcours du cycle (longueur ≤ 2n):
    calcul du delta                → O(n)
    mise à jour des flux           → O(n)
    suppression de l'arête sortante → O(1) (base.discard + remove_edge O(deg) = O(n))
```

La longueur maximale d'un cycle dans un arbre de base de taille 2n est 2n.
Complexité : **O(n)**.

---

#### `stepping_stone()` — **O(n³)**

C'est la **boucle principale** du marche-pied avec potentiel.

**Par itération de la boucle externe :**

| Étape                         | Complexité       |
|-------------------------------|------------------|
| `is_acyclic()` (boucle interne) | O(n) × O(1) fois en moyenne |
| `_maximize_cycle()` (si cycle)  | O(n)             |
| `is_connected()`                | O(n)             |
| `fix_degeneracy()`              | O(n²) au pire    |
| `compute_potentials()`          | O(n)             |
| `compute_marginal_costs()`      | **O(n²)**        |
| `_maximize_cycle()` (si améliorante) | O(n)        |

Coût dominant par itération : **O(n²)** (calcul des coûts marginaux).

**Nombre d'itérations :**

Le marche-pied est un algorithme de type simplexe sur le polytope de transport.
Le nombre de pivots est borné théoriquement par le nombre de solutions de base réalisables,
mais en pratique il est de l'ordre de **O(n)** pour des instances aléatoires.

**Complexité totale du marche-pied :**

```
O(n) itérations × O(n²) par itération = O(n³)
```

Ce résultat est cohérent avec les mesures expérimentales (k ≈ 3,0 sur la moyenne).

---

### 4.3 Récapitulatif des complexités

| Fonction                  | Fichier              | Complexité       | Rôle                                        |
|---------------------------|----------------------|------------------|---------------------------------------------|
| `add_edge`                | Graph.py             | O(1)             | Ajout d'arête dans la liste d'adjacence     |
| `remove_edge`             | Graph.py             | O(n)             | Retrait d'arête (parcours liste adj.)       |
| `_bfs`                    | Graph.py             | O(n)             | Parcours en largeur                         |
| `is_acyclic`              | Graph.py             | O(n)             | Détection de cycle par BFS                  |
| `is_connected`            | Graph.py             | O(n)             | Test de connexité par BFS                   |
| `get_connected_components`| Graph.py             | O(n)             | Décomposition en composantes connexes       |
| `find_cycle`              | Graph.py             | O(n)             | Extraction du cycle + reconstruction        |
| `load_from_file`          | TransportProblem.py  | O(n²)            | Lecture et stockage de la matrice           |
| `NorthWest`               | TransportProblem.py  | **O(n)**         | Proposition initiale coin Nord-Ouest        |
| `BalasHammer`             | TransportProblem.py  | **O(n³)**        | Proposition initiale par pénalités          |
| `totalcost`               | TransportProblem.py  | O(n)             | Calcul du coût total de la proposition      |
| `_build_graph`            | TransportProblem.py  | O(n)             | Construction du graphe depuis la base       |
| `compute_potentials`      | TransportProblem.py  | O(n)             | Calcul des potentiels u[i] et v[j] (BFS)    |
| `compute_marginal_costs`  | TransportProblem.py  | **O(n²)**        | Calcul de tous les coûts marginaux          |
| `fix_degeneracy`          | TransportProblem.py  | O(n²)            | Ajout d'arêtes dégénérées pour la connexité |
| `_maximize_cycle`         | TransportProblem.py  | O(n)             | Maximisation du flux sur un cycle           |
| `stepping_stone`          | TransportProblem.py  | **O(n³)**        | Boucle principale du marche-pied            |

---

### 4.4 Synthèse — comment O(n³) émerge

La complexité globale O(n³) de la chaîne de résolution s'explique par la **cascade** suivante :

```
stepping_stone()          → O(n)   itérations
  └─ compute_marginal_costs()  → O(n²)  par itération
       └─ double boucle sur toute la matrice n × n
```

La fonction `compute_marginal_costs` est le **goulot d'étranglement** : elle doit inspecter
les n² cellules hors-base à chaque pivot pour garantir le choix de l'arête améliorante
de coût marginal le plus négatif. Toutes les autres fonctions (BFS, potentiels, cycle)
restent en O(n) et n'affectent pas l'ordre de grandeur global.

L'avantage de Balas-Hammer sur Nord-Ouest ne modifie pas cette complexité asymptotique,
mais **réduit la constante multiplicative** en produisant une proposition initiale plus
proche de l'optimum, ce qui diminue le nombre d'itérations du marche-pied en pratique.

---

## 3. L'étude de la complexité

---

### 3.1 Introduction

La complexité d'un algorithme désigne l'évaluation des ressources nécessaires à son exécution :
principalement la mémoire utilisée et le temps de calcul. Ces grandeurs dépendent de nombreux
paramètres matériels ; on cherche donc non pas une valeur absolue, mais un **ordre de grandeur**
permettant de comparer des algorithmes résolvant un même problème.

Dans ce projet, nous comparons les deux chaînes de résolution suivantes pour le problème
du transport :

- **Nord-Ouest + Marche-pied** : proposition initiale par l'algorithme du coin Nord-Ouest,
  puis optimisation par la méthode du marche-pied avec potentiel.
- **Balas-Hammer + Marche-pied** : proposition initiale par l'algorithme de Balas-Hammer,
  puis même optimisation par le marche-pied.

---

### 3.2 Rappels théoriques

| Notation   | Complexité       |
|------------|------------------|
| O(log n)   | logarithmique    |
| O(n)       | linéaire         |
| O(n log n) | quasi-linéaire   |
| O(n²)      | quadratique      |
| O(nᵏ), k>2 | polynomiale      |
| O(kⁿ), k>1 | exponentielle    |

Nous distinguons trois types de complexité temporelle :

- **Complexité dans le pire des cas** : majorant du temps d'exécution sur toutes les entrées
  de taille n. Notée O(·).
- **Complexité en moyenne** : évaluation du temps moyen sur l'ensemble des entrées de taille n
  supposées équiprobables.
- **Complexité spatiale** : ordre de grandeur de la mémoire consommée en fonction de n.

---

### 3.3 Protocole expérimental

Les problèmes de transport sont carrés (n fournisseurs = n clients). Pour chaque taille n,
100 instances aléatoires sont générées :

- Les coûts aᵢ,ⱼ sont tirés uniformément dans [[1, 100]].
- Une matrice temporaire tempᵢ,ⱼ est tirée dans [[1, 100]] ; les provisions Pᵢ et les commandes
  Cⱼ en sont déduites par sommation en ligne et en colonne respectivement, garantissant
  l'équilibre du problème.

Pour chaque instance, on mesure séparément :
- θ_NO(n) : temps de l'algorithme Nord-Ouest seul.
- θ_BH(n) : temps de l'algorithme Balas-Hammer seul.
- t_NO(n) : temps du marche-pied depuis la proposition Nord-Ouest.
- t_BH(n) : temps du marche-pied depuis la proposition Balas-Hammer.

Les valeurs de n testées sont : **10, 40, 100, 400, 1000**.

La complexité dans le pire des cas est approchée par le **maximum** des 100 mesures pour
chaque n. La complexité en moyenne est approchée par la **moyenne** des 100 mesures.

---

### 3.4 Résultats – Nord-Ouest + Marche-pied (θ_NO + t_NO)

#### 3.4.1 Tableau des temps et ratios

| n    | Max (s)    | Moyen (s)  | T/n        | T/n²       | T/n³        |
|------|------------|------------|------------|------------|-------------|
| 10   | 0.00174    | 0.00100    | 0.000174   | 0.0000174  | 0.00000174  |
| 40   | 0.05560    | 0.04435    | 0.001390   | 0.0000347  | 0.000000869 |
| 100  | 1.01299    | 0.76333    | 0.010130   | 0.0001013  | 0.00000101  |
| 400  | 70.94146   | 64.70263   | 0.177354   | 0.0004434  | 0.00000111  |
| 1000 | 1090.84935 | 1037.40148 | 1.090849   | 0.0010908  | 0.00000109  |

**Lecture des ratios :** La colonne T/n³ est la plus stable sur l'ensemble des valeurs de n
(oscillation entre 8,69×10⁻⁷ et 1,74×10⁻⁶), ce qui indique que le temps croît comme n³.

#### 3.4.2 Rapports de croissance (pire des cas)

| Passage        | Facteur n | Facteur temps | k déduit |
|----------------|-----------|---------------|----------|
| n=10 → n=40    | ×4,0      | ×31,89        | ≈ 2,50   |
| n=40 → n=100   | ×2,5      | ×18,22        | ≈ 3,17   |
| n=100 → n=400  | ×4,0      | ×70,03        | ≈ 3,06   |
| n=400 → n=1000 | ×2,5      | ×15,38        | ≈ 2,98   |
| n=10 → n=1000  | ×100      | ×625 738      | ≈ **2,90** |

#### 3.4.3 Rapports de croissance (temps moyen)

| Passage        | Facteur n | Facteur temps   | k déduit |
|----------------|-----------|-----------------|----------|
| n=10 → n=40    | ×4,0      | ×44,47          | ≈ 2,74   |
| n=40 → n=100   | ×2,5      | ×17,21          | ≈ 3,11   |
| n=100 → n=400  | ×4,0      | ×84,76          | ≈ 3,20   |
| n=400 → n=1000 | ×2,5      | ×16,03          | ≈ 3,03   |
| n=10 → n=1000  | ×100      | ×1 040 194      | ≈ **3,01** |

#### 3.4.4 Conclusion pour Nord-Ouest + Marche-pied

La stabilité du ratio T/n³ et les exposants déduits des rapports de croissance convergent
vers k ≈ 3 (entre 2,90 sur le max et 3,01 sur la moyenne).

> **La complexité temporelle de Nord-Ouest + Marche-pied est O(n³)** (complexité polynomiale).

Ce résultat s'explique naturellement : l'algorithme du coin Nord-Ouest est O(n), mais
la méthode du marche-pied avec potentiel effectue, à chaque itération, un calcul des
potentiels et une recherche de cycle en O(n²), et peut nécessiter O(n) itérations,
conduisant à une complexité globale en O(n³).

---

### 3.5 Résultats – Balas-Hammer + Marche-pied (θ_BH + t_BH)

#### 3.5.1 Tableau des temps et ratios

| n    | Max (s)   | Moyen (s)  | T/n       | T/n²       | T/n³        |
|------|-----------|------------|-----------|------------|-------------|
| 10   | 0.00152   | 0.00081    | 0.000152  | 0.0000152  | 0.00000153  |
| 40   | 0.02589   | 0.02102    | 0.000647  | 0.0000162  | 0.000000405 |
| 100  | 0.48603   | 0.27980    | 0.004860  | 0.0000486  | 0.000000486 |
| 400  | 19.77638  | 17.60000   | 0.049441  | 0.0001236  | 0.000000309 |
| 1000 | 292.63739 | 264.87435  | 0.292637  | 0.0002926  | 0.000000293 |

**Lecture des ratios :** Le ratio T/n³ est le plus stable (décroissance légère de 1,53×10⁻⁶
à 2,93×10⁻⁷), suggérant une complexité voisine de O(n³) mais avec un exposant effectif
légèrement inférieur.

#### 3.5.2 Rapports de croissance (pire des cas)

| Passage        | Facteur n | Facteur temps | k déduit |
|----------------|-----------|---------------|----------|
| n=10 → n=40    | ×4,0      | ×16,98        | ≈ 2,04   |
| n=40 → n=100   | ×2,5      | ×18,77        | ≈ 3,20   |
| n=100 → n=400  | ×4,0      | ×40,69        | ≈ 2,67   |
| n=400 → n=1000 | ×2,5      | ×14,80        | ≈ 2,94   |
| n=10 → n=1000  | ×100      | ×191 944      | ≈ **2,64** |

#### 3.5.3 Rapports de croissance (temps moyen)

| Passage        | Facteur n | Facteur temps | k déduit |
|----------------|-----------|---------------|----------|
| n=10 → n=40    | ×4,0      | ×26,10        | ≈ 2,35   |
| n=40 → n=100   | ×2,5      | ×13,31        | ≈ 2,82   |
| n=100 → n=400  | ×4,0      | ×62,90        | ≈ 2,99   |
| n=400 → n=1000 | ×2,5      | ×15,05        | ≈ 2,96   |
| n=10 → n=1000  | ×100      | ×328 755      | ≈ **2,76** |

#### 3.5.4 Conclusion pour Balas-Hammer + Marche-pied

Les rapports de croissance donnent un exposant oscillant entre 2,04 et 3,20, avec une
valeur globale de k ≈ 2,64 (max) à 2,76 (moyenne). La variabilité est plus forte que pour
Nord-Ouest, ce qui s'explique par le comportement de Balas-Hammer : cet algorithme produit
des propositions initiales de meilleure qualité (plus proches de l'optimal), réduisant
ainsi le nombre d'itérations du marche-pied.

> **La complexité temporelle de Balas-Hammer + Marche-pied est O(n³)** dans le pire des cas,
> avec un comportement pratique proche de O(n^{2,7}) en raison de la meilleure initialisation.

---

### 3.6 Comparaison des deux chaînes de résolution

#### 3.6.1 Ratio des complexités dans le pire des cas

Le graphique de comparaison trace le ratio :

$$\frac{(θ_{NO} + t_{NO})(n)}{(θ_{BH} + t_{BH})(n)}$$

| n    | Ratio (pire des cas) |
|------|----------------------|
| 10   | ≈ 1,97               |
| 40   | ≈ 2,94               |
| 100  | ≈ 3,48               |
| 400  | ≈ 4,15               |
| 1000 | ≈ 4,28               |

**Observations :**

1. Le ratio est **toujours strictement supérieur à 1** : Balas-Hammer + Marche-pied est
   systématiquement plus rapide que Nord-Ouest + Marche-pied, pour toutes les tailles testées.

2. Le ratio **croît avec n** : l'avantage de Balas-Hammer s'amplifie à mesure que les instances
   grossissent. Pour n=1000, Nord-Ouest + Marche-pied est environ 4,3 fois plus lent.

3. La courbe du ratio est **croissante mais concave** (la croissance ralentit), ce qui laisse
   penser que le ratio tend vers une constante asymptotique, cohérent avec le fait que les
   deux algorithmes sont de même ordre O(n³) mais avec des constantes différentes.

#### 3.6.2 Interprétation

L'algorithme de Balas-Hammer calcule des pénalités pour choisir l'arête à allouer en priorité,
ce qui produit une proposition initiale structurellement plus proche de l'optimum. En conséquence,
le marche-pied nécessite **moins d'itérations** pour converger, réduisant significativement le
temps total. L'algorithme du coin Nord-Ouest, par sa nature aveugle (remplissage systématique
depuis le coin supérieur gauche), aboutit à des propositions initiales éloignées de l'optimum,
allongeant le travail du marche-pied.

---

### 3.7 Analyse des graphiques

#### Graphique 1 – Nuage de points et pire cas (6 sous-graphes)

Le graphique en log-log présente les 100 réalisations (points bleus) et l'enveloppe supérieure
(pire cas, en rouge) pour chacune des six métriques : θ_NO, θ_BH, t_NO, t_BH,
(θ_NO + t_NO) et (θ_BH + t_BH).

- Sur l'échelle log-log, les courbes du pire cas sont **quasi-linéaires**, confirmant une
  loi de puissance T(n) = C·nᵏ.
- La dispersion du nuage (écart entre le point minimum et le maximum) est visible mais
  modérée : les instances aléatoires produisent des comportements relativement homogènes,
  ce qui valide la robustesse de l'estimation par le maximum.
- Les courbes de t_NO et t_BH (marche-pied seul) montrent que c'est bien cette phase
  qui domine le temps total : θ_NO et θ_BH sont négligeables comparativement.

#### Graphique 2 – Comparaison de la complexité dans le pire des cas

Ce graphique trace en abscisse log la taille n et en ordonnée le ratio
(θ_NO + t_NO) / (θ_BH + t_BH) pour le pire cas (rouge) et les 100 réalisations
individuelles (bleu).

- Le ratio du pire cas passe de ~1,97 à n=10 à ~4,28 à n=1000.
- Le nuage de points montre que, **même pour les réalisations individuelles**, le ratio reste
  presque toujours au-dessus de 1 : Balas-Hammer est supérieur non seulement dans le pire
  des cas mais **en pratique**.
- Quelques points bleus inférieurs à 1 (visibles pour n=10) s'expliquent par la variabilité
  sur les petites instances où les deux algorithmes ont des temps très proches.
- La ligne verte pointillée (ratio = 1, égalité) n'est jamais touchée par la courbe du pire cas.

---

### 3.8 Conclusion générale

| Algorithme                 | Complexité pire des cas | Exposant mesuré (max) | Exposant mesuré (moy) |
|----------------------------|-------------------------|-----------------------|-----------------------|
| Nord-Ouest + Marche-pied   | **O(n³)**               | k ≈ 2,90              | k ≈ 3,01              |
| Balas-Hammer + Marche-pied | **O(n³)**               | k ≈ 2,64              | k ≈ 2,76              |

Les deux chaînes de résolution appartiennent à la même classe de complexité **polynomiale O(n³)**.
Cependant, la qualité supérieure de la proposition initiale fournie par Balas-Hammer conduit à
une **constante multiplicative nettement plus faible** : pour n=1000, le temps total est réduit
d'un facteur ~4,3 par rapport à Nord-Ouest. Cet écart, croissant avec n, confirme l'intérêt
pratique de l'algorithme de Balas-Hammer comme initialisation pour le marche-pied avec potentiel.

> **Recommandation :** Utiliser systématiquement Balas-Hammer comme proposition initiale
> lorsque les temps de calcul sont critiques, l'amélioration étant significative et constante.
