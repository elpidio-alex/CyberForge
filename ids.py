"""
════════════════════════════════════════════════════════════════
 ids.py — Module de détection d'intrusions (IDS)
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Analyse les paquets et flux d'une capture pour détecter des
   comportements suspects selon des règles heuristiques basées
   sur des seuils configurables (config.json). Génère une liste
   d'alertes classées par criticité (FAIBLE, MOYENNE, HAUTE).

 Règles implémentées :
   1. Flood / DoS      — trop de paquets envoyés par une même IP
   2. Scan de ports     — une IP source touche trop de ports
                          différents sur une même IP destination
   3. Paquets volumineux — taille de paquet anormalement grande
   4. Protocoles suspects — ICMP, ARP, DNS en volume important
   5. Ports sensibles    — trafic vers des services critiques
                          (SSH, RDP, MySQL, etc.)
════════════════════════════════════════════════════════════════
"""

import json                          # Lecture de la configuration
from datetime import datetime        # Timestamp des alertes
from collections import defaultdict  # Agrégation par IP


# Chargement de la configuration (seuils IDS)
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Extraction des seuils et listes depuis config.json
SEUIL_PAQUETS_PAR_IP   = CONFIG["ids"]["seuil_paquets_par_ip"]
SEUIL_PORTS_SCANNES    = CONFIG["ids"]["seuil_ports_scannes"]
SEUIL_TAILLE_PAQUET    = CONFIG["ids"]["seuil_taille_paquet"]
PROTOCOLES_SUSPECTS    = set(CONFIG["ids"]["protocoles_suspects"])
PORTS_SENSIBLES        = set(CONFIG["ids"]["ports_sensibles"])

# Niveaux de criticité utilisés dans les alertes
CRITICITE_FAIBLE  = "FAIBLE"
CRITICITE_MOYENNE = "MOYENNE"
CRITICITE_HAUTE   = "HAUTE"

# Types d'alertes générées
TYPE_FLOOD             = "FLOOD_DOS"
TYPE_SCAN_PORTS        = "SCAN_PORTS"
TYPE_PAQUET_VOLUMINEUX = "PAQUET_VOLUMINEUX"
TYPE_PROTOCOLE_SUSPECT = "PROTOCOLE_SUSPECT"
TYPE_PORT_SENSIBLE     = "ACCES_PORT_SENSIBLE"


# ════════════════════════════════════════════════════════════════
# SECTION 1 — POINT D'ENTRÉE PRINCIPAL
# ════════════════════════════════════════════════════════════════

def analyser_capture(paquets):
    """
    Analyse une liste complète de paquets et retourne toutes les
    alertes détectées, toutes règles confondues.

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés (voir parser.py)
                               Chaque paquet doit contenir : ip_src,
                               ip_dst, protocole, port_src, port_dst,
                               taille, timestamp

    Retourne :
        list[dict] : Liste d'alertes avec les clés :
                     type_alerte, criticite, ip_src, ip_dst,
                     description, timestamp
    """
    alertes = []  # Liste finale qui contiendra toutes les alertes

    # Exécuter chaque règle de détection successivement
    # et fusionner les résultats dans la liste finale
    alertes += detecter_flood(paquets)
    alertes += detecter_scan_ports(paquets)
    alertes += detecter_paquets_volumineux(paquets)
    alertes += detecter_protocoles_suspects(paquets)
    alertes += detecter_ports_sensibles(paquets)

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 2 — RÈGLE 1 : FLOOD / DOS
# ════════════════════════════════════════════════════════════════

def detecter_flood(paquets):
    """
    Détecte les IPs sources ayant envoyé un nombre de paquets
    supérieur au seuil défini (SEUIL_PAQUETS_PAR_IP). Ce
    comportement est caractéristique d'une attaque par déni
    de service (DoS) ou d'un flood volontaire.

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste d'alertes de type FLOOD_DOS
    """
    # Compter le nombre de paquets envoyés par chaque IP source
    compteur_par_ip = defaultdict(int)

    for paquet in paquets:
        ip_src = paquet.get("ip_src")
        if ip_src:
            compteur_par_ip[ip_src] += 1

    alertes = []  # Liste des alertes détectées pour cette règle

    # Vérifier chaque IP par rapport au seuil configuré
    for ip_src, nb_paquets in compteur_par_ip.items():
        if nb_paquets > SEUIL_PAQUETS_PAR_IP:
            # Déterminer la criticité selon l'ampleur du dépassement
            # Plus le dépassement est important, plus la criticité augmente
            if nb_paquets > SEUIL_PAQUETS_PAR_IP * 3:
                criticite = CRITICITE_HAUTE
            elif nb_paquets > SEUIL_PAQUETS_PAR_IP * 1.5:
                criticite = CRITICITE_MOYENNE
            else:
                criticite = CRITICITE_FAIBLE

            alertes.append({
                "type_alerte" : TYPE_FLOOD,
                "criticite"   : criticite,
                "ip_src"      : ip_src,
                "ip_dst"      : None,  # Pas de destination unique (flood global)
                "description" : (
                    f"Volume anormal détecté : {nb_paquets} paquets envoyés "
                    f"par {ip_src} (seuil : {SEUIL_PAQUETS_PAR_IP}). "
                    f"Possible attaque DoS ou flood."
                ),
                "timestamp"   : datetime.now().isoformat()
            })

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 3 — RÈGLE 2 : SCAN DE PORTS
# ════════════════════════════════════════════════════════════════

def detecter_scan_ports(paquets):
    """
    Détecte les scans de ports : une IP source qui contacte un
    nombre de ports différents supérieur au seuil, sur une même
    IP destination. Comportement typique d'un scan Nmap ou
    d'une reconnaissance réseau malveillante.

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste d'alertes de type SCAN_PORTS
    """
    # Structure : { (ip_src, ip_dst) : set(ports_destination) }
    ports_par_couple = defaultdict(set)

    for paquet in paquets:
        ip_src   = paquet.get("ip_src")
        ip_dst   = paquet.get("ip_dst")
        port_dst = paquet.get("port_dst")

        # On ne peut détecter un scan que si les deux IPs et le port sont connus
        if ip_src and ip_dst and port_dst is not None:
            ports_par_couple[(ip_src, ip_dst)].add(port_dst)

    alertes = []  # Liste des alertes détectées pour cette règle

    # Vérifier chaque couple (source, destination) par rapport au seuil
    for (ip_src, ip_dst), ports in ports_par_couple.items():
        nb_ports_distincts = len(ports)

        if nb_ports_distincts > SEUIL_PORTS_SCANNES:
            # Criticité HAUTE si le nombre de ports scannés est très élevé
            if nb_ports_distincts > SEUIL_PORTS_SCANNES * 2:
                criticite = CRITICITE_HAUTE
            else:
                criticite = CRITICITE_MOYENNE

            alertes.append({
                "type_alerte" : TYPE_SCAN_PORTS,
                "criticite"   : criticite,
                "ip_src"      : ip_src,
                "ip_dst"      : ip_dst,
                "description" : (
                    f"Scan de ports détecté : {ip_src} a contacté "
                    f"{nb_ports_distincts} ports différents sur {ip_dst} "
                    f"(seuil : {SEUIL_PORTS_SCANNES}). Possible reconnaissance réseau."
                ),
                "timestamp"   : datetime.now().isoformat()
            })

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 4 — RÈGLE 3 : PAQUETS VOLUMINEUX
# ════════════════════════════════════════════════════════════════

def detecter_paquets_volumineux(paquets):
    """
    Détecte les paquets dont la taille dépasse le seuil configuré.
    Des paquets anormalement volumineux peuvent indiquer une
    exfiltration de données ou une anomalie réseau (fragmentation
    suspecte, jumbo frames non attendues, etc.).

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste d'alertes de type PAQUET_VOLUMINEUX
                     (une alerte par paquet suspect)
    """
    alertes = []  # Liste des alertes détectées pour cette règle

    for paquet in paquets:
        taille = paquet.get("taille") or 0

        # Vérifier si la taille dépasse le seuil configuré
        if taille > SEUIL_TAILLE_PAQUET:
            alertes.append({
                "type_alerte" : TYPE_PAQUET_VOLUMINEUX,
                "criticite"   : CRITICITE_FAIBLE,  # Rarement critique seul
                "ip_src"      : paquet.get("ip_src"),
                "ip_dst"      : paquet.get("ip_dst"),
                "description" : (
                    f"Paquet volumineux détecté : {taille} octets "
                    f"(seuil : {SEUIL_TAILLE_PAQUET}) entre "
                    f"{paquet.get('ip_src')} et {paquet.get('ip_dst')}."
                ),
                "timestamp"   : datetime.now().isoformat()
            })

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 5 — RÈGLE 4 : PROTOCOLES SUSPECTS
# ════════════════════════════════════════════════════════════════

def detecter_protocoles_suspects(paquets):
    """
    Détecte un volume important de trafic sur des protocoles
    jugés sensibles (ICMP, ARP, DNS selon config.json). Un volume
    élevé sur ces protocoles peut indiquer :
      - ICMP : ping flood, reconnaissance réseau
      - ARP  : ARP spoofing / poisoning
      - DNS  : DNS tunneling, exfiltration de données

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste d'alertes de type PROTOCOLE_SUSPECT
                     (une alerte agrégée par protocole suspect détecté)
    """
    # Compter les paquets par protocole suspect et par IP source
    compteur = defaultdict(lambda: defaultdict(int))

    for paquet in paquets:
        protocole = paquet.get("protocole")
        ip_src    = paquet.get("ip_src")

        # Ne traiter que les protocoles définis comme suspects dans la config
        if protocole in PROTOCOLES_SUSPECTS and ip_src:
            compteur[protocole][ip_src] += 1

    alertes = []  # Liste des alertes détectées pour cette règle

    # Seuil interne : au-delà de 50 paquets sur un protocole suspect
    # depuis une même IP, on considère que c'est notable
    SEUIL_PROTOCOLE_SUSPECT = 50

    for protocole, compteur_par_ip in compteur.items():
        for ip_src, nb_paquets in compteur_par_ip.items():
            if nb_paquets > SEUIL_PROTOCOLE_SUSPECT:
                alertes.append({
                    "type_alerte" : TYPE_PROTOCOLE_SUSPECT,
                    "criticite"   : CRITICITE_MOYENNE,
                    "ip_src"      : ip_src,
                    "ip_dst"      : None,
                    "description" : (
                        f"Volume élevé de trafic {protocole} détecté depuis "
                        f"{ip_src} : {nb_paquets} paquets. "
                        f"Protocole considéré comme sensible pour la supervision."
                    ),
                    "timestamp"   : datetime.now().isoformat()
                })

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 6 — RÈGLE 5 : ACCÈS À DES PORTS SENSIBLES
# ════════════════════════════════════════════════════════════════

def detecter_ports_sensibles(paquets):
    """
    Détecte les tentatives de connexion vers des ports considérés
    comme sensibles (SSH, Telnet, HTTP/S, MySQL, RDP...). Une
    IP externe qui multiplie les connexions vers ces ports peut
    indiquer une tentative d'intrusion ciblée.

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste d'alertes de type ACCES_PORT_SENSIBLE
                     (une alerte par couple IP source / port sensible)
    """
    # Structure : { (ip_src, ip_dst, port_dst) : nb_tentatives }
    tentatives = defaultdict(int)

    for paquet in paquets:
        ip_src   = paquet.get("ip_src")
        ip_dst   = paquet.get("ip_dst")
        port_dst = paquet.get("port_dst")

        # Ne traiter que les paquets ciblant un port sensible connu
        if ip_src and ip_dst and port_dst in PORTS_SENSIBLES:
            tentatives[(ip_src, ip_dst, port_dst)] += 1

    alertes = []  # Liste des alertes détectées pour cette règle

    # Seuil interne : plus de 10 tentatives vers un port sensible
    # depuis la même IP source est jugé suspect (ex: brute-force SSH)
    SEUIL_TENTATIVES_PORT_SENSIBLE = 10

    for (ip_src, ip_dst, port_dst), nb_tentatives in tentatives.items():
        if nb_tentatives > SEUIL_TENTATIVES_PORT_SENSIBLE:
            alertes.append({
                "type_alerte" : TYPE_PORT_SENSIBLE,
                "criticite"   : CRITICITE_HAUTE,
                "ip_src"      : ip_src,
                "ip_dst"      : ip_dst,
                "description" : (
                    f"Accès répété au port sensible {port_dst} détecté : "
                    f"{nb_tentatives} tentatives depuis {ip_src} vers {ip_dst}. "
                    f"Possible tentative de brute-force ou d'intrusion."
                ),
                "timestamp"   : datetime.now().isoformat()
            })

    return alertes


# ════════════════════════════════════════════════════════════════
# SECTION 7 — PRÉPARATION POUR LA BASE DE DONNÉES
# ════════════════════════════════════════════════════════════════

def preparer_alertes_bd(alertes, capture_id):
    """
    Convertit la liste d'alertes en tuples prêts pour l'insertion
    batch dans SQLite via db.inserer_alertes().

    Paramètres :
        alertes    (list[dict]) : Liste d'alertes générées par analyser_capture()
        capture_id (int)        : ID de la capture parente

    Retourne :
        list[tuple] : Liste de tuples dans l'ordre des colonnes
                      de la table alertes
    """
    tuples = []

    for a in alertes:
        tuples.append((
            capture_id,           # capture_id — clé étrangère
            a["type_alerte"],     # type_alerte
            a["criticite"],       # criticite
            a["ip_src"],          # ip_src
            a["ip_dst"],          # ip_dst
            a["description"],     # description
            a["timestamp"]        # timestamp
        ))

    return tuples