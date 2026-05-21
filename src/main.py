import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from equipements import Routeur, Switch, Firewall, Serveur
from topologie import Topologie
from moniteur import NetworkMonitor
from paquets import Paquet, SimulateurTransit


def creer_reseau_demo(topologie):
    print("\n Chargement du reseau de demonstration...")

    r1  = Routeur("R1_principal",     "192.168.1.1",  "Cisco")
    s1  = Serveur("Serveur_web",      "192.168.1.10", "Dell")
    f1  = Firewall("Firewall_sortie", "10.0.0.1",     "Fortinet")
    sw1 = Switch("Switch_RDC",        "192.168.1.2",  "HP")

    topologie.ajouter_equipement(r1)
    topologie.ajouter_equipement(s1)
    topologie.ajouter_equipement(f1)
    topologie.ajouter_equipement(sw1)

    topologie.connecter("R1_principal", "Serveur_web",     1000, 2)
    topologie.connecter("R1_principal", "Firewall_sortie",  100, 10)
    topologie.connecter("R1_principal", "Switch_RDC",       100, 1)

    print("\n [OK] Reseau de demonstration charge.\n")
    return f1


def sous_menu_ajout_equipement(topologie):
    print("\n  Quel type d'equipement voulez-vous ajouter ?")
    print("  1. Routeur")
    print("  2. Switch")
    print("  3. Serveur")
    print("  4. Firewall")

    choix  = input("  Votre choix (1-4)    : ").strip()
    nom    = input("  Nom de l'equipement  : ").strip()
    ip     = input("  Adresse IP           : ").strip()
    marque = input("  Marque               : ").strip()

    if nom in topologie.appareils:
        print(f" [!] Un équipement nommé '{nom}' existe déjà.")
        return

    if choix == "1":
        topologie.ajouter_equipement(Routeur(nom, ip, marque))
    elif choix == "2":
        topologie.ajouter_equipement(Switch(nom, ip, marque))
    elif choix == "3":
        topologie.ajouter_equipement(Serveur(nom, ip, marque))
    elif choix == "4":
        topologie.ajouter_equipement(Firewall(nom, ip, marque))
    else:
        print(" [!] Choix invalide.")


def sous_menu_supprimer_equipement(topologie):
    nom = input("  Nom de l'équipement à supprimer : ").strip()
    if nom not in topologie.appareils:
        print(f"  [!] '{nom}' introuvable.")
        return
    del topologie.appareils[nom]
    topologie.liens = [
        l for l in topologie.liens
        if l.equipement_a.nom != nom and l.equipement_b.nom != nom
    ]
    print(f" [OK] '{nom}' supprimé.")


def sous_menu_ajouter_lien(topologie):
    print("\n Equipements disponibles :")
    for nom in topologie.appareils:
        print(f"    - {nom}")

    nom_a   = input("\n Nom équipement A      : ").strip()
    nom_b   = input("   Nom équipement B      : ").strip()
    debit   = input("   Bande passante (Mbps) : ").strip()
    latence = input("   Latence (ms)          : ").strip()

    try:
        debit   = float(debit)
        latence = float(latence)
    except ValueError:
        print(" [!] Valeurs incorrectes.")
        return

    topologie.connecter(nom_a, nom_b, debit, latence)


def sous_menu_supprimer_lien(topologie):
    print("\n  Liens existants :")
    if not topologie.liens:
        print("  (Aucun lien configuré)")
        return
    for i, lien in enumerate(topologie.liens):
        print(f"    {i+1}. {lien.equipement_a.nom} <---> {lien.equipement_b.nom} "
              f"| {lien.debit} Mbps | {lien.latence} ms")

    nom_a = input("\n  Nom équipement A : ").strip()
    nom_b = input("   Nom équipement B : ").strip()

    avant = len(topologie.liens)
    topologie.liens = [
        l for l in topologie.liens
        if not ({l.equipement_a.nom, l.equipement_b.nom} == {nom_a, nom_b})
    ]
    if len(topologie.liens) < avant:
        print(f"  [OK] Lien entre '{nom_a}' et '{nom_b}' supprimé.")
    else:
        print(f"  [!] Lien introuvable.")


def sous_menu_activer_desactiver(topologie):
    nom = input("  Nom de l'équipement : ").strip()
    if nom not in topologie.appareils:
        print(f"  [!] '{nom}' introuvable.")
        return
    eq = topologie.appareils[nom]
    if eq.est_actif:
        eq.est_actif = False
        print(f"  [OK] '{nom}' désactivé.")
    else:
        eq.est_actif = True
        print(f"  [OK] '{nom}' activé.")


def sous_menu_afficher_details(topologie):
    nom = input("  Nom de l'équipement : ").strip()
    if nom not in topologie.appareils:
        print(f"  [!] '{nom}' introuvable.")
        return
    eq = topologie.appareils[nom]
    print(f"\n  {'='*40}")
    print(f"  {eq}")
    print(f"  Type    : {type(eq).__name__}")
    if isinstance(eq, Routeur):
        print(f"  Routes  : {len(eq.table_deroutage)} entrée(s)")
    elif isinstance(eq, Switch):
        print(f"  VLANs   : {eq.vlans if eq.vlans else 'Aucun configuré'}")
    elif isinstance(eq, Serveur):
        print(f"  Services: {getattr(eq, 'services', 'Non défini')}")
    elif isinstance(eq, Firewall):
        print(f"  Règles  : {len(eq.regles)} règle(s)")
    connectes = [
        l for l in topologie.liens
        if l.equipement_a.nom == nom or l.equipement_b.nom == nom
    ]
    print(f"\n  Liens connectés ({len(connectes)}) :")
    for l in connectes:
        voisin = l.equipement_b.nom if l.equipement_a.nom == nom else l.equipement_a.nom
        print(f"    -> {voisin} | {l.debit} Mbps | {l.latence} ms")
    print(f"  {'='*40}\n")


def executer_envoi_paquet(topologie, simulateur):
    print("\n--- ENVOI D'UN PAQUET ---")
    print(" Équipements disponibles :")
    for nom in topologie.appareils:
        print(f"    - {nom}")

    src  = input("\n Nom equipement source      : ").strip()
    dest = input("  Nom equipement destination : ").strip()

    if src not in topologie.appareils:
        print(f" [!] '{src}' introuvable.")
        return
    if dest not in topologie.appareils:
        print(f" [!] '{dest}' introuvable.")
        return

    proto     = input("  Protocole (TCP/UDP/ICMP)   : ").strip().upper()
    taille_in = input("  Taille en octets [512]     : ").strip()
    port_in   = input("  Port cible (vide si aucun) : ").strip()

    try:
        taille = float(taille_in) if taille_in else 512.0
        port   = int(port_in) if port_in else None
    except ValueError:
        print(" [!] Taille ou port invalide.")
        return

    paquet = Paquet(src, dest, proto, taille, port)
    simulateur.envoyer_paquet(paquet)


def gerer_firewall_interactif(topologie):
    print("\n--- GESTION DU PARE-FEU ---")
    fw_liste = {n: eq for n, eq in topologie.appareils.items() if isinstance(eq, Firewall)}

    if not fw_liste:
        print(" [!] Aucun pare-feu dans la topologie.")
        return

    print(" Firewalls disponibles :")
    for nom in fw_liste:
        print(f"    - {nom}")

    nom_fw = input("\n Nom du pare-feu a configurer : ").strip()
    fw = topologie.appareils.get(nom_fw)

    if not fw or not isinstance(fw, Firewall):
        print(" [!] Equipement introuvable ou ce n'est pas un pare-feu.")
        return

    mdp = input(" Mot de passe administrateur  : ")
    if not fw.authentifier(mdp):
        return

    while True:
        print(f"\n  ---- Firewall : {nom_fw} ----")
        print("  1. Ajouter une regle")
        print("  2. Supprimer une regle")
        print("  3. Afficher les regles")
        print("  4. Afficher le journal")
        print("  5. Inspecter un paquet manuellement")
        print("  0. Retour au menu principal")

        c = input("  Votre choix : ").strip()

        if c == "1":
            print("\n  Ajout d'une regle :")
            while True:
                action = input("   Action (AUTORISER/BLOQUER) : ").strip().upper()
                if action in ["AUTORISER", "BLOQUER"]:
                    break
                print("   Entrez AUTORISER ou BLOQUER.")
            ip_src  = input("   IP source (obligatoire)    : ").strip()
            proto   = input("   Protocole (vide = tous)    : ").strip().upper() or None
            port_in = input("   Port (vide = tous)         : ").strip()
            port    = int(port_in) if port_in.isdigit() else None
            plage   = input("   Plage reseau (vide = tous) : ").strip() or None
            fw.ajouter_regle(action, ip_src, proto, port, plage)

        elif c == "2":
            fw.afficher_regles()
            if fw.regles:
                try:
                    idx = int(input("  Index a supprimer : "))
                    fw.supprimer_regle(idx)
                except ValueError:
                    print("  [!] Index invalide.")

        elif c == "3":
            fw.afficher_regles()

        elif c == "4":
            fw.afficher_journal()

        elif c == "5":
            ip_test    = input("  IP source a tester  : ").strip()
            proto_test = input("  Protocole           : ").strip().upper() or None
            port_str   = input("  Port                : ").strip()
            port_test  = int(port_str) if port_str.isdigit() else None
            res = fw.inspecter_paquet(ip_test, proto_test, port_test)
            print(f"  Resultat : {res}")

        elif c == "0":
            break
        else:
            print("  [!] Choix invalide.")


def afficher_statistiques(moniteur, topologie):
    print(f"\n  {'='*45}")
    print("  STATISTIQUES DU RESEAU")
    print(f"  {'='*45}")

    actifs   = sum(1 for eq in topologie.appareils.values() if eq.est_actif)
    inactifs = sum(1 for eq in topologie.appareils.values() if not eq.est_actif)
    print(f"  Equipements actifs   : {actifs}")
    print(f"  Equipements inactifs : {inactifs}")
    print(f"  Liens configures     : {len(topologie.liens)}")

    print(f"\n  Trafic par equipement :")
    if moniteur.stats:
        for nom, data in moniteur.stats.items():
            total = data['sent'] + data['lost']
            taux  = (data['lost'] / total * 100) if total > 0 else 0
            print(f"    {nom} : {data['sent']} transmis | "
                  f"{data['lost']} perdus | taux {taux:.1f}%")
    else:
        print("    (Aucune donnee — envoyez des paquets d'abord)")

    if moniteur.packet_history:
        print(f"\n  Historique (10 derniers) :")
        for entry in moniteur.packet_history:
            print(f"    {entry}")
    print(f"  {'='*45}\n")


def generer_rapport(moniteur, topologie):
    for lien in topologie.liens:
        if not hasattr(lien, 'bandwidth'):
            lien.bandwidth = lien.debit

    from datetime import datetime
    with open("rapport_simnet.txt", "w", encoding="utf-8") as f:
        f.write("=== SIMNet — RAPPORT RESEAU ===\n")
        f.write(f"Genere le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("1. EQUIPEMENTS :\n")
        for nom, eq in topologie.appareils.items():
            statut = "ACTIF" if eq.est_actif else "INACTIF"
            f.write(f"  - {nom} ({eq.ip}) : {statut}\n")
        f.write("\n2. LIENS :\n")
        for lien in topologie.liens:
            f.write(f"  - {lien.equipement_a.nom} <-> {lien.equipement_b.nom} "
                    f"| {lien.debit} Mbps | {lien.latence} ms "
                    f"| {lien.octets_transmis} octets transmis\n")
        f.write("\n3. STATISTIQUES :\n")
        for nom, data in moniteur.stats.items():
            f.write(f"  - {nom} : {data['sent']} transmis, {data['lost']} perdus\n")
        f.write("\n4. DERNIERS PAQUETS :\n")
        for log in moniteur.packet_history:
            f.write(f"  {log}\n")

    print(" [OK] Rapport exporte : rapport_simnet.txt")


def afficher_menu():
    print("\n" + "╔" + "═"*45 + "╗")
    print("║         SIMNet — Simulateur Reseau v1.0     ║")
    print("╠" + "═"*45 + "╣")
    print("║  1.  Afficher le reseau (topologie)         ║")
    print("║  2.  Ajouter un equipement                  ║")
    print("║  3.  Supprimer un equipement                ║")
    print("║  4.  Ajouter un lien                        ║")
    print("║  5.  Supprimer un lien                      ║")
    print("║  6.  Envoyer un paquet                      ║")
    print("║  7.  Configurer Firewall                    ║")
    print("║  8.  Afficher les statistiques              ║")
    print("║  9.  Activer / Desactiver un equipement     ║")
    print("║  10. Details d'un equipement                ║")
    print("║  11. Generer le rapport                     ║")
    print("║  0.  Quitter                                ║")
    print("╚" + "═"*45 + "╝")
    return input("  Votre choix : ").strip()


def main():
    print("\n" + "="*50)
    print("   Bienvenue dans SIMNet")
    print("   Simulateur de Reseau — ING3 SRT 2025/2026")
    print("   Institut Saint Jean — M. Fedim")
    print("="*50)

    topologie_globale = Topologie()
    firewall_demo     = creer_reseau_demo(topologie_globale)
    moniteur          = NetworkMonitor(topologie_globale)
    simulateur        = SimulateurTransit(topologie_globale, moniteur)

    while True:
        choix = afficher_menu()

        if choix == "1":
            topologie_globale.afficher_reseau()
        elif choix == "2":
            sous_menu_ajout_equipement(topologie_globale)
        elif choix == "3":
            sous_menu_supprimer_equipement(topologie_globale)
        elif choix == "4":
            sous_menu_ajouter_lien(topologie_globale)
        elif choix == "5":
            sous_menu_supprimer_lien(topologie_globale)
        elif choix == "6":
            executer_envoi_paquet(topologie_globale, simulateur)
        elif choix == "7":
            gerer_firewall_interactif(topologie_globale)
        elif choix == "8":
            afficher_statistiques(moniteur, topologie_globale)
        elif choix == "9":
            sous_menu_activer_desactiver(topologie_globale)
        elif choix == "10":
            sous_menu_afficher_details(topologie_globale)
        elif choix == "11":
            generer_rapport(moniteur, topologie_globale)
        elif choix == "0":
            print("\n  Au revoir ! Simulation terminee.\n")
            break
        else:
            print("  [!] Choix invalide. Entrez un nombre entre 0 et 11.")


if __name__ == "__main__":
    main()