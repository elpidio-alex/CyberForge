"""
════════════════════════════════════════════════════════════════
 gui/dashboard_view.py — Tableau de bord principal
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Vue d'accueil après connexion. Affiche un résumé chiffré
   (nombre de captures, paquets, alertes par criticité) et la
   liste des captures de l'utilisateur, avec possibilité de
   sélectionner une capture comme "capture active" (stockée dans
   controleur.capture_courante_id) ou d'en supprimer une.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk

from gui.theme import (
    theme,
    POLICE_TITRE,
    POLICE_SOUS_TITRE,
    POLICE_TEXTE,
    POLICE_TEXTE_GRAS,
    POLICE_PETIT,
    POLICE_CHIFFRE_CLE,
    PADDING_GRAND,
    PADDING_MOYEN,
    PADDING_PETIT,
    COULEUR_DANGER,
    COULEUR_AVERTISSEMENT,
    COULEUR_INFO,
    obtenir_couleur_criticite
)

from db import obtenir_captures_utilisateur, obtenir_alertes, supprimer_capture
from history_log import log_suppression_capture


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE DASHBOARDVIEW
# ════════════════════════════════════════════════════════════════

class DashboardView(tk.Frame):
    """
    Vue affichant les statistiques globales de l'utilisateur et
    la liste de ses captures importées, avec sélection/suppression.
    """

    def __init__(self, parent, controleur):
        """
        Construit le tableau de bord.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp)  : Fenêtre principale, pour lire
                                          utilisateur_courant et lire/écrire
                                          capture_courante_id

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur
        self.utilisateur = controleur.utilisateur_courant

        # Charger les captures de l'utilisateur dès la construction
        self.captures = obtenir_captures_utilisateur(self.utilisateur["id"])

        # Références aux lignes du tableau de captures, pour pouvoir
        # les surligner/reconstruire lors d'une sélection
        self._lignes_captures = {}

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — CONSTRUCTION GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'en-tête, les cartes de statistiques et le
        tableau des captures.

        Retourne :
            None
        """
        # Zone défilable simple : un cadre avec padding généreux
        cadre_principal = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_principal.pack(fill="both", expand=True, padx=PADDING_GRAND, pady=PADDING_GRAND)

        self._construire_entete(cadre_principal)
        self._construire_cartes_statistiques(cadre_principal)
        self._construire_liste_captures(cadre_principal)

    def _construire_entete(self, parent):
        """
        Affiche le titre de la vue et un message de bienvenue
        personnalisé avec le prénom de l'utilisateur.

        Paramètres :
            parent (tk.Widget) : Conteneur parent

        Retourne :
            None
        """
        label_titre = tk.Label(
            parent,
            text="Tableau de bord",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        )
        label_titre.pack(anchor="w")

        label_bienvenue = tk.Label(
            parent,
            text=f"Bienvenue, {self.utilisateur['prenom']} 👋",
            font=POLICE_TEXTE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire")
        )
        label_bienvenue.pack(anchor="w", pady=(0, PADDING_MOYEN))

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — CARTES DE STATISTIQUES
    # ────────────────────────────────────────────────────────────

    def _construire_cartes_statistiques(self, parent):
        """
        Calcule les statistiques globales (nb captures, nb paquets
        cumulés, nb alertes par criticité) et affiche une rangée
        de cartes chiffrées.

        Paramètres :
            parent (tk.Widget) : Conteneur parent

        Retourne :
            None
        """
        # ─── Calcul des statistiques agrégées ───
        nb_captures = len(self.captures)
        nb_paquets_total = sum(c["nb_paquets"] for c in self.captures)

        # Compter les alertes par criticité, toutes captures confondues
        nb_alertes_haute = 0
        nb_alertes_moyenne = 0
        nb_alertes_faible = 0

        for capture in self.captures:
            alertes = obtenir_alertes(capture["id"])
            for alerte in alertes:
                if alerte["criticite"] == "HAUTE":
                    nb_alertes_haute += 1
                elif alerte["criticite"] == "MOYENNE":
                    nb_alertes_moyenne += 1
                else:
                    nb_alertes_faible += 1

        # ─── Rangée de cartes ───
        cadre_cartes = tk.Frame(parent, bg=theme.get("bg_principal"))
        cadre_cartes.pack(fill="x", pady=(0, PADDING_GRAND))

        cartes = [
            ("Captures importées", nb_captures, theme.get("accent_principal")),
            ("Paquets analysés",    nb_paquets_total, theme.get("accent_secondaire")),
            ("Alertes critiques",   nb_alertes_haute, COULEUR_DANGER),
            ("Alertes moyennes",    nb_alertes_moyenne, COULEUR_AVERTISSEMENT),
        ]

        for libelle, valeur, couleur in cartes:
            self._creer_carte_statistique(cadre_cartes, libelle, valeur, couleur)

    def _creer_carte_statistique(self, parent, libelle, valeur, couleur):
        """
        Crée une carte individuelle affichant un chiffre clé et
        son libellé, avec une bordure de couleur distinctive.

        Paramètres :
            parent  (tk.Widget) : Conteneur parent (cadre_cartes)
            libelle (str)       : Texte descriptif sous le chiffre
            valeur  (int)       : Valeur numérique à afficher en grand
            couleur (str)       : Couleur hexadécimale du chiffre

        Retourne :
            None
        """
        carte = tk.Frame(
            parent,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_MOYEN,
            pady=PADDING_MOYEN,
            highlightthickness=1,
            highlightbackground=theme.get("bordure")
        )
        carte.pack(side="left", fill="both", expand=True, padx=(0, PADDING_PETIT))

        label_valeur = tk.Label(
            carte,
            text=str(valeur),
            font=POLICE_CHIFFRE_CLE,
            bg=theme.get("bg_secondaire"),
            fg=couleur
        )
        label_valeur.pack(anchor="w")

        label_libelle = tk.Label(
            carte,
            text=libelle,
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        )
        label_libelle.pack(anchor="w")

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — LISTE DES CAPTURES
    # ────────────────────────────────────────────────────────────

    def _construire_liste_captures(self, parent):
        """
        Affiche la liste des captures importées sous forme de
        lignes cliquables (sélection = capture active), avec un
        bouton de suppression par ligne.

        Paramètres :
            parent (tk.Widget) : Conteneur parent

        Retourne :
            None
        """
        label_section = tk.Label(
            parent,
            text="Mes captures",
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        )
        label_section.pack(anchor="w", pady=(0, PADDING_PETIT))

        # Cas où aucune capture n'a encore été importée
        if not self.captures:
            label_vide = tk.Label(
                parent,
                text="Aucune capture importée pour le moment. "
                     "Rendez-vous dans « Importer capture » pour commencer.",
                font=POLICE_TEXTE,
                bg=theme.get("bg_principal"),
                fg=theme.get("texte_secondaire"),
                wraplength=600,
                justify="left"
            )
            label_vide.pack(anchor="w")
            return

        cadre_liste = tk.Frame(parent, bg=theme.get("bg_secondaire"))
        cadre_liste.pack(fill="both", expand=True)

        for capture in self.captures:
            self._creer_ligne_capture(cadre_liste, capture)

    def _creer_ligne_capture(self, parent, capture):
        """
        Construit une ligne représentant une capture : nom de
        fichier, date, nb paquets/alertes, bouton "Ouvrir" et
        bouton de suppression.

        Paramètres :
            parent  (tk.Widget)   : Conteneur parent (cadre_liste)
            capture (sqlite3.Row) : Ligne de la table captures

        Retourne :
            None
        """
        est_active = (capture["id"] == self.controleur.capture_courante_id)

        ligne = tk.Frame(
            parent,
            bg=theme.get("bg_survol") if est_active else theme.get("bg_secondaire"),
            padx=PADDING_MOYEN,
            pady=PADDING_PETIT
        )
        ligne.pack(fill="x")

        # Séparateur discret entre chaque ligne
        tk.Frame(parent, bg=theme.get("bordure"), height=1).pack(fill="x")

        # ─── Informations principales (nom + date) ───
        cadre_infos = tk.Frame(ligne, bg=ligne["bg"])
        cadre_infos.pack(side="left", fill="x", expand=True)

        date_affichee = capture["date_import"][:19].replace("T", " ")

        label_nom = tk.Label(
            cadre_infos,
            text=f"📄 {capture['nom_fichier']}",
            font=POLICE_TEXTE_GRAS,
            bg=ligne["bg"],
            fg=theme.get("texte_principal"),
            anchor="w"
        )
        label_nom.pack(anchor="w")

        label_details = tk.Label(
            cadre_infos,
            text=(
                f"{date_affichee}  •  {capture['nb_paquets']} paquets  •  "
                f"{capture['nb_alertes']} alertes"
            ),
            font=POLICE_PETIT,
            bg=ligne["bg"],
            fg=theme.get("texte_secondaire"),
            anchor="w"
        )
        label_details.pack(anchor="w")

        # ─── Boutons d'action (Ouvrir / Supprimer) ───
        cadre_actions = tk.Frame(ligne, bg=ligne["bg"])
        cadre_actions.pack(side="right")

        texte_bouton = "✓ Active" if est_active else "Ouvrir"
        bouton_ouvrir = tk.Label(
            cadre_actions,
            text=texte_bouton,
            font=POLICE_PETIT,
            bg=theme.get("accent_principal") if est_active else theme.get("bg_principal"),
            fg="#FFFFFF" if est_active else theme.get("texte_principal"),
            padx=PADDING_PETIT,
            pady=4,
            cursor="hand2"
        )
        bouton_ouvrir.pack(side="left", padx=(0, PADDING_PETIT))
        bouton_ouvrir.bind("<Button-1>", lambda e, c=capture: self._selectionner_capture(c))

        bouton_supprimer = tk.Label(
            cadre_actions,
            text="🗑",
            font=POLICE_PETIT,
            bg=ligne["bg"],
            fg=COULEUR_DANGER,
            padx=PADDING_PETIT,
            pady=4,
            cursor="hand2"
        )
        bouton_supprimer.pack(side="left")
        bouton_supprimer.bind("<Button-1>", lambda e, c=capture: self._demander_suppression(c))

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — ACTIONS SUR LES CAPTURES
    # ────────────────────────────────────────────────────────────

    def _selectionner_capture(self, capture):
        """
        Définit la capture cliquée comme capture active de
        l'application (utilisée par packets_view et alerts_view),
        puis rafraîchit l'affichage pour surligner la sélection.

        Paramètres :
            capture (sqlite3.Row) : Capture sélectionnée

        Retourne :
            None
        """
        self.controleur.capture_courante_id = capture["id"]
        self._rafraichir()

    def _demander_suppression(self, capture):
        """
        Affiche une boîte de dialogue de confirmation avant de
        supprimer définitivement une capture et toutes ses données
        liées (paquets, flux, alertes).

        Paramètres :
            capture (sqlite3.Row) : Capture à supprimer

        Retourne :
            None
        """
        from tkinter import messagebox

        confirme = messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer définitivement la capture « {capture['nom_fichier']} » "
            f"et toutes ses données associées (paquets, flux, alertes) ?\n\n"
            f"Cette action est irréversible."
        )

        if not confirme:
            return

        supprimer_capture(capture["id"])
        log_suppression_capture(self.utilisateur["id"], capture["nom_fichier"])

        # Si la capture supprimée était la capture active, réinitialiser
        if self.controleur.capture_courante_id == capture["id"]:
            self.controleur.capture_courante_id = None

        self._rafraichir()

    def _rafraichir(self):
        """
        Recharge les captures depuis la base et reconstruit
        entièrement la vue pour refléter l'état à jour.

        Retourne :
            None
        """
        self.captures = obtenir_captures_utilisateur(self.utilisateur["id"])

        for widget in self.winfo_children():
            widget.destroy()

        self._construire_interface()