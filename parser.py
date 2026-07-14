"""
════════════════════════════════════════════════════════════════
 parser.py — Module de parsing des exports Wireshark (.txt)
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Lit et parse les fichiers .txt exportés depuis Wireshark
   (format "Packet List" texte brut). Extrait pour chaque
   paquet : numéro, timestamp, IP source, IP destination,
   protocole, ports, taille et info. Calcule ensuite les flux
   (conversations entre deux IPs) et prépare les données pour
   insertion en base SQLite via db.py.

 Format Wireshark attendu (colonnes séparées par des espaces) :
   No.  Time       Source        Destination   Protocol  Length  Info
   1    0.000000   192.168.1.1   8.8.8.8       DNS       74      Standard query
════════════════════════════════════════════════════════════════
"""

import re                  # Expressions régulières pour extraire les IPs et ports
import json                # Lecture de la configuration
from collections import defaultdict  # Pour agréger les flux facilement


# Chargement de la configuration (encodage, max paquets)
with open("config.json", "r") as f:
    CONFIG = json.load(f)

# Paramètres de parsing issus de la config
ENCODAGE   = CONFIG["parser"]["encodage"]
MAX_PAQUETS = CONFIG["parser"]["max_paquets"]


# ════════════════════════════════════════════════════════════════
# SECTION 1 — PARSING DU FICHIER
# ════════════════════════════════════════════════════════════════

def parser_fichier(chemin_fichier, callback_progression=None):
    """
    Parse un fichier .txt exporté depuis Wireshark et retourne
    la liste des paquets extraits.

    Paramètres :
        chemin_fichier       (str)      : Chemin absolu vers le fichier .txt
        callback_progression (callable) : Fonction appelée à chaque paquet
                                          parsé, reçoit (index, total) pour
                                          mettre à jour une barre de progression

    Retourne :
        list[dict] : Liste de dictionnaires représentant chaque paquet
                     avec les clés : numero, timestamp, ip_src, ip_dst,
                     protocole, port_src, port_dst, taille, info
    """
    paquets = []  # Liste qui contiendra tous les paquets parsés

    try:
        # Ouvrir le fichier avec l'encodage défini dans config.json
        with open(chemin_fichier, "r", encoding=ENCODAGE, errors="replace") as f:
            lignes = f.readlines()

    except FileNotFoundError:
        # Le fichier n'existe pas ou le chemin est incorrect
        raise FileNotFoundError(f"Fichier introuvable : {chemin_fichier}")

    except Exception as e:
        # Toute autre erreur de lecture
        raise IOError(f"Erreur lors de la lecture du fichier : {e}")

    # Filtrer les lignes vides et les lignes d'en-tête Wireshark
    lignes_valides = [l for l in lignes if _est_ligne_paquet(l)]

    # Limiter au maximum défini dans config.json
    lignes_valides = lignes_valides[:MAX_PAQUETS]

    total = len(lignes_valides)  # Nombre total de paquets à parser

    for index, ligne in enumerate(lignes_valides):
        # Parser chaque ligne individuellement
        paquet = _parser_ligne(ligne)

        if paquet:
            paquets.append(paquet)

        # Appeler le callback de progression si fourni
        if callback_progression:
            callback_progression(index + 1, total)

    return paquets


def _est_ligne_paquet(ligne):
    """
    Détermine si une ligne correspond à un paquet Wireshark valide.
    Ignore les en-têtes, lignes vides et séparateurs.

    Paramètres :
        ligne (str) : Ligne brute du fichier

    Retourne :
        bool : True si la ligne est un paquet valide, False sinon
    """
    ligne = ligne.strip()

    # Ignorer les lignes vides
    if not ligne:
        return False

    # Ignorer les lignes d'en-tête (commencent par "No." ou "-")
    if ligne.startswith("No.") or ligne.startswith("-"):
        return False

    # Une ligne de paquet valide commence par un numéro
    return ligne[0].isdigit()


def _parser_ligne(ligne):
    """
    Extrait les champs d'une ligne de paquet Wireshark.

    Paramètres :
        ligne (str) : Ligne brute représentant un paquet

    Retourne :
        dict : Dictionnaire avec les champs du paquet,
               ou None si la ligne ne peut pas être parsée
    """
    try:
        # Diviser la ligne en colonnes (max 7 parties)
        # Format : No. | Time | Source | Destination | Protocol | Length | Info
        parties = ligne.strip().split(None, 6)

        # Une ligne valide doit avoir au moins 6 colonnes
        if len(parties) < 6:
            return None

        # Extraction des colonnes principales
        numero    = int(parties[0])           # Numéro du paquet
        timestamp = parties[1]                # Temps relatif (secondes)
        source    = parties[2]                # IP ou nom source
        dest      = parties[3]               # IP ou nom destination
        protocole = parties[4].upper()        # Protocole (DNS, TCP, UDP...)
        taille    = _extraire_entier(parties[5])  # Taille en octets
        info      = parties[6] if len(parties) > 6 else ""  # Info descriptive

        # Extraire les IPs et ports depuis les champs source/destination
        ip_src, port_src = _extraire_ip_port(source)
        ip_dst, port_dst = _extraire_ip_port(dest)

        # Construire le dictionnaire du paquet
        return {
            "numero"    : numero,
            "timestamp" : timestamp,
            "ip_src"    : ip_src,
            "ip_dst"    : ip_dst,
            "protocole" : protocole,
            "port_src"  : port_src,
            "port_dst"  : port_dst,
            "taille"    : taille,
            "info"      : info.strip()
        }

    except Exception:
        # Si une ligne ne peut pas être parsée, on l'ignore silencieusement
        return None


def _extraire_ip_port(adresse):
    """
    Extrait l'IP et le port depuis une adresse de type "192.168.1.1:443"
    ou "192.168.1.1" ou un nom d'hôte.

    Paramètres :
        adresse (str) : Adresse brute extraite du fichier

    Retourne :
        tuple(str, int|None) : (ip, port) — port est None si absent
    """
    # Cas IPv6 avec port : [::1]:443
    match_ipv6 = re.match(r'\[(.+)\]:(\d+)', adresse)
    if match_ipv6:
        return match_ipv6.group(1), int(match_ipv6.group(2))

    # Cas IPv4 avec port : 192.168.1.1:443
    match_ipv4_port = re.match(r'(\d+\.\d+\.\d+\.\d+):(\d+)', adresse)
    if match_ipv4_port:
        return match_ipv4_port.group(1), int(match_ipv4_port.group(2))

    # Cas IPv4 sans port : 192.168.1.1
    match_ipv4 = re.match(r'(\d+\.\d+\.\d+\.\d+)', adresse)
    if match_ipv4:
        return match_ipv4.group(1), None

    # Cas nom d'hôte ou adresse non reconnue — retourner tel quel
    return adresse, None


def _extraire_entier(valeur):
    """
    Convertit une chaîne en entier de manière sécurisée.

    Paramètres :
        valeur (str) : Chaîne à convertir

    Retourne :
        int : Valeur entière, ou 0 si la conversion échoue
    """
    try:
        return int(valeur)
    except (ValueError, TypeError):
        return 0


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CALCUL DES FLUX
# ════════════════════════════════════════════════════════════════

def calculer_flux(paquets):
    """
    Agrège les paquets en flux (conversations entre deux IPs).
    Un flux est identifié par : (ip_src, ip_dst, protocole).

    Paramètres :
        paquets (list[dict]) : Liste de paquets parsés

    Retourne :
        list[dict] : Liste de flux avec les clés :
                     ip_src, ip_dst, protocole, nb_paquets, taille_totale
    """
    # Dictionnaire pour agréger les flux par clé (src, dst, protocole)
    agregation = defaultdict(lambda: {"nb_paquets": 0, "taille_totale": 0})

    for paquet in paquets:
        # Clé unique identifiant ce flux
        cle = (
            paquet["ip_src"] or "inconnu",
            paquet["ip_dst"] or "inconnu",
            paquet["protocole"] or "AUTRE"
        )

        # Incrémenter le compteur de paquets et la taille totale
        agregation[cle]["nb_paquets"]   += 1
        agregation[cle]["taille_totale"] += paquet["taille"] or 0

    # Convertir le dictionnaire en liste de flux
    flux_list = []
    for (ip_src, ip_dst, protocole), stats in agregation.items():
        flux_list.append({
            "ip_src"       : ip_src,
            "ip_dst"       : ip_dst,
            "protocole"    : protocole,
            "nb_paquets"   : stats["nb_paquets"],
            "taille_totale": stats["taille_totale"]
        })

    return flux_list


# ════════════════════════════════════════════════════════════════
# SECTION 3 — PRÉPARATION POUR LA BASE DE DONNÉES
# ════════════════════════════════════════════════════════════════

def preparer_paquets_bd(paquets, capture_id):
    """
    Convertit la liste de paquets en tuples prêts pour
    l'insertion batch dans SQLite via db.inserer_paquets().

    Paramètres :
        paquets    (list[dict]) : Liste de paquets parsés
        capture_id (int)        : ID de la capture parente

    Retourne :
        list[tuple] : Liste de tuples dans l'ordre des colonnes
                      de la table paquets
    """
    tuples = []

    for p in paquets:
        tuples.append((
            capture_id,       # capture_id — clé étrangère
            p["numero"],      # numero
            p["timestamp"],   # timestamp
            p["ip_src"],      # ip_src
            p["ip_dst"],      # ip_dst
            p["protocole"],   # protocole
            p["port_src"],    # port_src
            p["port_dst"],    # port_dst
            p["taille"],      # taille
            p["info"]         # info
        ))

    return tuples


def preparer_flux_bd(flux_list, capture_id):
    """
    Convertit la liste de flux en tuples prêts pour
    l'insertion batch dans SQLite via db.inserer_flux().

    Paramètres :
        flux_list  (list[dict]) : Liste de flux calculés
        capture_id (int)        : ID de la capture parente

    Retourne :
        list[tuple] : Liste de tuples dans l'ordre des colonnes
                      de la table flux
    """
    tuples = []

    for f in flux_list:
        tuples.append((
            capture_id,          # capture_id — clé étrangère
            f["ip_src"],         # ip_src
            f["ip_dst"],         # ip_dst
            f["protocole"],      # protocole
            f["nb_paquets"],     # nb_paquets
            f["taille_totale"]   # taille_totale
        ))

    return tuples