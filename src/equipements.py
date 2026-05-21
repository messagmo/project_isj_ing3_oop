class Equipement:
    """Classe de base pour tous les appareils du réseau"""
    def __init__(self, nom, ip, marque):
        self.nom = nom
        self.ip = ip
        self.marque = marque
        self.est_actif = True  # Par défaut, l'équipement fonctionne

    def __str__(self):
        etat = "Actif" if self.est_actif else "Inactif"
        return f"[{self.nom}] IP: {self.ip} | Marque: {self.marque} | Etat: {etat}"

# --- Sous-classes spécifiques ---

class Routeur(Equipement):
    def __init__(self, nom, ip, marque):
        super().__init__(nom, ip, marque)
        self.table_deroutage = {} # Sera rempli par le responsable Module 2

class Switch(Equipement):
    def __init__(self, nom, ip, marque):
        super().__init__(nom, ip, marque)
        self.vlans = [] # Liste des VLANs gérés

class Firewall(Equipement):
    def __init__(self, nom, ip, marque):
        super().__init__(nom, ip, marque)
        self.regles = []
        self.password = "admin123"
        self._authentifie = False        

    def authentifier(self, mot_de_passe):  
        if mot_de_passe == self.password:
            self._authentifie = True
            print("Authentification reussie.")
            return True
        self._authentifie = False
        print("Mot de passe incorrect.")
        return False

    def ajouter_regle(self, action, ip_source, protocole=None, port=None, plage_reseau=None):
        if not self._authentifie:
            print("Acces refuse.")
            return
        if port:
            try:
                port = int(port)
            except ValueError:
                print("Port invalide.")
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

    def afficher_regles(self):
        print("\n--- REGLES DU FIREWALL ---")
        if not self.regles:
            print("Aucune regle configuree.")
            return
        for i, r in enumerate(self.regles):
            print(f"[{i}] {r}")

    def supprimer_regle(self, index):
        if not self._authentifie:
            print("Acces refuse.")
            return
        if 0 <= index < len(self.regles):
            sup = self.regles.pop(index)
            print(f"Regle supprimee : {sup}")
        else:
            print("Index invalide.")

    def inspecter_paquet(self, ip_source, protocole, port):
        if port:
            try:
                port = int(port)
            except ValueError:
                port = None
        for regle in self.regles:
            ok = True
            if regle["ip_source"] and regle["ip_source"] != ip_source:
                ok = False
            if regle["protocole"]:
                if not protocole or regle["protocole"] != protocole.upper():
                    ok = False
            if regle["port"] and regle["port"] != port:
                ok = False
            if regle["plage_reseau"] and not ip_source.startswith(regle["plage_reseau"]):
                ok = False
            if ok:
                return regle["action"]
        return "REFUSER (Defaut)"

    def afficher_journal(self):
        print("(Journal non disponible dans cette version)")



class Serveur(Equipement):
    def __init__(self, nom, ip, marque):
        super().__init__(nom, ip, marque)
        self.services = ["HTTP", "FTP"]

# --- Gestion des connexions ---

class Lien:
    """Représente un câble entre deux équipements"""
    def __init__(self, equipement_a, equipement_b, debit, latence):
        self.equipement_a = equipement_a
        self.equipement_b = equipement_b
        self.debit = debit      # en Mbps
        self.latence = latence  # en ms

# --- La Topologie (Le Réseau complet) ---

class Topologie:
    def __init__(self):
        self.appareils = {} # Dictionnaire { "Nom": Objet_Equipement }
        self.liens = []     # Liste des objets Lien

    def ajouter_equipement(self, equipement):
        self.appareils[equipement.nom] = equipement
        print(f"L'appareil {equipement.nom} a été ajouté.")

    def connecter(self, nom_a, nom_b, debit, latence):
        if nom_a in self.appareils and nom_b in self.appareils:
            nouveau_lien = Lien(self.appareils[nom_a], self.appareils[nom_b], debit, latence)
            self.liens.append(nouveau_lien)
            print(f"Lien créé entre {nom_a} et {nom_b}.")
        else:
            print("Erreur : L'un des équipements n'existe pas.")

    def afficher_reseau(self):
        print("\n--- ÉTAT ACTUEL DU RÉSEAU ---")
        for eq in self.appareils.values():
            print(eq)


if __name__ == "__main__":
    mon_reseau = Topologie()

    # Création d'appareils
    r1 = Routeur("R1_Principal", "192.168.1.1", "Cisco")
    s1 = Serveur("Serveur_Web", "192.168.1.10", "Dell")
    f1 = Firewall("Firewall_Sortie", "10.0.0.1", "Fortinet")

    # Ajout au réseau
    mon_reseau.ajouter_equipement(r1)
    mon_reseau.ajouter_equipement(s1)
    mon_reseau.ajouter_equipement(f1)

    # Création des liens
    mon_reseau.connecter("R1_Principal", "Serveur_Web", 1000, 2)
    mon_reseau.connecter("R1_Principal", "Firewall_Sortie", 100, 10)

    # Affichage
    mon_reseau.afficher_reseau()