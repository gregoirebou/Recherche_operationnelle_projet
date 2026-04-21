from Complexite import Complexite
from TransportProblem import TransportProblem
import contextlib
import sys


def main():
    continuer = True
    while continuer:
        num = input("\nEntrez le numéro du problème à traiter (1-12) : ")
        filename = f"Probleme{num}.txt"

        try:
            transport = TransportProblem(filename)
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable.")
            continue
        print("\n--- Tableau de contraintes ---")
        print(transport)
        print("\nChoisissez l'algorithme pour la proposition initiale :")
        print("  1. Nord-Ouest")
        print("  2. Balas-Hammer")
        choix = input("Votre choix : ")

        if choix == "1":
            print("\n--- Méthode Nord-Ouest ---")
            transport.NorthWest()
        elif choix == "2":
            print("\n--- Méthode Balas-Hammer ---")
            transport.BalasHammer()
        else:
            print("Choix invalide, Nord-Ouest par défaut.")
            transport.NorthWest()

        print("\n--- Proposition initiale ---")
        print(transport)
        print(f"Coût total : {transport.totalcost()}")
        print("\n--- Méthode du marche-pied ---")
        transport.stepping_stone()

        print("\n--- Proposition optimale ---")
        print(transport)
        print(f"Coût total optimal : {transport.totalcost()}")
        rep = input("\nVoulez-vous tester un autre problème ? (o/n) : ")
        continuer = rep.strip().lower() == "o"

    print("Fin du programme.")


def run_all_problems():
    with open("trace_execution.txt", "w", encoding="utf-8") as f:
        with contextlib.redirect_stdout(f):
            for num in range(1, 13):
                filename = f"Probleme{num}.txt"
                print(f"\n{'='*60}")
                print(f"  PROBLÈME {num}")
                print(f"{'='*60}")

                try:
                    transport = TransportProblem(filename)
                except FileNotFoundError:
                    print(f"Fichier {filename} introuvable, problème ignoré.")
                    continue

                print("\n--- Tableau de contraintes ---")
                print(transport)

                for algo, nom in [("NW", "Nord-Ouest"), ("BH", "Balas-Hammer")]:
                    print(f"\n{'='*40}")
                    print(f"  Algorithme : {nom}")
                    print(f"{'='*40}")

                    t = TransportProblem(filename)
                    if algo == "NW":
                        t.NorthWest()
                    else:
                        t.BalasHammer()

                    print("\n--- Proposition initiale ---")
                    print(t)
                    print(f"Coût total : {t.totalcost()}")

                    print("\n--- Méthode du marche-pied ---")
                    t.stepping_stone()

                    print("\n--- Proposition optimale ---")
                    print(t)
                    print(f"Coût total optimal : {t.totalcost()}")

    print("Trace écrite dans trace_execution_2.2.txt")

def run_complexity_study():
    print("\n" + "="*50)
    print("  LANCEMENT DE L'ÉTUDE DE COMPLEXITÉ ")
    print("="*50)
    etude = Complexite()
    etude.lancer_etude()
    print("\nCalculs terminés ! Génération des graphiques en cours...")
    etude.tracer_graphiques()
    print("Étude de complexité terminée.")

if __name__ == "__main__":
    run_complexity_study()