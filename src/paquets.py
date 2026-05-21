import random
from equipements import Firewall


class Paquet:
    def __init__(self, src, dest, protocol, size, port=None):
        self.src = src
        self.dest = dest
        self.protocol = protocol
        self.size = size
        self.port = port

    def __str__(self):
        port_str = f":{self.port}" if self.port else ""
        return f"Paquet [{self.protocol}{port_str}] | {self.src} -> {self.dest} ({self.size} octets)"


class SimulateurTransit:
    def __init__(self, topologie, moniteur=None):
        self.topologie = topologie
        self.moniteur = moniteur

    def envoyer_paquet(self, paquet):
        print(f"\n Envoi : {paquet}")

        chemin = self.topologie.trouver_chemin(paquet.src, paquet.dest)

        if not chemin:
            print(f" [ERREUR] Aucun chemin entre {paquet.src} et {paquet.dest}.")
            if self.moniteur:
                self.moniteur.update_stats(paquet.src, success=False)
                self.moniteur.log_packet(paquet, status="no_route")
            return False

        print(f" [ROUTAGE] Chemin : {' -> '.join(chemin)}")

        for i, nom_courant in enumerate(chemin):
            eq = self.topologie.get_equipement(nom_courant)

            if not eq or not eq.est_actif:
                print(f" [PANNE] {nom_courant} est hors ligne. Paquet perdu.")
                if self.moniteur:
                    self.moniteur.log_packet(paquet, status=f"dropped_at_{nom_courant}")
                    self.moniteur.update_stats(paquet.src, success=False)
                return False

            if isinstance(eq, Firewall):
                decision = eq.inspecter_paquet(paquet.src, paquet.protocol, paquet.port)
                if "REFUSER" in decision or "BLOQUER" in decision:
                    print(f" [FIREWALL] Paquet bloqué par {nom_courant}.")
                    if self.moniteur:
                        self.moniteur.log_packet(paquet, status=f"blocked_by_{nom_courant}")
                        self.moniteur.update_stats(paquet.src, success=False)
                    return False
                print(f" [FIREWALL] Autorisé par {nom_courant}.")

            if i < len(chemin) - 1:
                lien = self.topologie.get_lien_entre(nom_courant, chemin[i + 1])
                if lien:
                    lien.bandwidth = lien.debit
                    if self.moniteur:
                        charge = self.moniteur.calculate_link_usage(lien, paquet)
                        print(f" [LIEN] {nom_courant} <-> {chemin[i+1]} — charge : {charge}%")
                    lien.octets_transmis += paquet.size

        print(f" [OK] Paquet arrivé à {paquet.dest}.")
        if self.moniteur:
            self.moniteur.log_packet(paquet, status="transmitted")
            self.moniteur.update_stats(paquet.src, success=True)
        return True