"""
paquets.py
Définition des paquets réseau et simulation de leur transmission.
"""

import time
import random


class Paquet:
    """
    Représente un paquet réseau en transit.
    """

    PROTOCOLES_VALIDES = ['TCP', 'UDP', 'ICMP']

    def __init__(self, source: str, destination: str, protocole: str,
                 taille: int, priorite: int, port_dest: int = 80):
        """
        Args:
            source: Adresse IP source
            destination: Adresse IP destination
            protocole: 'TCP', 'UDP' ou 'ICMP'
            taille: Taille en octets
            priorite: Niveau 1 (basse) à 5 (haute)
            port_dest: Port de destination
        """
        if protocole not in self.PROTOCOLES_VALIDES:
            raise ValueError(f"Protocole invalide. Choisir parmi {self.PROTOCOLES_VALIDES}")
        if not (1 <= priorite <= 5):
            raise ValueError("La priorité doit être entre 1 et 5.")
        if taille <= 0:
            raise ValueError("La taille doit être positive.")

        self.source = source
        self.destination = destination
        self.protocole = protocole
        self.taille = taille          # octets
        self.priorite = priorite
        self.port_dest = port_dest

    def __str__(self):
        return (f"Paquet[{self.protocole}] {self.source} -> {self.destination} "
                f"| {self.taille}o | priorité={self.priorite} | port={self.port_dest}")


class Simulateur:
    """
    Moteur de simulation de trafic réseau.
    Gère l'envoi de paquets à travers la topologie.
    """

    def __init__(self, topologie):
        """
        Args:
            topologie: Objet Topologie contenant les équipements et liens
        """
        self._topologie = topologie
        # Statistiques globales
        self._paquets_envoyes = 0
        self._paquets_perdus = 0
        self._debit_cumule = 0       # en octets
        self._temps_transit_total = 0.0  # en ms
        self._historique = []        # 10 derniers paquets

    def envoyer_paquet(self, paquet: Paquet):
        """
        Envoie un paquet de sa source à sa destination.
        Simule le trajet saut par saut.
        """
        print(f"\n{'─'*55}")
        print(f"  ENVOI : {paquet}")
        print(f"{'─'*55}")

        # Trouver les équipements source et destination par IP
        source_eq = self._trouver_par_ip(paquet.source)
        dest_eq = self._trouver_par_ip(paquet.destination)

        if source_eq is None:
            print(f"  [ERREUR] Aucun équipement avec l'IP source {paquet.source}")
            self._paquets_perdus += 1
            self._enregistrer_historique(paquet, None, "PERDU - source inconnue")
            return

        if dest_eq is None:
            print(f"  [ERREUR] Aucun équipement avec l'IP dest {paquet.destination}")
            self._paquets_perdus += 1
            self._enregistrer_historique(paquet, None, "PERDU - dest inconnue")
            return

        # Vérifier que source et dest sont actifs
        if not source_eq.actif:
            print(f"  [ERREUR] Source '{source_eq.nom}' est inactive.")
            self._paquets_perdus += 1
            return

        if not dest_eq.actif:
            print(f"  [ERREUR] Destination '{dest_eq.nom}' est inactive.")
            self._paquets_perdus += 1
            return

        # Chercher le chemin
        chemin = self._topologie.trouver_chemin(source_eq.nom, dest_eq.nom)

        if chemin is None:
            print(f"  [!] Destination INATTEIGNABLE : aucun chemin trouvé.")
            self._paquets_perdus += 1
            self._enregistrer_historique(paquet, None, "PERDU - inatteignable")
            return

        # Vérifier le firewall sur le chemin
        for nom_eq in chemin:
            eq = self._topologie.get_equipement(nom_eq)
            from equipements import Firewall
            if isinstance(eq, Firewall):
                autorise = eq.inspecter_paquet(paquet)
                if not autorise:
                    print(f"  [FIREWALL] Paquet BLOQUÉ par '{eq.nom}'.")
                    self._paquets_perdus += 1
                    self._enregistrer_historique(paquet, chemin, "BLOQUÉ par firewall")
                    return

        # Simuler le transit saut par saut
        temps_total = 0.0
        print(f"\n  Chemin : {' --> '.join(chemin)}")
        print(f"\n  Transit saut par saut :")

        for i in range(len(chemin) - 1):
            nom_actuel = chemin[i]
            nom_suivant = chemin[i + 1]
            lien = self._topologie.get_lien_entre(nom_actuel, nom_suivant)

            if lien:
                # Temps de transit = latence + taille / bande_passante (converti en ms)
                temps_transit = lien.latence + (paquet.taille * 8) / (lien.bande_passante * 1000)
                temps_total += temps_transit
                lien.octets_transmis += paquet.taille

                # Mise à jour des stats de l'équipement (si moniteur disponible)
                print(f"    [{nom_actuel}] --> [{nom_suivant}]  "
                      f"latence={lien.latence}ms  débit={lien.bande_passante}Mbps  "
                      f"temps={temps_transit:.2f}ms")

        # Mise à jour des statistiques globales
        self._paquets_envoyes += 1
        self._debit_cumule += paquet.taille
        self._temps_transit_total += temps_total

        print(f"\n  ✓ Paquet LIVRÉ en {temps_total:.2f} ms")
        self._enregistrer_historique(paquet, chemin, f"LIVRÉ en {temps_total:.2f}ms")

    def _trouver_par_ip(self, ip: str):
        """Cherche un équipement par son adresse IP."""
        for eq in self._topologie.get_equipements().values():
            if eq.adresse_ip == ip:
                return eq
        return None

    def _enregistrer_historique(self, paquet, chemin, resultat: str):
        """Enregistre un paquet dans l'historique (10 max)."""
        entree = {
            'paquet': str(paquet),
            'chemin': chemin,
            'resultat': resultat
        }
        self._historique.append(entree)
        if len(self._historique) > 10:
            self._historique.pop(0)

    def afficher_statistiques(self):
        """Affiche les statistiques globales de simulation."""
        print(f"\n{'='*50}")
        print(f"  STATISTIQUES DE SIMULATION")
        print(f"{'='*50}")
        print(f"  Paquets envoyés  : {self._paquets_envoyes}")
        print(f"  Paquets perdus   : {self._paquets_perdus}")
        taux_perte = 0 if self._paquets_envoyes == 0 else \
            (self._paquets_perdus / (self._paquets_envoyes + self._paquets_perdus)) * 100
        print(f"  Taux de perte    : {taux_perte:.1f}%")
        print(f"  Débit cumulé     : {self._debit_cumule / 1024:.2f} Ko")
        moy_transit = 0 if self._paquets_envoyes == 0 else \
            self._temps_transit_total / self._paquets_envoyes
        print(f"  Temps moy transit: {moy_transit:.2f} ms")
        print(f"\n  10 derniers paquets :")
        for entree in self._historique:
            print(f"    [{entree['resultat']}] {entree['paquet']}")
        print(f"{'='*50}\n")

    def get_stats(self) -> dict:
        return {
            'paquets_envoyes': self._paquets_envoyes,
            'paquets_perdus': self._paquets_perdus,
            'debit_cumule': self._debit_cumule,
            'temps_transit_total': self._temps_transit_total,
            'historique': self._historique
        }