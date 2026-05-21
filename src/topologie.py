from equipements import Equipement


class Lien:
    """Représente un câble entre deux équipements"""
    def __init__(self, equipement_a, equipement_b, debit, latence):
        self.equipement_a    = equipement_a
        self.equipement_b    = equipement_b
        self.debit           = debit
        self.latence         = latence
        self.octets_transmis = 0

    def __str__(self):
        return (f"Lien entre {self.equipement_a.nom} et {self.equipement_b.nom} "
                f"(Débit: {self.debit}Mbps, Latence: {self.latence}ms)")


class Topologie:
    """Gère la topologie du réseau, y compris les équipements et les liens."""

    def __init__(self):
        self.appareils = {}
        self.liens     = []

    def ajouter_equipement(self, equipement):
        if equipement.nom in self.appareils:
            print(f"Avertissement : L'équipement {equipement.nom} existe déjà et sera mis à jour.")
        self.appareils[equipement.nom] = equipement
        print(f"L'appareil {equipement.nom} a été ajouté.")

    def connecter(self, nom_a, nom_b, debit, latence):
        if nom_a not in self.appareils:
            print(f"Erreur : L'équipement {nom_a} n'existe pas.")
            return
        if nom_b not in self.appareils:
            print(f"Erreur : L'équipement {nom_b} n'existe pas.")
            return

        equipement_a = self.appareils[nom_a]
        equipement_b = self.appareils[nom_b]

        for lien in self.liens:
            if (lien.equipement_a == equipement_a and lien.equipement_b == equipement_b) or \
               (lien.equipement_a == equipement_b and lien.equipement_b == equipement_a):
                print(f"Avertissement : Un lien existe déjà entre {nom_a} et {nom_b}. Mise à jour.")
                lien.debit   = debit
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

    def get_equipement(self, nom):
        return self.appareils.get(nom)

    def get_lien_entre(self, nom_a, nom_b):
        eq_a = self.get_equipement(nom_a)
        eq_b = self.get_equipement(nom_b)
        if not eq_a or not eq_b:
            return None
        for lien in self.liens:
            if (lien.equipement_a == eq_a and lien.equipement_b == eq_b) or \
               (lien.equipement_a == eq_b and lien.equipement_b == eq_a):
                return lien
        return None

    def trouver_chemin(self, source_nom, dest_nom):
        """Chemin le plus court par latence — algorithme de Dijkstra."""
        if source_nom not in self.appareils or dest_nom not in self.appareils:
            return None

        distances     = {n: float('inf') for n in self.appareils}
        predecesseurs = {n: None for n in self.appareils}
        distances[source_nom] = 0
        non_visites = set(self.appareils.keys())

        while non_visites:
            u = min(non_visites, key=lambda n: distances[n])
            if distances[u] == float('inf'):
                break
            non_visites.remove(u)
            eq_u = self.appareils[u]

            for lien in self.liens:
                if lien.equipement_a == eq_u:
                    v = lien.equipement_b.nom
                elif lien.equipement_b == eq_u:
                    v = lien.equipement_a.nom
                else:
                    continue
                if v in non_visites:
                    alt = distances[u] + lien.latence
                    if alt < distances[v]:
                        distances[v]     = alt
                        predecesseurs[v] = u

        chemin, cur = [], dest_nom
        while cur is not None:
            chemin.insert(0, cur)
            cur = predecesseurs[cur]

        return chemin if chemin and chemin[0] == source_nom else None