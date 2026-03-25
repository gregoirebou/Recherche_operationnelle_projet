class TransportProblem:
    def __init__(self, file):
        self.n = 0  # nombre de fournisseurs
        self.m = 0  # nombre de clients
        self.couts = []       # matrice n x m des coûts unitaires
        self.provisions = []  # liste de taille n
        self.commandes = []   # liste de taille m
        self.proposition = [] # matrice n x m de la proposition de transport
        self.load_from_file(file)

    def load_from_file(self, filepath):
        with open(filepath, 'r') as f:
            lignes = f.readlines()
        self.n, self.m = map(int, lignes[0].split())
        for i in range(1, self.n + 1):
            valeurs = list(map(int, lignes[i].split()))
            self.couts.append(valeurs[:self.m])
            self.provisions.append(valeurs[self.m])
        self.commandes = list(map(int, lignes[self.n + 1].split()))

    