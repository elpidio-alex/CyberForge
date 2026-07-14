"""
════════════════════════════════════════════════════════════════
 gui/login_view.py — Vue de connexion et d'inscription
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche une interface split : panneau gauche avec logo et
   identité de marque, panneau droit avec le formulaire de
   connexion ou d'inscription (basculables via un lien).
   Utilise auth.py pour valider les identifiants et journalise
   la connexion réussie via history_log.py.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from PIL import Image, ImageTk          # Affichage du logo PNG

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
# CONSTANTES VISUELLES DU PANNEAU GAUCHE
# ════════════════════════════════════════════════════════════════

# Couleur du panneau gauche — couleur exacte du fond de assets/logo.png
# (extraite par pipette : rgb(12, 27, 46)), pour une jonction invisible
# entre le bandeau et le logo.
COULEUR_PANNEAU_GAUCHE = "#0C1B2E"

# Couleur de fond principale de l'application (remplace l'ancien noir)
COULEUR_FOND_PRINCIPAL = "#FFFFFF"

# Largeur fixe du panneau gauche en pixels
LARGEUR_PANNEAU_GAUCHE = 380

# Taille du logo affiché dans le panneau gauche (agrandi, cf. demande Diamond)
TAILLE_LOGO = (280, 280)


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE LOGINVIEW
# ════════════════════════════════════════════════════════════════

class LoginView(tk.Frame):
    """
    Vue affichée au démarrage de l'application et après une
    déconnexion. Mise en page split :
      - Gauche : fond bleu marine avec logo et nom du projet
      - Droite : formulaire de connexion ou d'inscription
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue split connexion/inscription.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (CyberForgeApp.conteneur)
            controleur (CyberForgeApp)  : Fenêtre principale pour naviguer après
                                          une connexion réussie

        Retourne :
            None
        """
        super().__init__(parent, bg=COULEUR_FOND_PRINCIPAL)

        self.controleur = controleur

        # Mode actif : "connexion" ou "inscription"
        self.mode_actif = "connexion"

        # Références aux champs de saisie, reconstruites à chaque bascule
        self.champs = {}

        # Label de message d'erreur/succès sous le formulaire
        self.label_message = None

        # Référence à l'image du logo (doit rester en mémoire pour Tkinter)
        self._image_logo = None

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — CONSTRUCTION DE L'INTERFACE SPLIT
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit la mise en page split :
          - Panneau gauche (bleu marine) : logo + nom
          - Panneau droit (fond app)     : formulaire

        Retourne :
            None
        """
        # ─── Panneau gauche : identité de marque ───────────────
        self.panneau_gauche = tk.Frame(
            self,
            bg=COULEUR_PANNEAU_GAUCHE,
            width=LARGEUR_PANNEAU_GAUCHE
        )
        # pack_propagate(False) empêche le panneau de se réduire
        # à la taille de son contenu
        self.panneau_gauche.pack(side="left", fill="y")
        self.panneau_gauche.pack_propagate(False)

        self._construire_panneau_gauche()

        # ─── Panneau droit : formulaire ────────────────────────
        self.panneau_droit = tk.Frame(
            self,
            bg=COULEUR_FOND_PRINCIPAL
        )
        self.panneau_droit.pack(side="left", fill="both", expand=True)

        self._construire_panneau_droit()

    def _construire_panneau_gauche(self):
        """
        Remplit le panneau gauche : logo centré + nom du projet
        + sous-titre descriptif.

        Retourne :
            None
        """
        # Conteneur centré verticalement dans le panneau gauche
        cadre_centre = tk.Frame(self.panneau_gauche, bg=COULEUR_PANNEAU_GAUCHE)
        cadre_centre.place(relx=0.5, rely=0.5, anchor="center")

        # ─── Logo PNG ──────────────────────────────────────────
        try:
            # Charger et redimensionner le logo depuis le dossier assets/
            img = Image.open("assets/logo.png").resize(
                TAILLE_LOGO, Image.LANCZOS
            )
            self._image_logo = ImageTk.PhotoImage(img)

            label_logo = tk.Label(
                cadre_centre,
                image=self._image_logo,
                bg=COULEUR_PANNEAU_GAUCHE
            )
            label_logo.pack(pady=(0, PADDING_MOYEN))

        except Exception:
            # Si le logo est absent, afficher un emoji bouclier à la place
            label_logo = tk.Label(
                cadre_centre,
                text="🛡️",
                font=("Times New Roman", 64),
                bg=COULEUR_PANNEAU_GAUCHE,
                fg="#FFFFFF"
            )
            label_logo.pack(pady=(0, PADDING_MOYEN))

        # ─── Nom du projet ─────────────────────────────────────
        tk.Label(
            cadre_centre,
            text="CyberForge",
            font=("Times New Roman", 24, "bold"),
            bg=COULEUR_PANNEAU_GAUCHE,
            fg="#FFFFFF"
        ).pack()

        # ─── Sous-titre descriptif ─────────────────────────────
        tk.Label(
            cadre_centre,
            text="Superviseur de captures réseau",
            font=("Times New Roman", 11, "italic"),
            bg=COULEUR_PANNEAU_GAUCHE,
            fg="#A0AEC0"
        ).pack(pady=(4, 0))

    def _construire_panneau_droit(self):
        """
        Remplit le panneau droit : carte centrée contenant
        le titre du formulaire actif, les champs, le bouton
        et le lien de bascule.

        Retourne :
            None
        """
        # Conteneur qui centre la carte dans le panneau droit
        cadre_centre = tk.Frame(
            self.panneau_droit,
            bg=COULEUR_FOND_PRINCIPAL
        )
        cadre_centre.place(relx=0.5, rely=0.5, anchor="center")

        # ─── Carte blanche (fond clair même en mode sombre) ────
        self.carte = tk.Frame(
            cadre_centre,
            bg="#FFFFFF",
            padx=200,
            pady=48
        )
        self.carte.pack()

        # ─── Titre du formulaire ───────────────────────────────
        self.label_titre_form = tk.Label(
            self.carte,
            text="Connexion",
            font=("Times New Roman", 28, "bold"),
            bg="#FFFFFF",
            fg="#1A202C"
        )
        self.label_titre_form.pack(anchor="w", pady=(0, PADDING_GRAND))

        # ─── Conteneur du formulaire (rechargé à chaque bascule) ─
        self.cadre_formulaire = tk.Frame(self.carte, bg="#FFFFFF")
        self.cadre_formulaire.pack(fill="both")

        # ─── Message d'erreur/succès ───────────────────────────
        self.label_message = tk.Label(
            self.carte,
            text="",
            font=POLICE_PETIT,
            bg="#FFFFFF",
            wraplength=320,
            justify="left"
        )
        self.label_message.pack(fill="x", pady=(PADDING_PETIT, 0))

        # Afficher le formulaire de connexion par défaut
        self._construire_formulaire_connexion()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — BASCULE ENTRE CONNEXION / INSCRIPTION
    # ────────────────────────────────────────────────────────────

    def _basculer_mode(self, mode):
        """
        Change le mode actif, met à jour le titre de la carte
        et reconstruit le formulaire.

        Paramètres :
            mode (str) : "connexion" ou "inscription"

        Retourne :
            None
        """
        if mode == self.mode_actif:
            return

        self.mode_actif = mode
        self._effacer_message()

        # Vider le formulaire précédent
        for widget in self.cadre_formulaire.winfo_children():
            widget.destroy()
        self.champs = {}

        # Mettre à jour le titre de la carte
        if mode == "connexion":
            self.label_titre_form.configure(text="Connexion")
            self._construire_formulaire_connexion()
        else:
            self.label_titre_form.configure(text="Créer un compte")
            self._construire_formulaire_inscription()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — FORMULAIRE DE CONNEXION
    # ────────────────────────────────────────────────────────────

    def _construire_formulaire_connexion(self):
        """
        Construit les champs email + mot de passe, le bouton
        Se connecter, et le lien vers l'inscription.

        Retourne :
            None
        """
        self.champs["email"] = self._creer_champ_texte(
            self.cadre_formulaire, "Adresse email"
        )
        self.champs["mot_de_passe"] = self._creer_champ_texte(
            self.cadre_formulaire, "Mot de passe", masque=True
        )

        # ─── Bouton Se connecter ───────────────────────────────
        bouton = tk.Label(
            self.cadre_formulaire,
            text="Se connecter",
            font=POLICE_BOUTON,
            bg="#2563EB",        # Bleu vif identique à CyberPyAudit
            fg="#FFFFFF",
            cursor="hand2",
            pady=10
        )
        bouton.pack(fill="x", pady=(PADDING_MOYEN, PADDING_PETIT))
        bouton.bind("<Button-1>", lambda e: self._soumettre_connexion())
        bouton.bind("<Enter>", lambda e: bouton.configure(bg="#1D4ED8"))
        bouton.bind("<Leave>", lambda e: bouton.configure(bg="#2563EB"))

        # Touche Entrée dans le champ mot de passe = soumettre
        self.champs["mot_de_passe"].bind(
            "<Return>", lambda e: self._soumettre_connexion()
        )

        # ─── Lien vers l'inscription ───────────────────────────
        lien = tk.Label(
            self.cadre_formulaire,
            text="Pas encore de compte ?  Créer un compte",
            font=("Times New Roman", 9, "underline"),
            bg="#FFFFFF",
            fg="#2563EB",
            cursor="hand2"
        )
        lien.pack()
        lien.bind("<Button-1>", lambda e: self._basculer_mode("inscription"))

    def _soumettre_connexion(self):
        """
        Récupère les champs, appelle auth.connecter_utilisateur()
        et gère le succès (navigation) ou l'échec (message d'erreur).

        Retourne :
            None
        """
        email        = self.champs["email"].get()
        mot_de_passe = self.champs["mot_de_passe"].get()

        succes, resultat = connecter_utilisateur(email, mot_de_passe)

        if succes:
            utilisateur = resultat
            log_connexion(utilisateur["id"], utilisateur["email"])
            self.controleur.afficher_application_principale(utilisateur)
        else:
            self._afficher_message(resultat, erreur=True)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — FORMULAIRE D'INSCRIPTION
    # ────────────────────────────────────────────────────────────

    def _construire_formulaire_inscription(self):
        """
        Construit les champs nom / prénom / email / mot de passe /
        confirmation, le bouton Créer le compte, et le lien retour.

        Retourne :
            None
        """
        self.champs["nom"] = self._creer_champ_texte(
            self.cadre_formulaire, "Nom d'utilisateur"
        )
        self.champs["prenom"] = self._creer_champ_texte(
            self.cadre_formulaire, "Prénom"
        )
        self.champs["email"] = self._creer_champ_texte(
            self.cadre_formulaire, "Adresse email"
        )
        self.champs["mot_de_passe"] = self._creer_champ_texte(
            self.cadre_formulaire, "Mot de passe", masque=True
        )
        self.champs["confirmation"] = self._creer_champ_texte(
            self.cadre_formulaire, "Confirmer le mot de passe", masque=True
        )

        # ─── Bouton Créer le compte ────────────────────────────
        bouton = tk.Label(
            self.cadre_formulaire,
            text="Créer le compte",
            font=POLICE_BOUTON,
            bg="#2563EB",
            fg="#FFFFFF",
            cursor="hand2",
            pady=10
        )
        bouton.pack(fill="x", pady=(PADDING_MOYEN, PADDING_PETIT))
        bouton.bind("<Button-1>", lambda e: self._soumettre_inscription())
        bouton.bind("<Enter>", lambda e: bouton.configure(bg="#1D4ED8"))
        bouton.bind("<Leave>", lambda e: bouton.configure(bg="#2563EB"))

        self.champs["confirmation"].bind(
            "<Return>", lambda e: self._soumettre_inscription()
        )

        # ─── Lien retour vers la connexion ─────────────────────
        lien = tk.Label(
            self.cadre_formulaire,
            text="Déjà un compte ?  Se connecter",
            font=("Times New Roman", 9, "underline"),
            bg="#FFFFFF",
            fg="#2563EB",
            cursor="hand2"
        )
        lien.pack()
        lien.bind("<Button-1>", lambda e: self._basculer_mode("connexion"))

    def _soumettre_inscription(self):
        """
        Valide la confirmation du mot de passe, appelle
        auth.inscrire_utilisateur(), puis bascule vers la
        connexion avec un message de succès si l'inscription réussit.

        Retourne :
            None
        """
        nom          = self.champs["nom"].get()
        prenom       = self.champs["prenom"].get()
        email        = self.champs["email"].get()
        mot_de_passe = self.champs["mot_de_passe"].get()
        confirmation = self.champs["confirmation"].get()

        if mot_de_passe != confirmation:
            self._afficher_message(
                "Les mots de passe ne correspondent pas.", erreur=True
            )
            return

        succes, message = inscrire_utilisateur(nom, prenom, email, mot_de_passe)

        if succes:
            self._basculer_mode("connexion")
            self._afficher_message(message, erreur=False)
            self.champs["email"].insert(0, email.strip().lower())
        else:
            self._afficher_message(message, erreur=True)

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — UTILITAIRES
    # ────────────────────────────────────────────────────────────

    def _creer_champ_texte(self, parent, libelle, masque=False):
        """
        Crée un label + Entry stylés (fond gris clair, bordure fine).

        Paramètres :
            parent  (tk.Widget) : Conteneur parent
            libelle (str)       : Texte affiché au-dessus du champ
            masque  (bool)      : True pour masquer la saisie (mot de passe)

        Retourne :
            tk.Entry : Le widget de saisie
        """
        cadre = tk.Frame(parent, bg="#FFFFFF")
        cadre.pack(fill="x", pady=(0, PADDING_PETIT))

        # Label du champ
        tk.Label(
            cadre,
            text=libelle,
            font=("Times New Roman", 10),
            bg="#FFFFFF",
            fg="#4A5568",
            anchor="w"
        ).pack(fill="x")

        
        # Champ de saisie
        entree = tk.Entry(
            cadre,
            font=("Times New Roman", 13),
            bg="#EDF2F7",
            fg="#1A202C",
            insertbackground="#1A202C",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#CBD5E0",
            highlightcolor="#2563EB",
            show="•" if masque else ""
        )
        entree.pack(fill="x", ipady=12)

        return entree

    def _afficher_message(self, texte, erreur=True):
        """
        Affiche un message rouge (erreur) ou vert (succès).

        Paramètres :
            texte  (str)  : Message à afficher
            erreur (bool) : True = rouge, False = vert

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