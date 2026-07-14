"""
════════════════════════════════════════════════════════════════
 gui/profile_view.py — Vue du profil utilisateur
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Permet à l'utilisateur connecté de consulter et modifier ses
   informations personnelles (nom, prénom, email), de changer
   son mot de passe, de consulter ses statistiques d'utilisation
   et de supprimer définitivement son compte.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import messagebox
import bcrypt

from gui.theme import (
    theme,
    POLICE_TITRE,
    POLICE_SOUS_TITRE,
    POLICE_TEXTE,
    POLICE_TEXTE_GRAS,
    POLICE_BOUTON,
    POLICE_PETIT,
    PADDING_GRAND,
    PADDING_MOYEN,
    PADDING_PETIT,
    COULEUR_DANGER,
    COULEUR_SUCCES,
    COULEUR_INFO,
)

from db import (
    mettre_a_jour_utilisateur,
    mettre_a_jour_mot_de_passe,
    obtenir_captures_utilisateur,
    obtenir_historique,
    ajouter_historique,
)


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE PROFILEVIEW
# ════════════════════════════════════════════════════════════════

class ProfileView(tk.Frame):
    """
    Vue du profil utilisateur : informations personnelles,
    changement de mot de passe, statistiques et suppression
    de compte.
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue du profil.

        Paramètres :
            parent     (tk.Widget)     : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp) : Fenêtre principale, pour lire
                                         utilisateur_connecte et déclencher
                                         la déconnexion

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — CONSTRUCTION GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'ensemble de la vue : en-tête, section infos,
        section mot de passe, section statistiques et section
        suppression de compte.

        Retourne :
            None
        """
        utilisateur = self.controleur.utilisateur_courant

        # Zone scrollable principale
        cadre_externe = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_externe.pack(fill="both", expand=True)

        canvas = tk.Canvas(
            cadre_externe,
            bg=theme.get("bg_principal"),
            highlightthickness=0
        )
        from tkinter import ttk
        scrollbar = ttk.Scrollbar(cadre_externe, orient="vertical",
                                   command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.cadre_contenu = tk.Frame(canvas, bg=theme.get("bg_principal"))
        fenetre = canvas.create_window((0, 0), window=self.cadre_contenu, anchor="nw")

        self.cadre_contenu.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(fenetre, width=e.width)
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
        )

        # ─── En-tête ───
        cadre_entete = tk.Frame(
            self.cadre_contenu, bg=theme.get("bg_principal")
        )
        cadre_entete.pack(fill="x", padx=PADDING_GRAND, pady=(PADDING_GRAND, PADDING_MOYEN))

        tk.Label(
            cadre_entete,
            text="Mon profil",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        ).pack(anchor="w")

        nom_complet = f"{utilisateur['prenom']} {utilisateur['nom']}" if utilisateur else "—"
        tk.Label(
            cadre_entete,
            text=nom_complet,
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire")
        ).pack(anchor="w")

        # ─── Sections ───
        self._construire_section_infos(utilisateur)
        self._construire_section_mot_de_passe(utilisateur)
        self._construire_section_statistiques(utilisateur)
        self._construire_section_suppression(utilisateur)

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — INFORMATIONS PERSONNELLES
    # ────────────────────────────────────────────────────────────

    def _construire_section_infos(self, utilisateur):
        """
        Construit la section de modification des informations
        personnelles (nom, prénom, email).

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur connecté

        Retourne :
            None
        """
        cadre = self._creer_cadre_section("Informations personnelles")

        champs = [
            ("Nom",    "nom",    utilisateur["nom"]    if utilisateur else ""),
            ("Prénom", "prenom", utilisateur["prenom"] if utilisateur else ""),
            ("Email",  "email",  utilisateur["email"]  if utilisateur else ""),
        ]

        self._entrees_infos = {}

        for libelle, cle, valeur in champs:
            self._creer_champ(cadre, libelle, valeur, cle, self._entrees_infos)

        # Message de retour
        self.label_retour_infos = tk.Label(
            cadre, text="", font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"), fg=COULEUR_SUCCES
        )
        self.label_retour_infos.pack(anchor="w", pady=(PADDING_PETIT, 0))

        # Bouton Enregistrer
        bouton = tk.Label(
            cadre,
            text="Enregistrer les modifications",
            font=POLICE_BOUTON,
            bg=theme.get("accent_principal"),
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_MOYEN,
            pady=6
        )
        bouton.pack(anchor="w", pady=(PADDING_PETIT, 0))
        bouton.bind("<Button-1>", lambda e: self._enregistrer_infos())

    def _enregistrer_infos(self):
        """
        Valide et enregistre les modifications des informations
        personnelles de l'utilisateur.

        Retourne :
            None
        """
        utilisateur = self.controleur.utilisateur_courant
        if not utilisateur:
            return

        nom    = self._entrees_infos["nom"].get().strip()
        prenom = self._entrees_infos["prenom"].get().strip()
        email  = self._entrees_infos["email"].get().strip()

        if not nom or not prenom or not email:
            self._afficher_retour(
                self.label_retour_infos,
                "Tous les champs sont obligatoires.",
                erreur=True
            )
            return

        if "@" not in email or "." not in email.split("@")[-1]:
            self._afficher_retour(
                self.label_retour_infos,
                "Adresse email invalide.",
                erreur=True
            )
            return

        mettre_a_jour_utilisateur(utilisateur["id"], nom, prenom, email)
        ajouter_historique(
            utilisateur["id"],
            "modification",
            "Informations personnelles mises à jour."
        )

        self._afficher_retour(
            self.label_retour_infos,
            "✓ Informations enregistrées avec succès."
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — CHANGEMENT DE MOT DE PASSE
    # ────────────────────────────────────────────────────────────

    def _construire_section_mot_de_passe(self, utilisateur):
        """
        Construit la section de changement de mot de passe.

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur connecté

        Retourne :
            None
        """
        cadre = self._creer_cadre_section("Changer le mot de passe")

        champs_mdp = [
            ("Mot de passe actuel",       "actuel"),
            ("Nouveau mot de passe",      "nouveau"),
            ("Confirmer le nouveau mdp",  "confirmation"),
        ]

        self._entrees_mdp = {}

        for libelle, cle in champs_mdp:
            self._creer_champ(cadre, libelle, "", cle,
                              self._entrees_mdp, masque=True)

        self.label_retour_mdp = tk.Label(
            cadre, text="", font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"), fg=COULEUR_SUCCES
        )
        self.label_retour_mdp.pack(anchor="w", pady=(PADDING_PETIT, 0))

        bouton = tk.Label(
            cadre,
            text="Changer le mot de passe",
            font=POLICE_BOUTON,
            bg=theme.get("accent_principal"),
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_MOYEN,
            pady=6
        )
        bouton.pack(anchor="w", pady=(PADDING_PETIT, 0))
        bouton.bind("<Button-1>", lambda e: self._changer_mot_de_passe())

    def _changer_mot_de_passe(self):
        """
        Valide et enregistre le nouveau mot de passe après
        vérification de l'ancien.

        Retourne :
            None
        """
        utilisateur = self.controleur.utilisateur_courant
        if not utilisateur:
            return

        actuel       = self._entrees_mdp["actuel"].get()
        nouveau      = self._entrees_mdp["nouveau"].get()
        confirmation = self._entrees_mdp["confirmation"].get()

        # Vérifier l'ancien mot de passe
        if not bcrypt.checkpw(actuel.encode(), utilisateur["mot_de_passe"].encode()):            
            self._afficher_retour(
                self.label_retour_mdp,
                "Mot de passe actuel incorrect.",
                erreur=True
            )
            return

        if len(nouveau) < 6:
            self._afficher_retour(
                self.label_retour_mdp,
                "Le nouveau mot de passe doit contenir au moins 6 caractères.",
                erreur=True
            )
            return

        if nouveau != confirmation:
            self._afficher_retour(
                self.label_retour_mdp,
                "Les mots de passe ne correspondent pas.",
                erreur=True
            )
            return

        nouveau_hash = bcrypt.hashpw(nouveau.encode(), bcrypt.gensalt()).decode()
        mettre_a_jour_mot_de_passe(utilisateur["id"], nouveau_hash)
        ajouter_historique(
            utilisateur["id"],
            "modification",
            "Mot de passe modifié."
        )

        # Vider les champs
        for entree in self._entrees_mdp.values():
            entree.delete(0, "end")

        self._afficher_retour(
            self.label_retour_mdp,
            "✓ Mot de passe mis à jour avec succès."
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — STATISTIQUES
    # ────────────────────────────────────────────────────────────

    def _construire_section_statistiques(self, utilisateur):
        """
        Construit la section affichant les statistiques
        d'utilisation de l'utilisateur connecté.

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur connecté

        Retourne :
            None
        """
        cadre = self._creer_cadre_section("Statistiques d'utilisation")

        if not utilisateur:
            tk.Label(
                cadre, text="Aucune donnée disponible.",
                font=POLICE_TEXTE,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_secondaire")
            ).pack(anchor="w")
            return

        captures   = list(obtenir_captures_utilisateur(utilisateur["id"]))
        historique = list(obtenir_historique(utilisateur["id"]))

        nb_captures  = len(captures)
        nb_paquets   = sum(c["nb_paquets"] for c in captures)
        nb_alertes   = sum(c["nb_alertes"] for c in captures)
        nb_actions   = len(historique)

        stats = [
            ("📁  Captures importées", str(nb_captures),  theme.get("accent_principal")),
            ("📦  Paquets analysés",   f"{nb_paquets:,}", COULEUR_INFO),
            ("🔔  Alertes détectées",  str(nb_alertes),   COULEUR_DANGER),
            ("📋  Actions enregistrées", str(nb_actions), COULEUR_SUCCES),
        ]

        cadre_cartes = tk.Frame(cadre, bg=theme.get("bg_secondaire"))
        cadre_cartes.pack(anchor="w", pady=(PADDING_PETIT, 0))

        for libelle, valeur, couleur in stats:
            carte = tk.Frame(
                cadre_cartes,
                bg=theme.get("bg_input"),
                padx=PADDING_MOYEN,
                pady=PADDING_PETIT,
                highlightthickness=1,
                highlightbackground=couleur
            )
            carte.pack(side="left", padx=(0, PADDING_PETIT))

            tk.Label(
                carte,
                text=valeur,
                font=POLICE_TEXTE_GRAS,
                bg=theme.get("bg_input"),
                fg=couleur
            ).pack(anchor="w")

            tk.Label(
                carte,
                text=libelle,
                font=POLICE_PETIT,
                bg=theme.get("bg_input"),
                fg=theme.get("texte_secondaire")
            ).pack(anchor="w")

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — SUPPRESSION DE COMPTE
    # ────────────────────────────────────────────────────────────

    def _construire_section_suppression(self, utilisateur):
        """
        Construit la section de suppression définitive du compte,
        avec avertissement visuel et double confirmation.

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur connecté

        Retourne :
            None
        """
        cadre = self._creer_cadre_section(
            "Zone de danger",
            couleur_bordure=COULEUR_DANGER
        )

        tk.Label(
            cadre,
            text="⚠  La suppression du compte est définitive et irréversible.\n"
                 "Toutes vos captures, paquets, alertes et données seront effacés.",
            font=POLICE_TEXTE,
            bg=theme.get("bg_secondaire"),
            fg=COULEUR_DANGER,
            justify="left",
            wraplength=600
        ).pack(anchor="w", pady=(0, PADDING_MOYEN))

        bouton = tk.Label(
            cadre,
            text="Supprimer mon compte",
            font=POLICE_BOUTON,
            bg=COULEUR_DANGER,
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_MOYEN,
            pady=6
        )
        bouton.pack(anchor="w")
        bouton.bind("<Button-1>", lambda e: self._confirmer_suppression())

    def _confirmer_suppression(self):
        """
        Demande une double confirmation avant de supprimer le
        compte de l'utilisateur connecté, puis déclenche la
        déconnexion.

        Retourne :
            None
        """
        utilisateur = self.controleur.utilisateur_courant
        if not utilisateur:
            return

        reponse = messagebox.askyesno(
            "Confirmation",
            "Êtes-vous sûr de vouloir supprimer définitivement votre compte ?\n"
            "Cette action est irréversible.",
            icon="warning"
        )
        if not reponse:
            return

        reponse2 = messagebox.askyesno(
            "Dernière confirmation",
            "Toutes vos données seront perdues.\n"
            "Confirmer la suppression ?",
            icon="warning"
        )
        if not reponse2:
            return

        self._supprimer_compte(utilisateur)

    def _supprimer_compte(self, utilisateur):
        """
        Supprime toutes les données de l'utilisateur depuis la base
        et déclenche la déconnexion via le contrôleur.

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur à supprimer

        Retourne :
            None
        """
        import sqlite3 as _sqlite3
        from db import obtenir_connexion, supprimer_capture

        # Supprimer toutes les captures (et leurs données liées)
        captures = list(obtenir_captures_utilisateur(utilisateur["id"]))
        for capture in captures:
            supprimer_capture(capture["id"])

        # Supprimer l'historique et l'utilisateur
        conn = obtenir_connexion()
        cur  = conn.cursor()
        cur.execute(
            "DELETE FROM historique WHERE utilisateur_id = ?",
            (utilisateur["id"],)
        )
        cur.execute(
            "DELETE FROM utilisateurs WHERE id = ?",
            (utilisateur["id"],)
        )
        conn.commit()
        conn.close()

        messagebox.showinfo(
            "Compte supprimé",
            "Votre compte a été supprimé avec succès."
        )

        # Retour à l'écran de connexion
        self.controleur.deconnecter()

    # ────────────────────────────────────────────────────────────
    # SECTION 7 — UTILITAIRES
    # ────────────────────────────────────────────────────────────

    def _creer_cadre_section(self, titre, couleur_bordure=None):
        """
        Crée un cadre de section avec titre et bordure optionnelle.

        Paramètres :
            titre           (str) : Titre de la section
            couleur_bordure (str) : Couleur de la bordure (None = bordure standard)

        Retourne :
            tk.Frame : Cadre intérieur prêt à accueillir les widgets
        """
        bordure = couleur_bordure or theme.get("bordure")

        cadre_ext = tk.Frame(
            self.cadre_contenu,
            bg=theme.get("bg_secondaire"),
            highlightthickness=1,
            highlightbackground=bordure
        )
        cadre_ext.pack(
            fill="x",
            padx=PADDING_GRAND,
            pady=(0, PADDING_MOYEN)
        )

        cadre_int = tk.Frame(
            cadre_ext,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_MOYEN,
            pady=PADDING_MOYEN
        )
        cadre_int.pack(fill="x")

        tk.Label(
            cadre_int,
            text=titre,
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_titre")
        ).pack(anchor="w", pady=(0, PADDING_MOYEN))

        return cadre_int

    def _creer_champ(self, parent, libelle, valeur, cle, registre, masque=False):
        """
        Crée un champ label + Entry et l'enregistre dans le dict registre.

        Paramètres :
            parent   (tk.Widget) : Conteneur parent
            libelle  (str)       : Texte du label
            valeur   (str)       : Valeur initiale du champ
            cle      (str)       : Clé dans le dict registre
            registre (dict)      : Dictionnaire {cle: Entry}
            masque   (bool)      : True pour masquer le texte (mot de passe)

        Retourne :
            None
        """
        cadre = tk.Frame(parent, bg=theme.get("bg_secondaire"))
        cadre.pack(fill="x", pady=(0, PADDING_PETIT))

        tk.Label(
            cadre,
            text=libelle,
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            width=28,
            anchor="w"
        ).pack(side="left")

        entree = tk.Entry(
            cadre,
            font=POLICE_TEXTE,
            width=30,
            bg=theme.get("bg_input"),
            fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal"),
            show="•" if masque else ""
        )
        entree.pack(side="left", ipady=4)

        if valeur:
            entree.insert(0, valeur)

        registre[cle] = entree

    def _afficher_retour(self, label, message, erreur=False):
        """
        Met à jour un label de retour avec un message coloré.

        Paramètres :
            label   (tk.Label) : Label à mettre à jour
            message (str)      : Message à afficher
            erreur  (bool)     : True = rouge, False = vert

        Retourne :
            None
        """
        label.configure(
            text=message,
            fg=COULEUR_DANGER if erreur else COULEUR_SUCCES
        )