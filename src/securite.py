import json
import os
from datetime import datetime

# --- Fonction utilitaire de validation d'IP ---
def valider_format_ip(ip):
    """
    Vérifie si l'IP respecte le format X.X.X.X
    1er octet : [1, 255]
    Autres octets : [0, 255]
    """
    parties = ip.split('.')
    
    # Doit avoir exactement 4 parties
    if len(parties) != 4:
        return False, "L'adresse IP doit contenir exactement 4 octets (X.X.X.X)."
    
    try:
        # Tenter de convertir chaque partie en entier
        octets = [int(p) for p in parties]
    except ValueError:
        return False, "Les octets doivent être des nombres entiers."
    
    # Vérification du premier octet [1, 255]
    if not (1 <= octets[0] <= 255):
        return False, "Le premier octet doit être compris entre 1 et 255."
    
    # Vérification des autres octets [0, 255]
    for i in range(1, 4):
        if not (0 <= octets[i] <= 255):
            return False, f"L'octet {i+1} doit être compris entre 0 et 255."
            
    return True, "IP Valide"


class Equipement:
    def __init__(self, nom, ip, marque):
        self.nom = nom
        self.ip = ip
        self.marque = marque
        self.est_actif = True

    def __str__(self):
        etat = "Actif" if self.est_actif else "Inactif"
        return f"[{self.nom}] IP: {self.ip} | Marque: {self.marque} | Etat: {etat}"

class Firewall(Equipement):
    def __init__(self, nom, ip, marque):
        super().__init__(nom, ip, marque)
        
        self.fichier_regles = "regles.json"
        self.fichier_journal = "journal.json"
        self.fichier_config = "config.json"
        
        self.regles = []
        self.journal = []
        self.password = "admin123"
        self._authentifie = False

        self.charger_config()
        self.charger_donnees()

    def sauvegarder_config(self):
        try:
            with open(self.fichier_config, 'w') as f:
                json.dump({"password": self.password}, f)
        except Exception as e:
            print(f"Erreur sauvegarde config : {e}")

    def charger_config(self):
        if os.path.exists(self.fichier_config):
            try:
                with open(self.fichier_config, 'r') as f:
                    data = json.load(f)
                    self.password = data.get("password", "admin123")
            except Exception as e:
                print(f"Erreur lecture config : {e}")
                self.password = "admin123"

    def sauvegarder_donnees(self):
        try:
            with open(self.fichier_regles, 'w') as f:
                json.dump(self.regles, f, indent=4)
            with open(self.fichier_journal, 'w') as f:
                json.dump(self.journal, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde donnees : {e}")

    def charger_donnees(self):
        if os.path.exists(self.fichier_regles):
            try:
                with open(self.fichier_regles, 'r') as f:
                    self.regles = json.load(f)
                print(f"{len(self.regles)} regle(s) chargee(s).")
            except Exception as e:
                print(f"Erreur lecture regles : {e}")

        if os.path.exists(self.fichier_journal):
            try:
                with open(self.fichier_journal, 'r') as f:
                    self.journal = json.load(f)
            except Exception as e:
                print(f"Erreur lecture journal : {e}")

    def authentifier(self, mot_de_passe):
        if mot_de_passe == self.password:
            self._authentifie = True
            print("Authentification reussie.")
            return True
        else:
            self._authentifie = False
            print("Mot de passe incorrect.")
            return False

    def changer_mot_de_passe(self, ancien_mdp, nouveau_mdp):
        if ancien_mdp == self.password:
            self.password = nouveau_mdp
            print("Mot de passe modifie avec succes !")
            self.sauvegarder_config()
            return True
        else:
            print("Erreur : L'ancien mot de passe ne correspond pas.")
            return False

    def _verifier_acces(self):
        if not self._authentifie:
            print("Acces refuse. Veuillez vous authentifier d'abord.")
            return False
        return True

    def ajouter_regle(self, action, ip_source, protocole=None, port=None, plage_reseau=None):
        if not self._verifier_acces():
            return
        
        if port:
            try:
                port = int(port)
            except ValueError:
                print("Erreur: Le port doit être un nombre entier.")
                return

        regle = {
            "action": action.upper(),
            "ip_source": ip_source,
            "protocole": protocole.upper() if protocole else None,
            "port": port,
            "plage_reseau": plage_reseau
        }
        self.regles.append(regle)
        print(f"Regle ajoutee : {regle}")
        self.sauvegarder_donnees()

    def supprimer_regle(self, index):
        if not self._verifier_acces():
            return
        if 0 <= index < len(self.regles):
            supprimee = self.regles.pop(index)
            print(f"Regle supprimee : {supprimee}")
            self.sauvegarder_donnees()
        else:
            print("Index de regle invalide.")

    def afficher_regles(self):
        if not self._verifier_acces():
            return
        print("\n--- REGLES DU FIREWALL ---")
        if not self.regles:
            print("Aucune regle configuree. (Tout sera refuse par defaut)")
        for i, r in enumerate(self.regles):
            print(f"[{i}] {r}")

    def _ip_dans_plage(self, ip, plage):
        return ip.startswith(plage)

    def inspecter_paquet(self, ip_source, protocole, port):
        if port:
            try:
                port = int(port)
            except ValueError:
                port = None
        
        decision = None
        
        for regle in self.regles:
            correspondance = True
            
            if regle["ip_source"] and regle["ip_source"] != ip_source:
                correspondance = False
            
            if regle["protocole"]:
                if protocole is None or regle["protocole"].upper() != protocole.upper():
                    correspondance = False

            if regle["port"] and regle["port"] != port:
                correspondance = False

            if regle["plage_reseau"] and not self._ip_dans_plage(ip_source, regle["plage_reseau"]):
                correspondance = False
            
            if correspondance:
                decision = regle["action"]
                break
        
        if decision is None:
            decision = "REFUSER (Defaut)"
        
        self._journaliser(ip_source, protocole, port, decision)
        return decision

    def _journaliser(self, ip_source, protocole, port, decision):
        entree = {
            "horodatage": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ip_source": ip_source,
            "protocole": protocole,
            "port": port,
            "decision": decision
        }
        self.journal.append(entree)
        self.sauvegarder_donnees()

    def afficher_journal(self):
        if not self._verifier_acces():
            return
        print("\n--- JOURNAL DU FIREWALL ---")
        
        if not self.journal:
            print("Journal vide.")
            return

        print(f"{'Horodatage':<20} | {'IP Source':<16} | {'Proto:Port':<12} | {'Decision'}")
        
        print("-" * 70)
        
        for entree in self.journal:
            p_port = entree['port']
            port_str = str(p_port) if p_port is not None else "N/A"
            proto_str = str(entree['protocole']) if entree['protocole'] is not None else "N/A"
            proto_port = f"{proto_str}:{port_str}"
            print(f"{entree['horodatage']:<20} | {entree['ip_source']:<16} | {proto_port:<12} | {entree['decision']}")


if __name__ == "__main__":
    f1 = Firewall("Firewall_Sortie", "10.0.0.1", "Fortinet")

    auth_reussie = False
    while not auth_reussie:
        mdp = input("Mot de passe administrateur : ")
        if f1.authentifier(mdp):
            auth_reussie = True
            
            print("\nSouhaitez-vous changer le mot de passe ?")
            changer = input("o/n : ").lower()
            
            if changer == 'o':
                while True:
                    print("\n--- Changement de mot de passe ---")
                    ancien = input("Ancien mot de passe : ")
                    nouveau = input("Nouveau mot de passe : ")
                    confirmation = input("Confirmez : ")
                    
                    if nouveau != confirmation:
                        print("Les mots de passe ne correspondent pas.")
                    else:
                        if f1.changer_mot_de_passe(ancien, nouveau):
                            break
        else:
            continuer = input("Voulez-vous réessayer ? (o/n) : ")
            if continuer.lower() != 'o':
                print("Au revoir.")
                exit()

    while True:
        print("\n" + "="*30)
        print("       MENU ADMINISTRATEUR")
        print("="*30)
        print("1- Ajouter une regle")
        print("2- Supprimer une regle")
        print("3- Afficher les regles")
        print("4- Inspecter le Paquet")
        print("5- Journalisation")
        print("6- Quitter")
        
        choix = input("\nVotre choix (1-6) : ")

        if choix == '1':
            print("\n--- Ajout d'une nouvelle regle ---")
            
            while True:
                action = input("Action (OBLIGATOIRE - AUTORISER/BLOQUER) : ").strip().upper()
                if action in ["AUTORISER", "BLOQUER"]:
                    break
                print("Erreur : Vous devez entrer AUTORISER ou BLOQUER.")

            # AJOUT VALIDATION IP ICI
            while True:
                ip_src = input("IP Source (OBLIGATOIRE) : ").strip()
                valide, msg = valider_format_ip(ip_src)
                if valide:
                    break
                print(f"Erreur IP : {msg}")

            proto = input("Protocole (TCP/UDP/etc, laisser vide si aucun) : ").strip() or None
            port_input = input("Port (laisser vide si aucun) : ").strip() or None
            plage = input("Plage reseau (ex: 10.0.0., laisser vide si aucun) : ").strip() or None
            
            f1.ajouter_regle(action, ip_src, proto, port_input, plage)

        elif choix == '2':
            print("\n--- Suppression d'une regle ---")
            f1.afficher_regles()
            if f1.regles:
                try:
                    index = int(input("Index de la regle a supprimer : "))
                    f1.supprimer_regle(index)
                except ValueError:
                    print("Nombre invalide.")

        elif choix == '3':
            f1.afficher_regles()

        elif choix == '4':
            print("\n--- Inspection d'un paquet ---")
            
            # AJOUT VALIDATION IP ICI
            while True:
                ip_test = input("IP Source : ").strip()
                valide, msg = valider_format_ip(ip_test)
                if valide:
                    break
                print(f"Erreur IP : {msg}")

            proto_test = input("Protocole (laisser vide si aucun) : ").strip() or None
            port_test = input("Port (laisser vide si aucun) : ").strip() or None
            
            if port_test:
                try:
                    port_test = int(port_test)
                except ValueError:
                    print("Info : Le port saisi n'est pas un nombre, il sera ignoré dans la recherche.")
                    port_test = None
            
            res = f1.inspecter_paquet(ip_test, proto_test, port_test)
            print(f"Resultat : {res}")

        elif choix == '5':
            f1.afficher_journal()

        elif choix == '6':
            print("Sauvegarde et fermeture...")
            f1.sauvegarder_donnees()
            f1.sauvegarder_config()
            print("Au revoir !")
            break

        else:
            print("Choix invalide.")