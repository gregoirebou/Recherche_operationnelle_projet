import time
import random
import matplotlib.pyplot as plt
import os
import contextlib
from TransportProblem import TransportProblem
import pickle

class Complexite:
    def __init__(self):
        self.tailles_n = [10, 40, 100, 400]#, #1000, 4000, 10000]
        self.nb_iterations = 5
        self.fichier_sauvegarde = "sauvegarde_complexite.pkl"
        if os.path.exists(self.fichier_sauvegarde):
            print("\nSauvegarde trouvée, reprise des calculs là où ils s'étaient arrêtés")
            with open(self.fichier_sauvegarde, 'rb') as f:
                self.resultats = pickle.load(f)
        else:
            print("\nNouvelle étude de complexité (Aucune sauvegarde trouvée).")
            self.resultats = {
                "theta_NO": {n: [] for n in self.tailles_n},
                "theta_BH": {n: [] for n in self.tailles_n},
                "t_NO": {n: [] for n in self.tailles_n},
                "t_BH": {n: [] for n in self.tailles_n},
                "total_NO" : {},
                "total_BH" : {}
            }

    def generer_probleme_aleatoire(self, n):
        couts = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
        temp = [[random.randint(1, 100) for _ in range(n)] for _ in range(n)]
        provisions = [sum(row) for row in temp]
        temp_transpose = list(zip(*temp))
        commandes = [sum(col) for col in temp_transpose]
        return couts, provisions, commandes

    def mesurer_temps(self, n):
        couts, provisions, commandes = self.generer_probleme_aleatoire(n)

        pb_no = TransportProblem(from_data=(n, couts, provisions.copy(), commandes.copy()))
        pb_bh = TransportProblem(from_data=(n, couts, provisions.copy(), commandes.copy()))

        with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):

            debut_no = time.perf_counter()
            pb_no.NorthWest()
            fin_no = time.perf_counter()
            theta_no = fin_no - debut_no

            debut_bh = time.perf_counter()
            pb_bh.BalasHammer()
            fin_bh = time.perf_counter()
            theta_bh = fin_bh - debut_bh

            debut_marchepied_no = time.perf_counter()
            pb_no.stepping_stone()
            fin_marchepied_no = time.perf_counter()
            t_no = fin_marchepied_no - debut_marchepied_no

            debut_marchepied_bh = time.perf_counter()
            pb_bh.stepping_stone()
            fin_marchepied_bh = time.perf_counter()
            t_bh = fin_marchepied_bh - debut_marchepied_bh

        return theta_no, t_no, theta_bh, t_bh

    def lancer_etude(self):
        try:
            for n in self.tailles_n:
                iterations_deja_faites = len(self.resultats["theta_NO"][n])

                if iterations_deja_faites >= self.nb_iterations:
                    print(f"n={n} déjà terminé ({self.nb_iterations}/{self.nb_iterations}).")
                    continue

                print(f"\nReprise des tests pour n = {n} (à partir de l'itération {iterations_deja_faites + 1})")

                for iter in range(iterations_deja_faites, self.nb_iterations):
                    pourcentage = int(((iter + 1) / self.nb_iterations) * 100)
                    nb_diezes = pourcentage // 2
                    barre = "#" * nb_diezes + "-" * (50 - nb_diezes)
                    print(f"\r[{barre}] {pourcentage}% ({iter + 1}/{self.nb_iterations})", end="", flush=True)

                    theta_no, t_no, theta_bh, t_bh = self.mesurer_temps(n)

                    self.resultats["theta_NO"][n].append(theta_no)
                    self.resultats["theta_BH"][n].append(theta_bh)
                    self.resultats["t_NO"][n].append(t_no)
                    self.resultats["t_BH"][n].append(t_bh)

                    with open(self.fichier_sauvegarde, 'wb') as f:
                        pickle.dump(self.resultats, f)

                print()

        except KeyboardInterrupt:
            print("\n\nPAUSE D'URGENCE ACTIVÉE !\nL'itération en cours a été annulée.\nToutes les itérations précédentes sont sauvegardées.")

    def tracer_graphiques(self):
        for n in self.tailles_n:
            somme_no = [self.resultats["theta_NO"][n][i] + self.resultats["t_NO"][n][i] for i in range(self.nb_iterations)]
            self.resultats["total_NO"][n] = somme_no

            somme_bh = [self.resultats["theta_BH"][n][i] + self.resultats["t_BH"][n][i] for i in range(self.nb_iterations)]
            self.resultats["total_BH"][n] = somme_bh

        metriques = [
            ("theta_NO", "Temps initial NO (θ_NO)"),
            ("theta_BH", "Temps initial BH (θ_BH)"),
            ("t_NO", "Temps Marche-pied (source NO)"),
            ("t_BH", "Temps Marche-pied (source BH)"),
            ("total_NO", "Temps total (θ_NO + t_NO)"),
            ("total_BH", "Temps total (θ_BH + t_BH)")
        ]

        plt.figure(figsize=(15, 10))
        plt.suptitle("Étude de complexité : Nuages de points et Pire Cas (Max)")

        for i, (key, label) in enumerate(metriques, 1):
            plt.subplot(3, 2, i)

            x_points = []
            y_points = []
            x_max = []
            y_max = []

            for n in self.tailles_n:
                temps = self.resultats[key][n]
                x_points.extend([n] * self.nb_iterations)
                y_points.extend(temps)

                x_max.append(n)
                y_max.append(max(temps))

            plt.scatter(x_points, y_points, alpha=0.2, s=5, label=f"Réalisations ({self.nb_iterations}/n)")

            plt.plot(x_max, y_max, 'r-o', linewidth=2, label="Pire cas (Max)")

            plt.xscale('log')
            plt.yscale('log')
            plt.xlabel("Taille n (n=m)")
            plt.ylabel("Temps (secondes)")
            plt.title(label)
            plt.grid(True, which="both", ls="-", alpha=0.5)
            plt.legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def tracer_comparaison(self):
        x_n = []
        y_ratio_max = []

        for n in self.tailles_n:
            ratios = []
            for i in range(self.nb_iterations):
                total_no = self.resultats["theta_NO"][n][i] + self.resultats["t_NO"][n][i]
                total_bh = self.resultats["theta_BH"][n][i] + self.resultats["t_BH"][n][i]

                if total_bh > 0:
                    ratios.append(total_no / total_bh)
                else:
                    ratios.append(1)

            x_n.append(n)
            y_ratio_max.append(max(ratios))

        plt.figure(figsize=(10, 6))

        plt.plot(x_n, y_ratio_max, 'b-o', linewidth=2, label="Ratio Max (NO / BH)")

        plt.axhline(y=1, color='r', linestyle='--', label="Égalité (Ratio = 1)")

        plt.xscale('log')
        plt.xlabel("Taille n")
        plt.ylabel("Ratio $\\frac{t_{NO} + \\theta_{NO}}{t_{BH} + \\theta_{BH}}$")
        plt.title("Comparaison de la complexité dans le pire des cas (Ratio Max)")
        plt.grid(True, which="both", ls="-", alpha=0.5)
        plt.legend()
        plt.show()

    def analyser_complexite_empirique(self):
        import math

        print("\n" + "="*70)
        print("   ANALYSE PIRE CAS DE LA COMPLEXITÉ")
        print("="*70)

        metriques = [
            ("total_NO", "Nord-Ouest + Marche-Pied"),
            ("total_BH", "Balas-Hammer + Marche-Pied")
        ]

        for cle_metrique, nom_metrique in metriques:
            print(f"\n[{nom_metrique}]")

            print("\n1. Ratios Temps / n^k (On cherche la colonne qui se stabilise) :")
            print(f"{'n':<8} | {'Temps max(s)':<12} | {'T / n':<12} | {'T / n^2':<12} | {'T / n^3':<12} | {'T / n^4':<12}")
            print("-" * 65)

            temps_max_par_n = {}
            for n in self.tailles_n:
                if not self.resultats[cle_metrique].get(n):
                    continue
                t_max = max(self.resultats[cle_metrique][n])
                temps_max_par_n[n] = t_max

                t_n = t_max / n
                t_n2 = t_max / (n**2)
                t_n3 = t_max / (n**3)
                t_n4 = t_max / (n**4)

                print(f"{n:<8} | {t_max:<12.5f} | {t_n:<12.6f} | {t_n2:<12.8f} | {t_n3:<12.10f} | {t_n3:<12.10f}")

            print("\n2. Rapports de croissance entre étapes :")
            etapes = [(10, 40), (40, 100), (100, 400), (40, 400)]

            for n1, n2 in etapes:
                if n1 in temps_max_par_n and n2 in temps_max_par_n:
                    t1 = temps_max_par_n[n1]
                    t2 = temps_max_par_n[n2]

                    if t1 > 0:
                        ratio_temps = t2 / t1
                        ratio_n = n2 / n1

                        k_empirique = math.log(ratio_temps) / math.log(ratio_n)

                        print(f"  > Passage de n={n1} à n={n2} (Taille x{ratio_n:.1f})")
                        print(f"    - Le temps a été multiplié par : x{ratio_temps:.2f}")
                        print(f"    - Puissance déduite (O(n^k))   : k ≈ {k_empirique:.2f}")
            print("-" * 70)