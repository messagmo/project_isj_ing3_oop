
import sys
import os

import topologie 

sys.path.insert(0, os.path.dirname(__file__))

from equipements import (
    Routeur,
    Switch,
    Firewall,
    Serveur,
    Topologie
)
from moniteur import NetworkMonitor  


""" Module 2 : Topologie """ 

""" Module 3 : Paquets """

""" Module 4 : Securité """


def creer_reseau_demo(topologie):


    print("\n [*] chargement du reseau de demonstration...")

 
      # Création des équipements
    r1 = Routeur("R1_principal", "192.168.1.1", "Cisco")
    s1 = Serveur("Serveur_web", "192.168.1.10", "Dell")
    f1 = Firewall("Firewall_sortie", "10.0.0.1", "Fortinet")
    sw1 = Switch("Switch_RDC", "192.168.1.2", "HP")


    # Ajout de chaque équipement à la topologie
    # topologie.ajouter_equipement(equipement) 
    topologie.ajouter_equipement(r1)
    topologie.ajouter_equipement(s1)
    topologie.ajouter_equipement(f1)
    topologie.ajouter_equipement(sw1)


    # Creation des liens avec topologie.connecter(nom_a, nom_b, debit, latence)
    topologie.connecter("R1_principal", "Serveur_web", 1000, 2)
    topologie.connecter("R1_principal", "Firewall_sortie", 100, 10)
    topologie.connecter("R1_principal", "Switch_RDC", 100, 1)

    print("\n [OK] reseau de demonstration charge avec succes.")

    return f1  # On retourne le firewall pour les tests de sécurité dans le module 4



def sous_menu_ajout_equipement(topologie):

    print("\n  Quel type d'equipement voulez-vous ajouter ?")
    print("  1. Routeur")
    print("  2. Switch")
    print("  3. Serveur")
    print("  4. Firewall")


    choix = input("   Nom de l'equipement : ").strip()

    nom    = input("  Nom de l'equipement  : ").strip()
    ip     = input("  Adresse IP           : ").strip()
    marque = input("  Marque               : ").strip()


     # Verification que le nom n'est pas déjà utilisé 
    if nom in topologie.appareils:
        print(f" [!] Un équipement nommé '{nom}' existe déjà. ")
        return
    

    # Création de l'équipement selon le type choisi
    if choix == "1":
        topologie.ajouter_equipement(Routeur(nom, ip, marque))

    elif choix == "2":
        topologie.ajouter_equipement(Switch(nom, ip, marque))

    elif choix == "3":
        topologie.ajouter_equipement(Serveur(nom, ip, marque))

    elif choix == "4":
        topologie.ajouter_equipement(Firewall(nom, ip, marque))

    
    else: 
        print(" [!] Choix invalide. ")
    

def sous_menu_supprimer_equipement(topologie):
    nom = input ("  Nom de l'équipement à supprimer : ").strip()

    # Vérification que l'équipement existe
    if nom not in topologie.appareils: 
        print(f"  [!] équipement '{nom}' introuvable.")
        return

    
    # Suppression de l'équipement du dictionnaire
    del topologie.appareils[nom]


    # Suppression de tous les liens qui implique cet équipement 
    topologie.liens = [
        lien for lien in topologie.liens
        if lien.equipement_a.nom != nom and lien.equipement_b.nom != nom 
    ]

    print(f" [OK] '{nom}' supprimé. ")

def sous_menu_ajouter_lien(topologie):

    print("\n équipement disponibles :")

    for nom in topologie.appareils:
        print(f"    - {nom}")


    # Saisie des deux équipement à relier
    nom_a = input("\n Nom équipement A      :").strip()
    nom_b = input("   Nom équipement B      :").strip()
    debit = input(" Bande passante (Mbps)   :").strip()
    nom_a = input(" Latence(ms)             :").strip()
