"""
db.py — Gestion de la base de données SQLite pour CyberForge.
Crée le schéma, fournit les fonctions d'insertion et de requête.
"""

import sqlite3
import json
from datetime import datetime

# Chargement de la config
with open("config.json", "r") as f:
    CONFIG = json.load(f)

DB_PATH = CONFIG["database"]["path"]


def obtenir_connexion():
    """Retourne une connexion SQLite avec row_factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialiser_bd():
    """Crée toutes les tables si elles n'existent pas."""
    conn = obtenir_connexion()
    cur = conn.cursor()

    # Table utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            date_creation TEXT NOT NULL
        )
    """)

    # Table captures (fichiers importés)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            nom_fichier TEXT NOT NULL,
            date_import TEXT NOT NULL,
            nb_paquets INTEGER DEFAULT 0,
            nb_alertes INTEGER DEFAULT 0,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )
    """)

    # Table paquets
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paquets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capture_id INTEGER NOT NULL,
            numero INTEGER,
            timestamp TEXT,
            ip_src TEXT,
            ip_dst TEXT,
            protocole TEXT,
            port_src INTEGER,
            port_dst INTEGER,
            taille INTEGER,
            info TEXT,
            FOREIGN KEY (capture_id) REFERENCES captures(id)
        )
    """)

    # Table flux (conversations entre deux IPs)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capture_id INTEGER NOT NULL,
            ip_src TEXT,
            ip_dst TEXT,
            protocole TEXT,
            nb_paquets INTEGER DEFAULT 0,
            taille_totale INTEGER DEFAULT 0,
            FOREIGN KEY (capture_id) REFERENCES captures(id)
        )
    """)

    # Table alertes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            capture_id INTEGER NOT NULL,
            type_alerte TEXT,
            criticite TEXT,
            ip_src TEXT,
            ip_dst TEXT,
            description TEXT,
            timestamp TEXT,
            FOREIGN KEY (capture_id) REFERENCES captures(id)
        )
    """)

    # Table historique des actions
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            utilisateur_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            detail TEXT,
            date_action TEXT NOT NULL,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs(id)
        )
    """)

    conn.commit()
    conn.close()


# ─── UTILISATEURS ─────────────────────────────────────────────

def creer_utilisateur(nom, prenom, email, mot_de_passe_hash):
    """Insère un nouvel utilisateur."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, date_creation)
        VALUES (?, ?, ?, ?, ?)
    """, (nom, prenom, email, mot_de_passe_hash, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def obtenir_utilisateur_par_email(email):
    """Retourne un utilisateur par son email."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("SELECT * FROM utilisateurs WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    return user


def mettre_a_jour_utilisateur(user_id, nom, prenom, email):
    """Met à jour les infos d'un utilisateur."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        UPDATE utilisateurs SET nom = ?, prenom = ?, email = ?
        WHERE id = ?
    """, (nom, prenom, email, user_id))
    conn.commit()
    conn.close()


def mettre_a_jour_mot_de_passe(user_id, nouveau_hash):
    """Met à jour le mot de passe d'un utilisateur."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?",
                (nouveau_hash, user_id))
    conn.commit()
    conn.close()


# ─── CAPTURES ─────────────────────────────────────────────────

def creer_capture(utilisateur_id, nom_fichier):
    """Crée une entrée capture et retourne son id."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO captures (utilisateur_id, nom_fichier, date_import)
        VALUES (?, ?, ?)
    """, (utilisateur_id, nom_fichier, datetime.now().isoformat()))
    capture_id = cur.lastrowid
    conn.commit()
    conn.close()
    return capture_id


def mettre_a_jour_stats_capture(capture_id, nb_paquets, nb_alertes):
    """Met à jour les stats d'une capture après parsing."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        UPDATE captures SET nb_paquets = ?, nb_alertes = ?
        WHERE id = ?
    """, (nb_paquets, nb_alertes, capture_id))
    conn.commit()
    conn.close()


def obtenir_captures_utilisateur(utilisateur_id):
    """Retourne toutes les captures d'un utilisateur."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM captures WHERE utilisateur_id = ?
        ORDER BY date_import DESC
    """, (utilisateur_id,))
    captures = cur.fetchall()
    conn.close()
    return captures


def supprimer_capture(capture_id):
    """Supprime une capture et toutes ses données liées."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    for table in ["alertes", "flux", "paquets"]:
        cur.execute(f"DELETE FROM {table} WHERE capture_id = ?", (capture_id,))
    cur.execute("DELETE FROM captures WHERE id = ?", (capture_id,))
    conn.commit()
    conn.close()


# ─── PAQUETS ──────────────────────────────────────────────────

def inserer_paquets(paquets):
    """Insère une liste de paquets en batch."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO paquets
        (capture_id, numero, timestamp, ip_src, ip_dst, protocole, port_src, port_dst, taille, info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, paquets)
    conn.commit()
    conn.close()


def obtenir_paquets(capture_id, filtres=None):
    """Retourne les paquets d'une capture avec filtres optionnels."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    query = "SELECT * FROM paquets WHERE capture_id = ?"
    params = [capture_id]
    if filtres:
        if filtres.get("ip_src"):
            query += " AND ip_src LIKE ?"
            params.append(f"%{filtres['ip_src']}%")
        if filtres.get("protocole"):
            query += " AND protocole = ?"
            params.append(filtres["protocole"])
        if filtres.get("port_dst"):
            query += " AND port_dst = ?"
            params.append(filtres["port_dst"])
    query += " ORDER BY numero ASC"
    cur.execute(query, params)
    paquets = cur.fetchall()
    conn.close()
    return paquets


# ─── FLUX ─────────────────────────────────────────────────────

def inserer_flux(flux_list):
    """Insère les flux calculés."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO flux (capture_id, ip_src, ip_dst, protocole, nb_paquets, taille_totale)
        VALUES (?, ?, ?, ?, ?, ?)
    """, flux_list)
    conn.commit()
    conn.close()


# ─── ALERTES ──────────────────────────────────────────────────

def inserer_alertes(alertes):
    """Insère les alertes détectées."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO alertes
        (capture_id, type_alerte, criticite, ip_src, ip_dst, description, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, alertes)
    conn.commit()
    conn.close()


def obtenir_alertes(capture_id):
    """Retourne les alertes d'une capture."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM alertes WHERE capture_id = ?
        ORDER BY criticite ASC
    """, (capture_id,))
    alertes = cur.fetchall()
    conn.close()
    return alertes


# ─── HISTORIQUE ───────────────────────────────────────────────

def ajouter_historique(utilisateur_id, action, detail=""):
    """Enregistre une action dans l'historique."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO historique (utilisateur_id, action, detail, date_action)
        VALUES (?, ?, ?, ?)
    """, (utilisateur_id, action, detail, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def obtenir_historique(utilisateur_id):
    """Retourne l'historique d'un utilisateur."""
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM historique WHERE utilisateur_id = ?
        ORDER BY date_action DESC
    """, (utilisateur_id,))
    historique = cur.fetchall()
    conn.close()
    return historique