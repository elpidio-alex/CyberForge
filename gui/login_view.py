"""
════════════════════════════════════════════════════════════════
 gui/login_view.py — Vue de connexion et d'inscription
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche un formulaire de connexion et un formulaire
   d'inscription, basculables via un onglet. Utilise auth.py
   pour valider les identifiants et journalise la connexion
   réussie via history_log.py. Notifie CyberForgeApp (controleur)
   du succès via afficher_application_principale().
════════════════════════════════════════════════════════════════
"""

import tkinter as tk

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
    COULEUR_SUCCES
)

from auth import connecter_utilisateur, inscrire_utilisateur
from history_log import log_connexion


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE LOGINVIEW
# ════════════════════════════════════════════════════════════════

class LoginView(tk.Frame):
    """
    Vue affichée au démarrage de l'application et après une
    déconnexion. Propose deux modes : "Connexion" et "Inscription",
    basculables via deux onglets simples en haut de la carte.
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue de connexion/inscription.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (CyberForgeApp.conteneur)
            controleur (CyberForgeApp)  : Fenêtre principale, pour naviguer après
                                          une connexion réussie

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        # Mode actif : "connexion" ou "inscription"
        self.mode_actif = "connexion"

        # Références aux champs de saisie, construites dynamiquement
        # selon le mode actif (voir _construire_formulaire_connexion
        # et _construire_formulaire_inscription)
        self.champs = {}

        # Label utilisé pour afficher les messages d'erreur/succès
        self.label_message = None

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — CONSTRUCTION DE L'INTERFACE GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit la structure générale : conteneur centré, carte
        de connexion, onglets, puis délègue au formulaire actif.

        Retourne :
            None
        """
        # Conteneur qui centre la carte verticalement et horizontalement
        cadre_centre = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_centre.place(relx=0.5, rely=0.5, anchor="center")

        # ─── Titre de l'application au-dessus de la carte ───
        label_titre = tk.Label(
            cadre_centre,
            text="🛡️ CyberForge",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("accent_principal")
        )
        label_titre.pack(pady=(0, PADDING_MOYEN))

        # ─── Carte contenant les onglets + formulaire ───
        self.carte = tk.Frame(
            cadre_centre,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_GRAND,
            pady=PADDING_GRAND
        )
        self.carte.pack()

        # ─── Onglets Connexion / Inscription ───
        cadre_onglets = tk.Frame(self.carte, bg=theme.get("bg_secondaire"))
        cadre_onglets.pack(fill="x", pady=(0, PADDING_MOYEN))

        self.onglet_connexion = tk.Label(
            cadre_onglets,
            text="Connexion",
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("accent_principal"),
            cursor="hand2",
            padx=PADDING_MOYEN
        )
        self.onglet_connexion.pack(side="left")
        self.onglet_connexion.bind("<Button-1>", lambda e: self._basculer_mode("connexion"))

        self.onglet_inscription = tk.Label(
            cadre_onglets,
            text="Inscription",
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            cursor="hand2",
            padx=PADDING_MOYEN
        )
        self.onglet_inscription.pack(side="left")
        self.onglet_inscription.bind("<Button-1>", lambda e: self._basculer_mode("inscription"))

        # ─── Conteneur du formulaire actif (reconstruit à chaque bascule) ───
        self.cadre_formulaire = tk.Frame(self.carte, bg=theme.get("bg_secondaire"))
        self.cadre_formulaire.pack(fill="both")

        # ─── Label de message d'erreur/succès, sous le formulaire ───
        self.label_message = tk.Label(
            self.carte,
            text="",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            wraplength=320,
            justify="left"
        )
        self.label_message.pack(fill="x", pady=(PADDING_PETIT, 0))

        # Afficher le formulaire correspondant au mode initial
        self._construire_formulaire_connexion()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — BASCULE ENTRE CONNEXION / INSCRIPTION
    # ────────────────────────────────────────────────────────────

    def _basculer_mode(self, mode):
        """
        Change le mode actif (connexion/inscription), met à jour
        le style des onglets et reconstruit le formulaire affiché.

        Paramètres :
            mode (str) : "connexion" ou "inscription"

        Retourne :
            None
        """
        if mode == self.mode_actif:
            return  # Rien à faire si on clique sur l'onglet déjà actif

        self.mode_actif = mode

        # Mettre à jour la couleur des onglets pour surligner l'actif
        if mode == "connexion":
            self.onglet_connexion.configure(fg=theme.get("accent_principal"))
            self.onglet_inscription.configure(fg=theme.get("texte_secondaire"))
        else:
            self.onglet_inscription.configure(fg=theme.get("accent_principal"))
            self.onglet_connexion.configure(fg=theme.get("texte_secondaire"))

        # Effacer le message précédent (erreur/succès de l'autre mode)
        self._effacer_message()

        # Vider le conteneur du formulaire avant reconstruction
        for widget in self.cadre_formulaire.winfo_children():
            widget.destroy()
        self.champs = {}

        # Construire le formulaire correspondant au nouveau mode
        if mode == "connexion":
            self._construire_formulaire_connexion()
        else:
            self._construire_formulaire_inscription()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — FORMULAIRE DE CONNEXION
    # ────────────────────────────────────────────────────────────

    def _construire_formulaire_connexion(self):
        """
        Construit les champs email/mot de passe et le bouton
        de connexion dans self.cadre_formulaire.

        Retourne :
            None
        """
        self.champs["email"] = self._creer_champ_texte(
            self.cadre_formulaire, "Email"
        )
        self.champs["mot_de_passe"] = self._creer_champ_texte(
            self.cadre_formulaire, "Mot de passe", masque=True
        )

        bouton_connexion = tk.Label(
            self.cadre_formulaire,
            text="Se connecter",
            font=POLICE_BOUTON,
            bg=theme.get("accent_principal"),
            fg="#FFFFFF",
            cursor="hand2",
            pady=PADDING_PETIT
        )
        bouton_connexion.pack(fill="x", pady=(PADDING_MOYEN, 0))
        bouton_connexion.bind("<Button-1>", lambda e: self._soumettre_connexion())

        # Permettre la validation du formulaire avec la touche Entrée
        self.champs["mot_de_passe"].bind("<Return>", lambda e: self._soumettre_connexion())

    def _soumettre_connexion(self):
        """
        Récupère les champs saisis, appelle auth.connecter_utilisateur(),
        et gère le résultat : navigation vers la vue principale en cas
        de succès, ou affichage du message d'erreur.

        Retourne :
            None
        """
        email = self.champs["email"].get()
        mot_de_passe = self.champs["mot_de_passe"].get()

        succes, resultat = connecter_utilisateur(email, mot_de_passe)

        if succes:
            # resultat est ici l'objet utilisateur (sqlite3.Row)
            utilisateur = resultat

            # Journaliser la connexion réussie
            log_connexion(utilisateur["id"], utilisateur["email"])

            # Déléguer la navigation au contrôleur (CyberForgeApp)
            self.controleur.afficher_application_principale(utilisateur)
        else:
            # resultat est ici le message d'erreur
            self._afficher_message(resultat, erreur=True)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — FORMULAIRE D'INSCRIPTION
    # ────────────────────────────────────────────────────────────

    def _construire_formulaire_inscription(self):
        """
        Construit les champs nom/prénom/email/mot de passe/
        confirmation et le bouton d'inscription.

        Retourne :
            None
        """
        self.champs["nom"] = self._creer_champ_texte(
            self.cadre_formulaire, "Nom"
        )
        self.champs["prenom"] = self._creer_champ_texte(
            self.cadre_formulaire, "Prénom"
        )
        self.champs["email"] = self._creer_champ_texte(
            self.cadre_formulaire, "Email"
        )
        self.champs["mot_de_passe"] = self._creer_champ_texte(
            self.cadre_formulaire, "Mot de passe", masque=True
        )
        self.champs["confirmation"] = self._creer_champ_texte(
            self.cadre_formulaire, "Confirmer le mot de passe", masque=True
        )

        bouton_inscription = tk.Label(
            self.cadre_formulaire,
            text="Créer mon compte",
            font=POLICE_BOUTON,
            bg=theme.get("accent_secondaire"),
            fg="#FFFFFF",
            cursor="hand2",
            pady=PADDING_PETIT
        )
        bouton_inscription.pack(fill="x", pady=(PADDING_MOYEN, 0))
        bouton_inscription.bind("<Button-1>", lambda e: self._soumettre_inscription())

        self.champs["confirmation"].bind("<Return>", lambda e: self._soumettre_inscription())

    def _soumettre_inscription(self):
        """
        Valide localement la confirmation du mot de passe, puis
        délègue à auth.inscrire_utilisateur(). Si l'inscription
        réussit, bascule automatiquement vers l'onglet Connexion
        avec un message de succès.

        Retourne :
            None
        """
        nom          = self.champs["nom"].get()
        prenom       = self.champs["prenom"].get()
        email        = self.champs["email"].get()
        mot_de_passe = self.champs["mot_de_passe"].get()
        confirmation = self.champs["confirmation"].get()

        # Vérification locale avant d'appeler la couche auth
        if mot_de_passe != confirmation:
            self._afficher_message("Les mots de passe ne correspondent pas.", erreur=True)
            return

        succes, message = inscrire_utilisateur(nom, prenom, email, mot_de_passe)

        if succes:
            # Revenir à l'onglet connexion avec un message de succès
            self._basculer_mode("connexion")
            self._afficher_message(message, erreur=False)
            # Pré-remplir l'email pour éviter à l'utilisateur de le retaper
            self.champs["email"].insert(0, email.strip().lower())
        else:
            self._afficher_message(message, erreur=True)

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — UTILITAIRES DE CHAMP ET DE MESSAGE
    # ────────────────────────────────────────────────────────────

    def _creer_champ_texte(self, parent, libelle, masque=False):
        """
        Crée un label + champ de saisie Entry stylé selon le thème.

        Paramètres :
            parent  (tk.Widget) : Conteneur parent
            libelle (str)       : Texte affiché au-dessus du champ
            masque  (bool)      : True pour masquer la saisie (mot de passe)

        Retourne :
            tk.Entry : Le widget de saisie créé (pour récupérer .get())
        """
        cadre = tk.Frame(parent, bg=theme.get("bg_secondaire"))
        cadre.pack(fill="x", pady=(0, PADDING_PETIT))

        label = tk.Label(
            cadre,
            text=libelle,
            font=POLICE_TEXTE_GRAS,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_principal"),
            anchor="w"
        )
        label.pack(fill="x")

        entree = tk.Entry(
            cadre,
            font=POLICE_TEXTE,
            bg=theme.get("bg_input"),
            fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),  # Couleur du curseur
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal"),
            show="•" if masque else ""
        )
        entree.pack(fill="x", ipady=6)

        return entree

    def _afficher_message(self, texte, erreur=True):
        """
        Affiche un message d'erreur (rouge) ou de succès (vert)
        sous le formulaire.

        Paramètres :
            texte  (str)  : Message à afficher
            erreur (bool) : True pour une couleur d'erreur, False pour succès

        Retourne :
            None
        """
        self.label_message.configure(
            text=texte,
            fg=COULEUR_DANGER if erreur else COULEUR_SUCCES
        )

    def _effacer_message(self):
        """
        Vide le label de message (appelé lors de la bascule de mode).

        Retourne :
            None
        """
        self.label_message.configure(text="")