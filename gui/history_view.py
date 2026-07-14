"""
════════════════════════════════════════════════════════════════
 gui/history_view.py — Vue de l'historique des actions
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche l'historique chronologique des actions effectuées par
   l'utilisateur connecté (imports, suppressions, connexions…).
   Chaque entrée est présentée sous forme de ligne horodatée avec
   un badge de type d'action coloré. Un champ de recherche permet
   de filtrer les entrées par mot-clé (action ou détail).
════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import ttk

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
    COULEUR_AVERTISSEMENT,
    COULEUR_INFO,
    COULEUR_SUCCES,
)

from db import obtenir_historique


# ════════════════════════════════════════════════════════════════
# SECTION 1 — MAPPING COULEURS PAR TYPE D'ACTION
# ════════════════════════════════════════════════════════════════

# Mots-clés dans le champ "action" → couleur du badge
COULEURS_ACTION = {
    "import":      COULEUR_INFO,
    "suppression": COULEUR_DANGER,
    "connexion":   COULEUR_SUCCES,
    "déconnexion": COULEUR_AVERTISSEMENT,
    "inscription": COULEUR_SUCCES,
    "modification":COULEUR_AVERTISSEMENT,
}

def _couleur_action(action: str) -> str:
    """
    Retourne la couleur de badge associée à une action.
    Fallback : couleur accent principale du thème.

    Paramètres :
        action (str) : Libellé de l'action

    Retourne :
        str : Code couleur hexadécimal
    """
    action_lower = action.lower()
    for mot_cle, couleur in COULEURS_ACTION.items():
        if mot_cle in action_lower:
            return couleur
    return theme.get("accent_principal")


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CLASSE HISTORYVIEW
# ════════════════════════════════════════════════════════════════

class HistoryView(tk.Frame):
    """
    Vue affichant l'historique des actions de l'utilisateur
    connecté, avec recherche par mot-clé.
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue de l'historique.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp)  : Fenêtre principale, pour lire
                                          utilisateur_connecte

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        # Toutes les entrées chargées depuis la base
        self._entrees = []

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — CONSTRUCTION GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'en-tête, la barre de recherche et la liste
        scrollable des entrées d'historique.

        Retourne :
            None
        """
        # ─── En-tête ───
        cadre_entete = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_entete.pack(fill="x", padx=PADDING_GRAND, pady=(PADDING_GRAND, 0))

        tk.Label(
            cadre_entete,
            text="Historique des actions",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        ).pack(anchor="w")

        tk.Label(
            cadre_entete,
            text="Toutes les actions effectuées durant vos sessions.",
            font=POLICE_TEXTE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire")
        ).pack(anchor="w", pady=(2, PADDING_MOYEN))

        self._construire_barre_recherche()
        self._construire_zone_liste()
        self._charger_historique()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — BARRE DE RECHERCHE
    # ────────────────────────────────────────────────────────────

    def _construire_barre_recherche(self):
        """
        Construit une barre de recherche permettant de filtrer les
        entrées d'historique par mot-clé (action ou détail).

        Retourne :
            None
        """
        cadre = tk.Frame(self, bg=theme.get("bg_secondaire"),
                         padx=PADDING_MOYEN, pady=PADDING_PETIT)
        cadre.pack(fill="x", padx=PADDING_GRAND, pady=(0, PADDING_PETIT))

        tk.Label(
            cadre,
            text="🔍  Rechercher :",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        ).pack(side="left")

        self.champ_recherche = tk.Entry(
            cadre,
            font=POLICE_TEXTE,
            width=30,
            bg=theme.get("bg_input"),
            fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal")
        )
        self.champ_recherche.pack(side="left", padx=(8, PADDING_MOYEN), ipady=4)

        # Recherche en temps réel à chaque frappe
        self.champ_recherche.bind("<KeyRelease>", lambda e: self._filtrer())

        bouton_reset = tk.Label(
            cadre,
            text="✕",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            cursor="hand2",
            padx=PADDING_PETIT
        )
        bouton_reset.pack(side="left")
        bouton_reset.bind("<Button-1>", lambda e: self._reinitialiser_recherche())

        # Compteur d'entrées affiché à droite
        self.label_compteur = tk.Label(
            cadre,
            text="",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        )
        self.label_compteur.pack(side="right", padx=PADDING_PETIT)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — ZONE DE LISTE SCROLLABLE
    # ────────────────────────────────────────────────────────────

    def _construire_zone_liste(self):
        """
        Construit la zone scrollable (Canvas + Frame intérieure)
        qui accueillera les lignes d'historique.

        Retourne :
            None
        """
        cadre_externe = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_externe.pack(fill="both", expand=True,
                           padx=PADDING_GRAND, pady=(0, PADDING_GRAND))

        self.canvas_liste = tk.Canvas(
            cadre_externe,
            bg=theme.get("bg_principal"),
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(cadre_externe, orient="vertical",
                                   command=self.canvas_liste.yview)
        self.canvas_liste.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas_liste.pack(side="left", fill="both", expand=True)

        self.cadre_entrees = tk.Frame(
            self.canvas_liste,
            bg=theme.get("bg_principal")
        )
        self._fenetre_canvas = self.canvas_liste.create_window(
            (0, 0), window=self.cadre_entrees, anchor="nw"
        )

        self.cadre_entrees.bind(
            "<Configure>",
            lambda e: self.canvas_liste.configure(
                scrollregion=self.canvas_liste.bbox("all")
            )
        )
        self.canvas_liste.bind(
            "<Configure>",
            lambda e: self.canvas_liste.itemconfig(
                self._fenetre_canvas, width=e.width
            )
        )

        self.canvas_liste.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas_liste.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            )
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — CHARGEMENT ET AFFICHAGE
    # ────────────────────────────────────────────────────────────

    def _charger_historique(self):
        """
        Récupère l'historique de l'utilisateur connecté depuis la
        base et déclenche l'affichage.

        Retourne :
            None
        """
        utilisateur = self.controleur.utilisateur_courant
        
        if utilisateur is None:
            self._entrees = []
        else:
            self._entrees = list(obtenir_historique(utilisateur["id"]))

        self._afficher_entrees(self._entrees)

    def _afficher_entrees(self, entrees):
        """
        Vide la zone de liste et reconstruit les lignes à partir
        de la liste d'entrées passée en paramètre.

        Paramètres :
            entrees (list[sqlite3.Row]) : Entrées à afficher

        Retourne :
            None
        """
        for widget in self.cadre_entrees.winfo_children():
            widget.destroy()

        self.label_compteur.configure(
            text=f"{len(entrees)} entrée(s)"
        )

        if not entrees:
            self._afficher_etat_vide()
            return

        for entree in entrees:
            self._creer_ligne_entree(self.cadre_entrees, entree)

        self.canvas_liste.yview_moveto(0)

    def _afficher_etat_vide(self):
        """
        Affiche un message centré quand l'historique est vide ou
        qu'aucune entrée ne correspond à la recherche.

        Retourne :
            None
        """
        cadre = tk.Frame(self.cadre_entrees, bg=theme.get("bg_principal"))
        cadre.pack(expand=True, pady=PADDING_GRAND * 3)

        tk.Label(
            cadre,
            text="Aucune entrée à afficher.",
            font=POLICE_TEXTE_GRAS,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_principal")
        ).pack()

        tk.Label(
            cadre,
            text="L'historique de vos actions apparaîtra ici au fil de votre utilisation.",
            font=POLICE_TEXTE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire"),
            wraplength=480,
            justify="center"
        ).pack(pady=(PADDING_PETIT, 0))

    # ────────────────────────────────────────────────────────────
    # SECTION 7 — LIGNE D'ENTRÉE INDIVIDUELLE
    # ────────────────────────────────────────────────────────────

    def _creer_ligne_entree(self, parent, entree):
        """
        Construit une ligne d'historique : horodatage, badge action
        coloré et détail de l'opération.

        Paramètres :
            parent  (tk.Widget)      : Conteneur parent (cadre_entrees)
            entree  (sqlite3.Row)    : Entrée d'historique à afficher

        Retourne :
            None
        """
        action   = entree["action"] or "Action"
        detail   = entree["detail"] or ""
        date_brute = entree["date_action"] or ""

        # Formater la date : "2024-05-12T14:32:01.123456" → "2024-05-12  14:32:01"
        date_affichee = date_brute[:19].replace("T", "  ") if date_brute else "—"

        couleur_badge = _couleur_action(action)

        # ─── Ligne conteneur ───
        ligne = tk.Frame(
            parent,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_MOYEN,
            pady=PADDING_PETIT
        )
        ligne.pack(fill="x", pady=(0, 1))

        # ─── Colonne 1 : horodatage (largeur fixe) ───
        tk.Label(
            ligne,
            text=date_affichee,
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            width=20,
            anchor="w"
        ).pack(side="left", padx=(0, PADDING_MOYEN))

        # ─── Colonne 2 : badge type d'action ───
        tk.Label(
            ligne,
            text=action,
            font=POLICE_PETIT,
            bg=couleur_badge,
            fg="#FFFFFF",
            padx=8,
            pady=2
        ).pack(side="left", padx=(0, PADDING_MOYEN))

        # ─── Colonne 3 : détail (prend le reste de la largeur) ───
        if detail:
            tk.Label(
                ligne,
                text=detail,
                font=POLICE_TEXTE,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_principal"),
                anchor="w",
                justify="left"
            ).pack(side="left", fill="x", expand=True)

        # Séparateur discret
        tk.Frame(parent, bg=theme.get("bordure"), height=1).pack(fill="x")

    # ────────────────────────────────────────────────────────────
    # SECTION 8 — RECHERCHE / FILTRE
    # ────────────────────────────────────────────────────────────

    def _filtrer(self):
        """
        Filtre les entrées d'historique selon le mot-clé saisi
        dans le champ de recherche et reconstruit la liste.

        Retourne :
            None
        """
        mot_cle = self.champ_recherche.get().strip().lower()

        if not mot_cle:
            self._afficher_entrees(self._entrees)
            return

        filtrees = [
            e for e in self._entrees
            if mot_cle in (e["action"] or "").lower()
            or mot_cle in (e["detail"] or "").lower()
        ]
        self._afficher_entrees(filtrees)

    def _reinitialiser_recherche(self):
        """
        Vide le champ de recherche et réaffiche toutes les entrées.

        Retourne :
            None
        """
        self.champ_recherche.delete(0, "end")
        self._afficher_entrees(self._entrees)