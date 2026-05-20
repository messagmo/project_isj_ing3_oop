
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


    print("\n2" \
    " chargement du reseau de demonstration...")

 
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
    latence = input(" Latence(ms)             :").strip()


    # Conversion en nombres avec gestion d'erreur
    try:
        debit = float(debit)
        latence = float(latence)
    except ValueError:
        print(" [!] debit et latence doivent être des nombres entiers.")
        return
    
    
    # Appel de la méthode connecter() codée dans Topologie
    topologie.connecter(nom_a, nom_b, debit, latence)


def sous_menu_supprimer_lien(topologie):

    
    # Supprime le lien entre deux équipements
    print("\n  Liens existants :")
    if not topologie.liens:
        print("  (Aucun lien configuré)")
        return
 
    # Affichage des liens existants
    for i, lien in enumerate(topologie.liens):
        print(f"    {i+1}. {lien.equipement_a.nom} <---> {lien.equipement_b.nom} "
              f"| {lien.debit} Mbps | {lien.latence} ms")
 
    nom_a = input("\n  Nom équipement A : ").strip()
    nom_b = input("  Nom équipement B : ").strip()

    
    # Recherche et suppression du lien correspondant
    avant = len(topologie.liens)
    topologie.liens = [
        lien for lien in topologie.liens
        if not ({lien.equipement_a.nom, lien.equipement_b.nom} == {nom_a, nom_b})
    ]
 
    # Vérification que la suppression a bien eu lieu
    if len(topologie.liens) < avant:
        print(f"  [OK] Lien entre '{nom_a}' et '{nom_b}' supprimé.")
    else:
        print(f"  [!] Lien introuvable entre '{nom_a}' et '{nom_b}'.")
 
 
def sous_menu_activer_desactiver(topologie):
    
    #Bascule le statut actif/inactif d'un équipement.
    #Modifie l'attribut est_actif défini dans Equipement.

    nom = input("  Nom de l'équipement : ").strip()
 
    # Recherche dans le dictionnaire topologie.appareils
    if nom not in topologie.appareils:
        print(f"  [!] Équipement '{nom}' introuvable.")
        return
 
    eq = topologie.appareils[nom]  # Récupération de l'objet
 
    # On inverse le statut : True en False ou False en True
    if eq.est_actif:
        eq.est_actif = False
        print(f"  [OK] '{nom}' désactivé.")
    else:
        eq.est_actif = True
        print(f"  [OK] '{nom}' activé.")
 
 
def sous_menu_afficher_details(topologie):

        # Affiche les détails d'un équipement, y compris les liens connectés.

    nom = input("  Nom de l'équipement : ").strip()
 
    if nom not in topologie.appareils:
        print(f"  [!] Équipement '{nom}' introuvable.")
        return
 
    eq = topologie.appareils[nom]  
 
    # Affichage des infos principales (via __str__ de Equipement)
    print(f"\n  {'='*40}")
    print(f"  {eq}")
    print(f"  Type    : {type(eq).__name__}")  # Affiche "Routeur", "Switch", etc.
 
    # Infos spécifiques selon le type d'équipement
    if isinstance(eq, Routeur):
        # isinstance() vérifie si l'objet est une instance de Routeur

        nb_routes = len(eq.table_deroutage)
        print(f"  Routes  : {nb_routes} entrée(s) dans la table")
 
    elif isinstance(eq, Switch):
        print(f"  VLANs   : {eq.vlans if eq.vlans else 'Aucun configuré'}")
 
    elif isinstance(eq, Serveur):
        print(f"  Services: {eq.services}")
 
    elif isinstance(eq, Firewall):
        nb_regles = len(eq.regles)
        print(f"  Règles  : {nb_regles} règle(s) configurée(s)")
 
    # Affichage des liens connectés à cet équipement
    liens_connectes = [
        lien for lien in topologie.liens
        if lien.equipement_a.nom == nom or lien.equipement_b.nom == nom
    ]
    print(f"\n  Liens connectés ({len(liens_connectes)}) :")
    if liens_connectes:
        for lien in liens_connectes:
            voisin = lien.equipement_b.nom if lien.equipement_a.nom == nom else lien.equipement_a.nom
            print(f"    → {voisin} | {lien.debit} Mbps | {lien.latence} ms")
    else:
        print("    (Aucun lien)")
    print(f"  {'='*40}\n")
 
 

# FONCTIONS RAMENÉES DES MODULES 2, 3, 4 (PLACEHOLDERS)
# Ces fonctions affichent un message temporaire en attendant que les autres modules soient codés 
 

def placeholder_firewall(topologie):
    """
    Placeholder pour le Module 3 (securite.py).
    Quand securite.py sera prêt, on remplacera ce code par :
        gestionnaire.configurer_regle_interactive()
    """
    print("\n╔══════════════════════════════════════╗")
    print("  ║  Module 4 — Sécurité Firewall        ║")
    print("  ║  En attente de securite.py           ║")
    print("  ╚══════════════════════════════════════╝")
    print("\n  Pour brancher ce module :")
    print("  1. Terminer securite.py")
    print("  2. Décommenter dans main.py :")
    print("       from securite import GestionnaireSecurite")
    print("  3. Remplacer cette fonction par le vrai code")
 
    # CODE QUAND securite.py EST PRÊT 
    # gestionnaire.configurer_regle_interactive()



def placeholder_envoyer_paquet(topologie, moniteur):
    
    # Placeholder pour le Module 2 (paquets.py).
    # Quand paquets.py sera prêt, on remplacera ce code par :
    #    paquet = Paquet(src, dest, protocole, taille, priorite)
    #    simulateur.envoyer_paquet(paquet)
    
    print("\n╔══════════════════════════════════════╗")
    print("  ║  Module 3 — Simulation trafic        ║")
    print("  ║  En attente de paquets.py            ║")
    print("  ╚══════════════════════════════════════╝")
    print("\n  Pour brancher ce module :")
    print("  1. Terminer paquets.py")
    print("  2. Décommenter dans main.py :")
    print("       from paquets import Paquet, Simulateur")
    print("  3. Remplacer cette fonction par le vrai code")
 
    #   CODE pour paquets.py EST PRÊT 
    # print("\n  --- Envoi d'un paquet ---")
    # src      = input("  IP source      : ").strip()
    # dest     = input("  IP destination : ").strip()
    # protocole = input("  Protocole TCP/UDP/ICMP : ").strip().upper()
    # taille   = int(input("  Taille (octets) [512] : ").strip() or "512")
    # priorite = int(input("  Priorité 1-5   [3]    : ").strip() or "3")
    # paquet   = Paquet(src, dest, protocole, taille, priorite)
    # simulateur.envoyer_paquet(paquet)
    # moniteur.log_packet(paquet, "transmitted")
 
 

 
 
def afficher_statistiques(moniteur, topologie):
    """
    Affiche les statistiques du réseau grâce au NetworkMonitor
    déjà codé dans moniteur.py.
    """
    print(f"\n  {'='*45}")
    print("  STATISTIQUES DU RÉSEAU")
    print(f"  {'='*45}")
 
    # Nombre d'équipements actifs et inactifs
    actifs   = sum(1 for eq in topologie.appareils.values() if eq.est_actif)
    inactifs = sum(1 for eq in topologie.appareils.values() if not eq.est_actif)
    print(f"  Équipements actifs   : {actifs}")
    print(f"  Équipements inactifs : {inactifs}")
    print(f"  Liens configurés     : {len(topologie.liens)}")
 
    # Statistiques de trafic depuis NetworkMonitor.stats
    print(f"\n  Trafic par équipement :")
    if moniteur.stats:
        for nom, data in moniteur.stats.items():
            total  = data['sent'] + data['lost']
            # Calcul du taux de perte (protection division par zéro)
            taux   = (data['lost'] / total * 100) if total > 0 else 0
            print(f"    {nom} : {data['sent']} transmis | "
                  f"{data['lost']} perdus | taux perte {taux:.1f}%")
    else:
        print("    (Aucune donnée — envoyez des paquets d'abord)")
 
    # Appel de l'historique depuis NetworkMonitor.afficher_historique()
    moniteur.afficher_historique()
    print(f"  {'='*45}\n")
 
 

# ================================================================
# MENU PRINCIPAL
# ================================================================

def afficher_menu():
    """
    Affiche le menu principal dans le terminal.
    Retourne le choix saisi par l'utilisateur.
    """
    print("\n" + "╔" + "═"*45 + "╗")
    print("║        SIMNet — Simulateur Réseau v1.0      ║")
    print("╠" + "═"*45 + "╣")
    print("║  1.  Afficher le réseau (topologie)         ║")
    print("║  2.  Ajouter un équipement                  ║")
    print("║  3.  Supprimer un équipement                ║")
    print("║  4.  Ajouter un lien                        ║")
    print("║  5.  Supprimer un lien                      ║")
    print("║  6.  Envoyer un paquet  [Module 2]          ║")
    print("║  7.  Configurer Firewall [Module 3]         ║")
    print("║  8.  Afficher les statistiques              ║")
    print("║  9.  Activer / Désactiver un équipement     ║")
    print("║  10. Détails d'un équipement                ║")
    print("║  11. Générer le rapport (rapport_simnet.txt)║")
    print("║  0.  Quitter                                ║")
    print("╚" + "═"*45 + "╝")
    return input("  Votre choix : ").strip()
 
 
# ================================================================
# FONCTION PRINCIPALE
# ================================================================
 
def main():
    """
    Lance le simulateur SIMNet.
    Initialise les composants et démarre la boucle du menu.
    """
    # Titre de bienvenue
    print("\n" + "="*50)
    print("   Bienvenue dans SIMNet")
    print("   Simulateur de Réseau — ING3 SRT 2025/2026")
    print("   Institut Saint Jean — M. Fedim")
    print("="*50)
 
    #  INITIALISATION 
 
    # Création de la topologie (utilise la classe de equipements.py)
    topologie = Topologie()
 
    # Chargement du réseau de démonstration
    firewall_demo = creer_reseau_demo(topologie)
 
    # Création du moniteur réseau (utilise la classe de moniteur.py)
    moniteur = NetworkMonitor(topologie)
 
    #  PLACEHOLDER : Simulateur (Module 2) 
    # Sera remplacé quand paquets.py sera prêt
    # simulateur = Simulateur(topologie)
 
    #  PLACEHOLDER : Gestionnaire sécurité (Module 3) 
    # Sera remplacé quand securite.py sera prêt
    # gestionnaire = GestionnaireSecurite(firewall_demo)
    #  BOUCLE PRINCIPALE 
    # Tourne indéfiniment jusqu'à ce que l'utilisateur tape '0'
    while True:
        choix = afficher_menu()  # Affiche le menu et lit le choix
 
        if choix == "1":
            # Appelle afficher_reseau() de la classe Topologie (equipements.py)
            topologie.afficher_reseau()
 
        elif choix == "2":
            # Sous-menu pour ajouter un équipement
            sous_menu_ajouter_equipement(topologie)
 
        elif choix == "3":
            # Sous-menu pour supprimer un équipement
            sous_menu_supprimer_equipement(topologie)
 
        elif choix == "4":
            # Sous-menu pour créer un lien
            sous_menu_ajouter_lien(topologie)
 
        elif choix == "5":
            # Sous-menu pour supprimer un lien
            sous_menu_supprimer_lien(topologie)
 
        elif choix == "6":
            # Module 2 — pas encore prêt → placeholder
            placeholder_envoyer_paquet(topologie, moniteur)
 
        elif choix == "7":
            # Module 3 — pas encore prêt → placeholder
            placeholder_firewall(topologie)
 
        elif choix == "8":
            # Affiche les statistiques via NetworkMonitor (moniteur.py)
            afficher_statistiques(moniteur, topologie)
 
        elif choix == "9":
            # Active ou désactive un équipement
            sous_menu_activer_desactiver(topologie)
 
        elif choix == "10":
            # Affiche les détails d'un équipement
            sous_menu_afficher_details(topologie)
 
        elif choix == "11":
            # Génère le rapport via NetworkMonitor.generate_report() (moniteur.py)
            moniteur.generate_report()
 
        elif choix == "0":
            # Quitter proprement
            print("\n  Au revoir ! Simulation terminée.\n")
            break  # Sort de la boucle while True
 
        else:
            # Choix non reconnu
            print("  [!] Choix invalide. Entrez un nombre entre 0 et 11.")
 
 
if __name__ == "__main__":
    main()