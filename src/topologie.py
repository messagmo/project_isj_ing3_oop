from equipement import Equipement

class Lien:
    """Représente un câble entre deux équipements"""
    def __init__(self, equipement_a: Equipement, equipement_b: Equipement, debit: int, latence: int):
        self.equipement_a = equipement_a
        self.equipement_b = equipement_b
        self.debit = debit      # en Mbps
        self.latence = latence  # en ms
        self.octets_transmis = 0 # Pour le monitoring

    def __str__(self):
        return f"Lien entre {self.equipement_a.nom} et {self.equipement_b.nom} (Débit: {self.debit}Mbps, Latence: {self.latence}ms)"


class Topologie:
    """Gère la topologie du réseau, y compris les équipements et les liens."""
    def __init__(self):
        self.appareils = {} # Dictionnaire { "Nom": Objet_Equipement }
        self.liens = []     # Liste des objets Lien

    def ajouter_equipement(self, equipement: Equipement):
        if equipement.nom in self.appareils:
            print(f"Avertissement : L'équipement {equipement.nom} existe déjà et sera mis à jour.")
        self.appareils[equipement.nom] = equipement
        print(f"L'appareil {equipement.nom} a été ajouté.")

    def connecter(self, nom_a: str, nom_b: str, debit: int, latence: int):
        if nom_a not in self.appareils:
            print(f"Erreur : L'équipement {nom_a} n'existe pas.")
            return
        if nom_b not in self.appareils:
            print(f"Erreur : L'équipement {nom_b} n'existe pas.")
            return

        equipement_a = self.appareils[nom_a]
        equipement_b = self.appareils[nom_b]

        # Vérifier si un lien existe déjà entre ces deux équipements
        for lien in self.liens:
            if (lien.equipement_a == equipement_a and lien.equipement_b == equipement_b) or \
               (lien.equipement_a == equipement_b and lien.equipement_b == equipement_a):
                print(f"Avertissement : Un lien existe déjà entre {nom_a} et {nom_b}. Mise à jour du lien existant.")
                lien.debit = debit
                lien.latence = latence
                return

        nouveau_lien = Lien(equipement_a, equipement_b, debit, latence)
        self.liens.append(nouveau_lien)
        print(f"Lien créé entre {nom_a} et {nom_b}.")

    def afficher_reseau(self):
        print("\n--- ÉTAT ACTUEL DU RÉSEAU ---")
        print("Équipements:")
        for eq in self.appareils.values():
            print(f"  - {eq}")
        print("Liens:")
        for lien in self.liens:
            print(f"  - {lien}")

    def get_equipement(self, nom: str) -> Equipement | None:
        """Retourne un équipement par son nom."""
        return self.appareils.get(nom)

    def get_lien_entre(self, nom_a: str, nom_b: str) -> Lien | None:
        """Retourne le lien entre deux équipements par leurs noms."""
        eq_a = self.get_equipement(nom_a)
        eq_b = self.get_equipement(nom_b)

        if not eq_a or not eq_b:
            return None

        for lien in self.liens:
            if (lien.equipement_a == eq_a and lien.equipement_b == eq_b) or \
               (lien.equipement_a == eq_b and lien.equipement_b == eq_a):
                return lien
        return None

    def trouver_chemin(self, source_nom: str, dest_nom: str) -> list[str] | None:
        """Trouve le chemin le plus court entre deux équipements en utilisant l'algorithme de Dijkstra.
        Le coût est basé uniquement sur la latence des liens.
        """
        source_eq = self.get_equipement(source_nom)
        dest_eq = self.get_equipement(dest_nom)

        if not source_eq or not dest_eq:
            return None

        # Implémentation de Dijkstra
        distances = {eq_name: float('infinity') for eq_name in self.appareils}
        predecesseurs = {eq_name: None for eq_name in self.appareils}
        distances[source_nom] = 0
        noeuds_non_visites = set(self.appareils.keys())

        while noeuds_non_visites:
            # Trouver le nœud non visité avec la plus petite distance
            min_distance_node = None
            for node in noeuds_non_visites:
                if min_distance_node is None:
                    min_distance_node = node
                elif distances[node] < distances[min_distance_node]:
                    min_distance_node = node

            if min_distance_node is None or distances[min_distance_node] == float('infinity'):
                break # Plus de nœuds atteignables

            noeuds_non_visites.remove(min_distance_node)
            current_equipement = self.get_equipement(min_distance_node)

            # Mettre à jour les distances des voisins
            for lien in self.liens:
                voisin_nom = None
                if lien.equipement_a == current_equipement:
                    voisin_nom = lien.equipement_b.nom
                elif lien.equipement_b == current_equipement:
                    voisin_nom = lien.equipement_a.nom

                if voisin_nom and voisin_nom in noeuds_non_visites:
                    # Note : Dans une simulation réelle, on pourrait vérifier ici si le nœud voisin est actif
                    # Mais l'algorithme Dijkstra standard calcule le chemin théorique.
                    # Le simulateur vérifiera l'activité lors du transit saut par saut.
                    cout = lien.latence # Coût basé uniquement sur la latence
                    if distances[min_distance_node] + cout < distances[voisin_nom]:
                        distances[voisin_nom] = distances[min_distance_node] + cout
                        predecesseurs[voisin_nom] = min_distance_node

        # Reconstruire le chemin
        chemin = []
        current = dest_nom
        while current is not None:
            chemin.insert(0, current)
            current = predecesseurs[current]

        if chemin and chemin[0] == source_nom:
            return chemin
        else:
            return None # Pas de chemin trouvé


