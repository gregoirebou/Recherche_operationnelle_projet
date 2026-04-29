# Projet Recherche Opérationnelle — SM602

Groupe 6 — Équipe 1

Résolution du problème de transport par les méthodes Nord-Ouest, Balas-Hammer et marche-pied avec potentiel.

## Structure du projet

```
.
├── main.py               # Point d'entrée (mode interactif, traces, étude de complexité)
├── TransportProblem.py   # Classe principale : algorithmes NO, BH, marche-pied
├── Graph.py              # Graphe biparti (BFS, détection de cycle/connexité)
├── Complexite.py         # Étude empirique de la complexité + graphiques
├── TransportFiles/       # Fichiers de problèmes (.txt)
├── Traces/               # Traces d'exécution générées (6-1-traceN-{no,bh}.txt)
└── Old_pkl/              # Sauvegardes de runs de complexité précédents
```
## Utilisation

### Mode interactif

Résout un problème de transport en choisissant l'algorithme et affiche chaque étape :

```bash
python main.py
```

Le programme demande le numéro du problème (1–12) et l'algorithme de proposition initiale (Nord-Ouest ou Balas-Hammer), puis déroule la méthode du marche-pied avec potentiel.

### Génération des traces d'exécution

Génère les 24 fichiers de traces (12 problèmes × 2 algorithmes) dans le dossier `Traces/` :

```python
# Dans main.py, décommenter :
run_all_problems(6, 1)
```

Les fichiers suivent la convention `{groupe}-{equipe}-trace{N}-{no|bh}.txt`.

### Étude de complexité

Lance l'étude empirique sur les tailles n ∈ {10, 40, 100, 400, 1000} avec 100 instances aléatoires par taille :

```python
# Dans main.py, décommenter :
run_complexity_study()
```

Les résultats sont sauvegardés dans `sauvegarde_complexite.pkl` — si ce fichier est déjà présent et complet, le programme passe directement aux graphiques sans relancer les calculs. Deux graphiques sont générés :
- Nuages de points + pire cas pour θ_NO, θ_BH, t_NO, t_BH, (θ_NO+t_NO), (θ_BH+t_BH)
- Comparaison du ratio (θ_NO+t_NO)/(θ_BH+t_BH) avec pire cas


## Algorithmes implémentés

| Méthode | Classe | Complexité théorique |
|---|---|---|
| Nord-Ouest | `TransportProblem.NorthWest` | O(n+m) |
| Balas-Hammer | `TransportProblem.BalasHammer` | O(n²·m + n·m²) |
| Marche-pied avec potentiel | `TransportProblem.stepping_stone` | O(n²·m²) par itération |
| Détection de cycle / connexité | `Graph._bfs` | O(n+m) |
