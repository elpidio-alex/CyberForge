"""
════════════════════════════════════════════════════════════════
 auth.py — Module d'authentification
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Gère l'inscription, la connexion et la modification du profil
   utilisateur. Utilise bcrypt pour le hachage sécurisé des
   mots de passe. Ne manipule jamais les mots de passe en clair
   en dehors de cette couche.
════════════════════════════════════════════════════════════════
"""

import bcrypt  # Bibliothèque de hachage sécurisé des mots de passe

# Import des fonctions de base de données nécessaires
from db import (
    creer_utilisateur,
    obtenir_utilisateur_par_email,
    mettre_a_jour_utilisateur,
    mettre_a_jour_mot_de_passe,
    obtenir_connexion
)


# ════════════════════════════════════════════════════════════════
# SECTION 1 — INSCRIPTION
# ════════════════════════════════════════════════════════════════

def inscrire_utilisateur(nom, prenom, email, mot_de_passe):
    """
    Inscrit un nouvel utilisateur dans la base de données.

    Paramètres :
        nom         (str) : Nom de famille de l'utilisateur
        prenom      (str) : Prénom de l'utilisateur
        email       (str) : Adresse email (identifiant unique)
        mot_de_passe(str) : Mot de passe en clair (sera haché)

    Retourne :
        (True,  "OK")              si l'inscription réussit
        (False, "message erreur")  si une validation échoue
    """
    # Vérifier qu'aucun compte n'existe déjà avec cet email
    if obtenir_utilisateur_par_email(email):
        return False, "Un compte avec cet email existe déjà."

    # Vérifier que le nom et le prénom ne sont pas vides
    if not nom.strip() or not prenom.strip():
        return False, "Le nom et le prénom sont obligatoires."

    # Le mot de passe doit avoir au moins 6 caractères
    if len(mot_de_passe) < 6:
        return False, "Le mot de passe doit contenir au moins 6 caractères."

    # Hacher le mot de passe avec bcrypt avant stockage
    # bcrypt.gensalt() génère un sel aléatoire pour renforcer la sécurité
    hash_mdp = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Insérer l'utilisateur en base avec les données nettoyées
    creer_utilisateur(
        nom.strip(),
        prenom.strip(),
        email.strip().lower(),  # Email toujours en minuscules
        hash_mdp
    )

    return True, "Compte créé avec succès."


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CONNEXION
# ════════════════════════════════════════════════════════════════

def connecter_utilisateur(email, mot_de_passe):
    """
    Vérifie les identifiants et connecte l'utilisateur.

    Paramètres :
        email        (str) : Adresse email saisie
        mot_de_passe (str) : Mot de passe saisi en clair

    Retourne :
        (True,  utilisateur) : Objet Row SQLite si connexion réussie
        (False, "message")   : Message d'erreur si échec
    """
    # Vérifier que les deux champs sont remplis
    if not email.strip() or not mot_de_passe.strip():
        return False, "Veuillez remplir tous les champs."

    # Rechercher l'utilisateur par email en base
    user = obtenir_utilisateur_par_email(email.strip().lower())

    # Si aucun compte trouvé avec cet email
    if not user:
        return False, "Aucun compte trouvé avec cet email."

    # Comparer le mot de passe saisi avec le hash stocké en base
    # bcrypt.checkpw() gère la comparaison sécurisée
    if not bcrypt.checkpw(mot_de_passe.encode("utf-8"), user["mot_de_passe"].encode("utf-8")):
        return False, "Mot de passe incorrect."

    # Connexion réussie — retourner l'objet utilisateur complet
    return True, user


# ════════════════════════════════════════════════════════════════
# SECTION 3 — MODIFICATION DU PROFIL
# ════════════════════════════════════════════════════════════════

def modifier_profil(user_id, nom, prenom, email):
    """
    Met à jour les informations personnelles d'un utilisateur.

    Paramètres :
        user_id (int) : Identifiant de l'utilisateur connecté
        nom     (str) : Nouveau nom
        prenom  (str) : Nouveau prénom
        email   (str) : Nouvel email

    Retourne :
        (True,  "OK")             si la mise à jour réussit
        (False, "message erreur") si une validation échoue
    """
    # Vérifier qu'aucun champ n'est vide
    if not nom.strip() or not prenom.strip() or not email.strip():
        return False, "Tous les champs sont obligatoires."

    # Vérifier que le nouvel email n'est pas déjà utilisé par un autre compte
    existant = obtenir_utilisateur_par_email(email.strip().lower())
    if existant and existant["id"] != user_id:
        return False, "Cet email est déjà utilisé par un autre compte."

    # Appliquer la mise à jour en base
    mettre_a_jour_utilisateur(
        user_id,
        nom.strip(),
        prenom.strip(),
        email.strip().lower()
    )

    return True, "Profil mis à jour avec succès."


# ════════════════════════════════════════════════════════════════
# SECTION 4 — CHANGEMENT DE MOT DE PASSE
# ════════════════════════════════════════════════════════════════

def modifier_mot_de_passe(user_id, ancien_mdp, nouveau_mdp, confirmation):
    """
    Change le mot de passe après vérification de l'ancien.

    Paramètres :
        user_id      (int) : Identifiant de l'utilisateur connecté
        ancien_mdp   (str) : Mot de passe actuel (pour vérification)
        nouveau_mdp  (str) : Nouveau mot de passe souhaité
        confirmation (str) : Répétition du nouveau mot de passe

    Retourne :
        (True,  "OK")             si le changement réussit
        (False, "message erreur") si une validation échoue
    """
    # Vérifier que tous les champs sont remplis
    if not ancien_mdp.strip() or not nouveau_mdp.strip():
        return False, "Tous les champs sont obligatoires."

    # Le nouveau mot de passe et la confirmation doivent être identiques
    if nouveau_mdp != confirmation:
        return False, "Le nouveau mot de passe et la confirmation ne correspondent pas."

    # Le nouveau mot de passe doit respecter la longueur minimale
    if len(nouveau_mdp) < 6:
        return False, "Le nouveau mot de passe doit contenir au moins 6 caractères."

    # Récupérer le hash du mot de passe actuel depuis la base
    conn = obtenir_connexion()
    cur = conn.cursor()
    cur.execute("SELECT mot_de_passe FROM utilisateurs WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    # Cas improbable mais à gérer : utilisateur introuvable
    if not row:
        return False, "Utilisateur introuvable."

    # Vérifier que l'ancien mot de passe saisi correspond au hash en base
    if not bcrypt.checkpw(ancien_mdp.encode("utf-8"), row["mot_de_passe"].encode("utf-8")):
        return False, "Ancien mot de passe incorrect."

    # Hacher le nouveau mot de passe avant stockage
    nouveau_hash = bcrypt.hashpw(nouveau_mdp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Mettre à jour le hash en base de données
    mettre_a_jour_mot_de_passe(user_id, nouveau_hash)

    return True, "Mot de passe modifié avec succès."