"""
════════════════════════════════════════════════════════════════
 gui/alerts_view.py — Vue de consultation des alertes IDS
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche les alertes détectées par l'IDS pour la capture active,
   filtrables par criticité (HAUTE / MOYENNE / FAIBLE). Chaque
   alerte est présentée sous forme de carte colorée indiquant le
   type, la criticité, les IPs impliquées et la description.
   Un résumé chiffré par criticité est affiché en haut de vue.
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
    obtenir_couleur_criticite
)

from db import obtenir_alertes


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTES
# ════════════════════════════════════════════════════════════════

# Mapping criticité → couleur d'accentuation de la carte
COULEURS_CRITICITE = {
    "HAUTE":   COULEUR_DANGER,
    "MOYENNE": COULEUR_AVERTISSEMENT,
    "FAIBLE":  COULEUR_INFO,
}

# Mapping criticité → emoji préfixe
EMOJI_CRITICITE = {
    "HAUTE":   "🔴",
    "MOYENNE": "🟠",
    "FAIBLE":  "🔵",
}

# Filtres disponibles dans la barre (ordre d'affichage)
FILTRES_CRITICITE = ["Toutes", "HAUTE", "MOYENNE", "FAIBLE"]


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CLASSE ALERTSVIEW
# ════════════════════════════════════════════════════════════════

class AlertsView(tk.Frame):
    """
    Vue affichant les alertes IDS de la capture active, avec
    filtrage par criticité et résumé statistique en en-tête.
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue des alertes.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp)  : Fenêtre principale, pour lire
                                          capture_courante_id

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        # Filtre actif : "Toutes", "HAUTE", "MOYENNE" ou "FAIBLE"
        self.filtre_actif = "Toutes"

        # Toutes les alertes chargées depuis la base
        self._alertes = []

        # Références aux boutons de filtre pour mettre à jour leur style
        self._boutons_filtres = {}

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — CONSTRUCTION GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'en-tête avec le titre et les cartes de résumé,
        la barre de filtre par criticité, puis la liste des alertes.

        Retourne :
            None
        """
        # ─── En-tête (titre + cartes résumé) ───
        cadre_entete = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_entete.pack(fill="x", padx=PADDING_GRAND, pady=(PADDING_GRAND, 0))

        tk.Label(
            cadre_entete,
            text="Alertes IDS",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        ).pack(anchor="w")

        # Charger les alertes avant de construire les cartes résumé
        self._charger_alertes()

        self._construire_cartes_resume(cadre_entete)
        self._construire_barre_filtres()
        self._construire_zone_liste()
        self._afficher_alertes_filtrees()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — CARTES RÉSUMÉ
    # ────────────────────────────────────────────────────────────

    def _construire_cartes_resume(self, parent):
        """
        Affiche trois petites cartes chiffrées (alertes HAUTE,
        MOYENNE, FAIBLE) sous le titre.

        Paramètres :
            parent (tk.Widget) : Conteneur parent (cadre_entete)

        Retourne :
            None
        """
        nb_haute   = sum(1 for a in self._alertes if a["criticite"] == "HAUTE")
        nb_moyenne = sum(1 for a in self._alertes if a["criticite"] == "MOYENNE")
        nb_faible  = sum(1 for a in self._alertes if a["criticite"] == "FAIBLE")

        cadre_cartes = tk.Frame(parent, bg=theme.get("bg_principal"))
        cadre_cartes.pack(anchor="w", pady=(PADDING_PETIT, PADDING_MOYEN))

        donnees_cartes = [
            (f"🔴  {nb_haute}",   "critique(s)",  COULEUR_DANGER),
            (f"🟠  {nb_moyenne}", "moyenne(s)",   COULEUR_AVERTISSEMENT),
            (f"🔵  {nb_faible}",  "faible(s)",    COULEUR_INFO),
        ]

        for valeur, libelle, couleur in donnees_cartes:
            carte = tk.Frame(
                cadre_cartes,
                bg=theme.get("bg_secondaire"),
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
                bg=theme.get("bg_secondaire"),
                fg=couleur
            ).pack(anchor="w")

            tk.Label(
                carte,
                text=libelle,
                font=POLICE_PETIT,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_secondaire")
            ).pack(anchor="w")

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — BARRE DE FILTRES PAR CRITICITÉ
    # ────────────────────────────────────────────────────────────

    def _construire_barre_filtres(self):
        """
        Construit une rangée de boutons-onglets (Toutes / HAUTE /
        MOYENNE / FAIBLE) permettant de filtrer les alertes affichées.

        Retourne :
            None
        """
        cadre = tk.Frame(self, bg=theme.get("bg_secondaire"),
                         padx=PADDING_MOYEN, pady=PADDING_PETIT)
        cadre.pack(fill="x", padx=PADDING_GRAND, pady=(0, PADDING_PETIT))

        for libelle in FILTRES_CRITICITE:
            est_actif = (libelle == self.filtre_actif)

            couleur_fond = (
                COULEURS_CRITICITE.get(libelle, theme.get("accent_principal"))
                if est_actif
                else theme.get("bg_secondaire")
            )
            couleur_texte = "#FFFFFF" if est_actif else theme.get("texte_secondaire")

            bouton = tk.Label(
                cadre,
                text=libelle,
                font=POLICE_PETIT,
                bg=couleur_fond,
                fg=couleur_texte,
                padx=PADDING_MOYEN,
                pady=4,
                cursor="hand2"
            )
            bouton.pack(side="left", padx=(0, PADDING_PETIT))
            bouton.bind("<Button-1>", lambda e, f=libelle: self._changer_filtre(f))

            self._boutons_filtres[libelle] = bouton

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — ZONE DE LISTE (CANVAS SCROLLABLE)
    # ────────────────────────────────────────────────────────────

    def _construire_zone_liste(self):
        """
        Construit la zone scrollable qui accueillera les cartes
        d'alertes. Utilise un Canvas + Frame intérieure pour le
        défilement vertical.

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

        self.cadre_alertes = tk.Frame(
            self.canvas_liste, bg=theme.get("bg_principal")
        )
        self._fenetre_canvas = self.canvas_liste.create_window(
            (0, 0), window=self.cadre_alertes, anchor="nw"
        )

        self.cadre_alertes.bind(
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

        # Scroll à la molette
        self.canvas_liste.bind_all(
            "<MouseWheel>",
            lambda e: self.canvas_liste.yview_scroll(
                int(-1 * (e.delta / 120)), "units"
            )
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 7 — CHARGEMENT ET AFFICHAGE DES ALERTES
    # ────────────────────────────────────────────────────────────

    def _charger_alertes(self):
        """
        Récupère les alertes de la capture active depuis la base.
        Stocke le résultat dans self._alertes (liste vide si aucune
        capture active).

        Retourne :
            None
        """
        capture_id = self.controleur.capture_courante_id

        if capture_id is None:
            self._alertes = []
            return

        self._alertes = list(obtenir_alertes(capture_id))

    def _afficher_alertes_filtrees(self):
        """
        Vide la zone de liste et reconstruit les cartes d'alertes
        correspondant au filtre actif.

        Retourne :
            None
        """
        # Vider les cartes existantes
        for widget in self.cadre_alertes.winfo_children():
            widget.destroy()

        if self.controleur.capture_courante_id is None:
            self._afficher_etat_vide(
                "Aucune capture active.",
                "Sélectionnez une capture dans le tableau de bord pour consulter ses alertes."
            )
            return

        # Filtrer selon le filtre actif
        if self.filtre_actif == "Toutes":
            alertes_affichees = self._alertes
        else:
            alertes_affichees = [
                a for a in self._alertes
                if a["criticite"] == self.filtre_actif
            ]

        if not alertes_affichees:
            self._afficher_etat_vide(
                "Aucune alerte à afficher.",
                f"Aucune alerte de criticité « {self.filtre_actif} » "
                "pour cette capture." if self.filtre_actif != "Toutes"
                else "Aucune anomalie n'a été détectée sur cette capture. 👍"
            )
            return

        for alerte in alertes_affichees:
            self._creer_carte_alerte(self.cadre_alertes, alerte)

        # Remonter en haut après reconstruction
        self.canvas_liste.yview_moveto(0)

    def _afficher_etat_vide(self, titre, detail):
        """
        Affiche un message centré quand aucune alerte n'est
        disponible (capture inactive ou filtre sans résultat).

        Paramètres :
            titre  (str) : Message principal (gras)
            detail (str) : Explication complémentaire

        Retourne :
            None
        """
        cadre = tk.Frame(self.cadre_alertes, bg=theme.get("bg_principal"))
        cadre.pack(expand=True, pady=PADDING_GRAND * 3)

        tk.Label(
            cadre,
            text=titre,
            font=POLICE_TEXTE_GRAS,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_principal")
        ).pack()

        tk.Label(
            cadre,
            text=detail,
            font=POLICE_TEXTE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire"),
            wraplength=500,
            justify="center"
        ).pack(pady=(PADDING_PETIT, 0))

    # ────────────────────────────────────────────────────────────
    # SECTION 8 — CARTE D'ALERTE INDIVIDUELLE
    # ────────────────────────────────────────────────────────────

    def _creer_carte_alerte(self, parent, alerte):
        """
        Construit une carte visuelle pour une alerte : bande de
        couleur latérale indiquant la criticité, type d'alerte,
        IPs impliquées, description et horodatage.

        Paramètres :
            parent (tk.Widget)   : Conteneur parent (cadre_alertes)
            alerte (sqlite3.Row) : Alerte à afficher

        Retourne :
            None
        """
        criticite = alerte["criticite"] or "FAIBLE"
        couleur   = COULEURS_CRITICITE.get(criticite, COULEUR_INFO)
        emoji     = EMOJI_CRITICITE.get(criticite, "🔵")

        # ─── Conteneur de la carte avec bordure gauche colorée ───
        cadre_carte = tk.Frame(
            parent,
            bg=theme.get("bg_secondaire"),
            pady=0
        )
        cadre_carte.pack(fill="x", pady=(0, PADDING_PETIT))

        # Bande colorée verticale à gauche (indicateur de criticité)
        bande = tk.Frame(cadre_carte, bg=couleur, width=5)
        bande.pack(side="left", fill="y")

        # Corps de la carte
        corps = tk.Frame(
            cadre_carte,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_MOYEN,
            pady=PADDING_MOYEN
        )
        corps.pack(side="left", fill="both", expand=True)

        # ─── Ligne 1 : type d'alerte + badge criticité ───
        cadre_ligne1 = tk.Frame(corps, bg=theme.get("bg_secondaire"))
        cadre_ligne1.pack(fill="x")

        tk.Label(
            cadre_ligne1,
            text=f"{emoji}  {alerte['type_alerte'] or 'Alerte inconnue'}",
            font=POLICE_TEXTE_GRAS,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_principal"),
            anchor="w"
        ).pack(side="left")

        tk.Label(
            cadre_ligne1,
            text=criticite,
            font=POLICE_PETIT,
            bg=couleur,
            fg="#FFFFFF",
            padx=6,
            pady=2
        ).pack(side="right")

        # ─── Ligne 2 : IPs impliquées ───
        ip_src = alerte["ip_src"] or "—"
        ip_dst = alerte["ip_dst"] or "—"

        tk.Label(
            corps,
            text=f"{ip_src}  →  {ip_dst}",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            anchor="w"
        ).pack(anchor="w", pady=(PADDING_PETIT, 0))

        # ─── Ligne 3 : description ───
        if alerte["description"]:
            tk.Label(
                corps,
                text=alerte["description"],
                font=POLICE_TEXTE,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_principal"),
                anchor="w",
                wraplength=700,
                justify="left"
            ).pack(anchor="w", pady=(PADDING_PETIT, 0))

        # ─── Ligne 4 : horodatage (discret, à droite) ───
        if alerte["timestamp"]:
            tk.Label(
                corps,
                text=alerte["timestamp"][:19].replace("T", " "),
                font=POLICE_PETIT,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_secondaire"),
                anchor="e"
            ).pack(anchor="e", pady=(PADDING_PETIT, 0))

        # Séparateur discret sous chaque carte
        tk.Frame(
            parent,
            bg=theme.get("bordure"),
            height=1
        ).pack(fill="x")

    # ────────────────────────────────────────────────────────────
    # SECTION 9 — CHANGEMENT DE FILTRE
    # ────────────────────────────────────────────────────────────

    def _changer_filtre(self, filtre):
        """
        Met à jour le filtre actif, resyle les boutons de la barre
        de filtre et reconstruit la liste des alertes affichées.

        Paramètres :
            filtre (str) : Nouveau filtre ("Toutes", "HAUTE",
                           "MOYENNE" ou "FAIBLE")

        Retourne :
            None
        """
        if filtre == self.filtre_actif:
            return

        self.filtre_actif = filtre

        # Mettre à jour le style de chaque bouton
        for libelle, bouton in self._boutons_filtres.items():
            est_actif = (libelle == filtre)
            couleur_fond = (
                COULEURS_CRITICITE.get(libelle, theme.get("accent_principal"))
                if est_actif
                else theme.get("bg_secondaire")
            )
            bouton.configure(
                bg=couleur_fond,
                fg="#FFFFFF" if est_actif else theme.get("texte_secondaire")
            )

        self._afficher_alertes_filtrees()