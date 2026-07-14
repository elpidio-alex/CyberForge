"""
════════════════════════════════════════════════════════════════
 history_log.py — Module de journalisation des actions
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Fournit des fonctions de haut niveau pour enregistrer et
   consulter l'historique des actions utilisateur (importation
   de captures, connexions, suppressions, modifications de
   profil). S'appuie sur db.py pour la persistance SQLite.
════════════════════════════════════════════════════════════════
"""

# Import des fonctions de base de données pour l'historique
from db import ajouter_historique, obtenir_historique


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTES D'ACTIONS
# ════════════════════════════════════════════════════════════════

# Constantes pour les types d'actions enregistrées dans l'historique
# Utiliser ces constantes évite les fautes de frappe dans le code
ACTION_CONNEXION        = "CONNEXION"
ACTION_DECONNEXION      = "DECONNEXION"
ACTION_IMPORT_CAPTURE   = "IMPORT_CAPTURE"
ACTION_SUPPRESSION      = "SUPPRESSION_CAPTURE"
ACTION_MODIF_PROFIL     = "MODIFICATION_PROFIL"
ACTION_MODIF_MDP        = "MODIFICATION_MOT_DE_PASSE"
ACTION_CONSULTATION     = "CONSULTATION_CAPTURE"


# ════════════════════════════════════════════════════════════════
# SECTION 2 — FONCTIONS DE JOURNALISATION
# ════════════════════════════════════════════════════════════════

def log_connexion(user_id, email):
    """
    Enregistre une connexion réussie dans l'historique.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur connecté
        email   (str) : Email utilisé pour la connexion

    Retourne :
        None
    """
    # Enregistrer l'action avec l'email comme détail
    ajouter_historique(
        user_id,
        ACTION_CONNEXION,
        f"Connexion avec le compte : {email}"
    )


def log_deconnexion(user_id):
    """
    Enregistre une déconnexion dans l'historique.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur déconnecté

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_DECONNEXION,
        "Déconnexion de la session"
    )


def log_import_capture(user_id, nom_fichier, nb_paquets):
    """
    Enregistre l'importation d'un fichier de capture.

    Paramètres :
        user_id     (int) : Identifiant de l'utilisateur
        nom_fichier (str) : Nom du fichier .txt importé
        nb_paquets  (int) : Nombre de paquets parsés

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_IMPORT_CAPTURE,
        f"Fichier : {nom_fichier} — {nb_paquets} paquets importés"
    )


def log_suppression_capture(user_id, nom_fichier):
    """
    Enregistre la suppression d'une capture.

    Paramètres :
        user_id     (int) : Identifiant de l'utilisateur
        nom_fichier (str) : Nom du fichier supprimé

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_SUPPRESSION,
        f"Capture supprimée : {nom_fichier}"
    )


def log_modification_profil(user_id):
    """
    Enregistre une modification des informations du profil.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_MODIF_PROFIL,
        "Informations du profil mises à jour"
    )


def log_modification_mot_de_passe(user_id):
    """
    Enregistre un changement de mot de passe.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_MODIF_MDP,
        "Mot de passe modifié"
    )


def log_consultation_capture(user_id, nom_fichier):
    """
    Enregistre la consultation d'une capture existante.

    Paramètres :
        user_id     (int) : Identifiant de l'utilisateur
        nom_fichier (str) : Nom du fichier consulté

    Retourne :
        None
    """
    ajouter_historique(
        user_id,
        ACTION_CONSULTATION,
        f"Consultation de la capture : {nom_fichier}"
    )


# ════════════════════════════════════════════════════════════════
# SECTION 3 — FONCTIONS DE CONSULTATION
# ════════════════════════════════════════════════════════════════

def obtenir_historique_utilisateur(user_id):
    """
    Retourne l'historique complet des actions d'un utilisateur.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur

    Retourne :
        list[sqlite3.Row] : Liste des actions triées par date
                            décroissante (la plus récente en premier)
    """
    # Déléguer la requête à la couche db.py
    return obtenir_historique(user_id)


def formater_historique(historique):
    """
    Formate une liste d'entrées historique pour affichage dans
    l'interface Tkinter (tableau ou liste).

    Paramètres :
        historique (list[sqlite3.Row]) : Résultat brut de la BD

    Retourne :
        list[dict] : Liste de dictionnaires avec les clés :
                     'date', 'action', 'detail'
    """
    lignes = []  # Liste qui contiendra les lignes formatées

    for entree in historique:
        # Raccourcir la date ISO pour l'affichage (enlever les microsecondes)
        date_affichee = entree["date_action"][:19].replace("T", " ")

        # Construire un dictionnaire lisible pour chaque entrée
        lignes.append({
            "date"   : date_affichee,
            "action" : entree["action"],
            "detail" : entree["detail"] or ""
        })

    return lignes