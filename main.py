from Complexite import Complexite
from TransportProblem import TransportProblem
import contextlib


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


def run_all_problems(groupe=6, equipe=1):
    for num in range(1, 13):
        filename = f"Probleme{num}.txt"

        try:
            TransportProblem(filename)  # vérifie que le fichier existe
        except FileNotFoundError:
            print(f"Fichier {filename} introuvable, problème ignoré.")
            continue

        for algo, nom, suffixe in [("NW", "Nord-Ouest", "no"), ("BH", "Balas-Hammer", "bh")]:
            trace_filename = f"{groupe}-{equipe}-trace{num}-{suffixe}.txt"

            with open(trace_filename, "w", encoding="utf-8") as f:
                with contextlib.redirect_stdout(f):
                    print(f"{'='*60}")
                    print(f"  PROBLÈME {num} — {nom}")
                    print(f"{'='*60}")

                    t = TransportProblem(filename)
                    print("\n--- Tableau de contraintes ---")
                    print(t)

                    if algo == "NW":
                        print("\n--- Méthode Nord-Ouest ---")
                        t.NorthWest()
                    else:
                        print("\n--- Méthode Balas-Hammer ---")
                        t.BalasHammer()

                    print("\n--- Proposition initiale ---")
                    print(t)
                    print(f"Coût total : {t.totalcost()}")

                    print("\n--- Méthode du marche-pied ---")
                    t.stepping_stone()

                    print("\n--- Proposition optimale ---")
                    print(t)
                    print(f"Coût total optimal : {t.totalcost()}")

            print(f"Trace écrite : {trace_filename}")


def run_complexity_study():
    print("\n" + "="*50)
    print("  LANCEMENT DE L'ÉTUDE DE COMPLEXITÉ ")
    print("="*50)
    etude = Complexite()
    etude.lancer_etude()
    print("\nCalculs terminés ! Génération des graphiques en cours...")
    etude.tracer_graphiques()
    etude.analyser_complexite_empirique()
    print("Étude de complexité terminée.")


if __name__ == "__main__":
    #run_complexity_study()
    # main()
    run_all_problems(6,1)