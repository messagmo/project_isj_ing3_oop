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
        self.regles = [] # Sera rempli par le responsable Module 3
        self.password = "admin123" # Protection simple

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