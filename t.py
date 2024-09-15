import atexit
import pickle

# Liste à sauvegarder
ma_liste = [1, 2, 3, 4, 5]


# Fonction appelée lors de la fin du programme
def sauvegarder_liste():
    with open("ma_liste_sauvegardeeoooo.pkl", "wb") as f:
        pickle.dump(ma_liste, f)
    print("Liste sauvegardée dans 'ma_liste_sauvegardee.pkl'")


# Enregistrer la fonction à appeler à la fin du programme
atexit.register(sauvegarder_liste)

print("Le programme est en cours d'exécution. Appuyez sur Ctrl + C pour l'arrêter.")

# Boucle infinie pour simuler un programme qui tourne
while True:

    t = input("Salut !")
