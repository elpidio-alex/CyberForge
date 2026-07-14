"""
════════════════════════════════════════════════════════════════
 gui/packets_view.py — Vue de consultation des paquets
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche les paquets de la capture active dans un tableau
   scrollable, avec filtres par IP source, protocole et port
   destination. Un clic sur une ligne ouvre un panneau de détail
   latéral affichant tous les champs du paquet sélectionné.
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
    POLICE_PETIT,
    PADDING_GRAND,
    PADDING_MOYEN,
    PADDING_PETIT,
    COULEUR_DANGER,
    COULEUR_INFO,
    obtenir_couleur_criticite
)

from db import obtenir_paquets


# ════════════════════════════════════════════════════════════════
# SECTION 1 — COLONNES DU TABLEAU
# ════════════════════════════════════════════════════════════════

# Chaque entrée : (clé sqlite3.Row, en-tête affiché, largeur en px, alignement)
COLONNES = [
    ("numero",    "#",         45,  "center"),
    ("timestamp", "Horodatage", 155, "w"),
    ("ip_src",    "IP source",  130, "w"),
    ("ip_dst",    "IP dest.",   130, "w"),
    ("protocole", "Protocole",  90,  "center"),
    ("port_src",  "Port src",   75,  "center"),
    ("port_dst",  "Port dst",   75,  "center"),
    ("taille",    "Taille (o)", 85,  "center"),
    ("info",      "Info",       220, "w"),
]


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CLASSE PACKETSVIEW
# ════════════════════════════════════════════════════════════════

class PacketsView(tk.Frame):
    """
    Vue affichant les paquets de la capture active dans un tableau
    Treeview filtrable. Un panneau latéral glissant affiche les
    détails complets du paquet sélectionné.
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue des paquets.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp)  : Fenêtre principale, pour lire
                                          capture_courante_id

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        # Filtres actifs (lus depuis les champs de saisie au clic sur Filtrer)
        self._filtres_actifs = {}

        # Paquet actuellement sélectionné dans le tableau (sqlite3.Row)
        self._paquet_selectionne = None

        # Indicateur de visibilité du panneau de détail
        self._panneau_detail_visible = False

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — CONSTRUCTION GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'en-tête, la barre de filtres, le tableau
        Treeview et le panneau de détail latéral.

        Retourne :
            None
        """
        # ─── En-tête ───
        cadre_entete = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_entete.pack(fill="x", padx=PADDING_GRAND, pady=(PADDING_GRAND, 0))

        tk.Label(
            cadre_entete,
            text="Paquets capturés",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        ).pack(anchor="w")

        # ─── Corps principal : tableau + panneau de détail côte à côte ───
        cadre_corps = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_corps.pack(fill="both", expand=True,
                         padx=PADDING_GRAND, pady=PADDING_MOYEN)

        # Colonne gauche : filtres + tableau
        self.cadre_gauche = tk.Frame(cadre_corps, bg=theme.get("bg_principal"))
        self.cadre_gauche.pack(side="left", fill="both", expand=True)

        # Colonne droite : panneau de détail (masqué au départ)
        self.cadre_detail = tk.Frame(
            cadre_corps,
            bg=theme.get("bg_secondaire"),
            width=300,
            padx=PADDING_MOYEN,
            pady=PADDING_MOYEN
        )
        # Ne pas pack() ici — révélé dynamiquement au clic sur une ligne

        self._construire_barre_filtres(self.cadre_gauche)
        self._construire_tableau(self.cadre_gauche)
        self._construire_panneau_detail()
        self._charger_paquets()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — BARRE DE FILTRES
    # ────────────────────────────────────────────────────────────

    def _construire_barre_filtres(self, parent):
        """
        Construit une ligne horizontale de filtres (IP source,
        protocole, port dst) avec un bouton Filtrer et un bouton
        Réinitialiser.

        Paramètres :
            parent (tk.Widget) : Conteneur parent (cadre_gauche)

        Retourne :
            None
        """
        cadre = tk.Frame(parent, bg=theme.get("bg_secondaire"),
                         padx=PADDING_MOYEN, pady=PADDING_PETIT)
        cadre.pack(fill="x", pady=(0, PADDING_PETIT))

        # ─── Champ IP source ───
        tk.Label(
            cadre, text="IP source :", font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"), fg=theme.get("texte_secondaire")
        ).pack(side="left")

        self.champ_ip_src = tk.Entry(
            cadre, font=POLICE_TEXTE, width=15,
            bg=theme.get("bg_input"), fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal")
        )
        self.champ_ip_src.pack(side="left", padx=(4, PADDING_MOYEN), ipady=4)

        # ─── Champ protocole ───
        tk.Label(
            cadre, text="Protocole :", font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"), fg=theme.get("texte_secondaire")
        ).pack(side="left")

        self.champ_protocole = tk.Entry(
            cadre, font=POLICE_TEXTE, width=8,
            bg=theme.get("bg_input"), fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal")
        )
        self.champ_protocole.pack(side="left", padx=(4, PADDING_MOYEN), ipady=4)

        # ─── Champ port destination ───
        tk.Label(
            cadre, text="Port dst :", font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"), fg=theme.get("texte_secondaire")
        ).pack(side="left")

        self.champ_port_dst = tk.Entry(
            cadre, font=POLICE_TEXTE, width=7,
            bg=theme.get("bg_input"), fg=theme.get("texte_principal"),
            insertbackground=theme.get("texte_principal"),
            relief="flat",
            highlightthickness=1,
            highlightbackground=theme.get("bordure"),
            highlightcolor=theme.get("accent_principal")
        )
        self.champ_port_dst.pack(side="left", padx=(4, PADDING_MOYEN), ipady=4)

        # ─── Boutons Filtrer / Réinitialiser ───
        tk.Label(
            cadre,
            text="Filtrer",
            font=POLICE_BOUTON,
            bg=theme.get("accent_principal"),
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_PETIT,
            pady=3
        ).pack(side="left", padx=(0, PADDING_PETIT))

        # Bind après pack pour capturer le widget dans la fermeture
        for widget in cadre.winfo_children():
            if isinstance(widget, tk.Label) and widget.cget("text") == "Filtrer":
                widget.bind("<Button-1>", lambda e: self._appliquer_filtres())
                break

        bouton_reset = tk.Label(
            cadre,
            text="✕ Réinitialiser",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            cursor="hand2",
            padx=PADDING_PETIT,
            pady=3
        )
        bouton_reset.pack(side="left")
        bouton_reset.bind("<Button-1>", lambda e: self._reinitialiser_filtres())

        # Label compteur (mis à jour après chaque chargement)
        self.label_compteur = tk.Label(
            cadre,
            text="",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        )
        self.label_compteur.pack(side="right", padx=PADDING_PETIT)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — TABLEAU TREEVIEW
    # ────────────────────────────────────────────────────────────

    def _construire_tableau(self, parent):
        """
        Construit le widget ttk.Treeview avec scrollbars verticale
        et horizontale, stylé selon les couleurs du thème actif.

        Paramètres :
            parent (tk.Widget) : Conteneur parent (cadre_gauche)

        Retourne :
            None
        """
        cadre_tableau = tk.Frame(parent, bg=theme.get("bg_secondaire"))
        cadre_tableau.pack(fill="both", expand=True)

        # ─── Style ttk pour le Treeview ───
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "CyberForge.Treeview",
            background=theme.get("bg_secondaire"),
            foreground=theme.get("texte_principal"),
            rowheight=26,
            fieldbackground=theme.get("bg_secondaire"),
            font=POLICE_PETIT,
            borderwidth=0
        )
        style.configure(
            "CyberForge.Treeview.Heading",
            background=theme.get("bg_input"),
            foreground=theme.get("texte_secondaire"),
            font=POLICE_TEXTE_GRAS,
            relief="flat"
        )
        style.map(
            "CyberForge.Treeview",
            background=[("selected", theme.get("accent_principal"))],
            foreground=[("selected", "#FFFFFF")]
        )

        # ─── Treeview ───
        colonnes_ids = [col[0] for col in COLONNES]

        self.tableau = ttk.Treeview(
            cadre_tableau,
            columns=colonnes_ids,
            show="headings",
            style="CyberForge.Treeview",
            selectmode="browse"
        )

        for cle, entete, largeur, alignement in COLONNES:
            self.tableau.heading(cle, text=entete,
                                 anchor="center" if alignement == "center" else "w")
            self.tableau.column(cle, width=largeur, minwidth=40,
                                anchor=alignement, stretch=False)

        # ─── Scrollbars ───
        scroll_v = ttk.Scrollbar(cadre_tableau, orient="vertical",
                                  command=self.tableau.yview)
        scroll_h = ttk.Scrollbar(cadre_tableau, orient="horizontal",
                                  command=self.tableau.xview)
        self.tableau.configure(yscrollcommand=scroll_v.set,
                                xscrollcommand=scroll_h.set)

        scroll_v.pack(side="right", fill="y")
        scroll_h.pack(side="bottom", fill="x")
        self.tableau.pack(side="left", fill="both", expand=True)

        # ─── Événements ───
        self.tableau.bind("<<TreeviewSelect>>", self._sur_selection_ligne)

        # Couleur alternée des lignes (pair / impair)
        self.tableau.tag_configure(
            "impair", background=theme.get("bg_secondaire")
        )
        self.tableau.tag_configure(
            "pair", background=theme.get("bg_input")
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — PANNEAU DE DÉTAIL LATÉRAL
    # ────────────────────────────────────────────────────────────

    def _construire_panneau_detail(self):
        """
        Construit le panneau de détail latéral (initialement masqué).
        Son contenu est rempli dynamiquement à chaque sélection de ligne.

        Retourne :
            None
        """
        # En-tête du panneau
        cadre_entete = tk.Frame(self.cadre_detail, bg=theme.get("bg_secondaire"))
        cadre_entete.pack(fill="x", pady=(0, PADDING_MOYEN))

        tk.Label(
            cadre_entete,
            text="Détail du paquet",
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_titre")
        ).pack(side="left")

        bouton_fermer = tk.Label(
            cadre_entete,
            text="✕",
            font=POLICE_SOUS_TITRE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire"),
            cursor="hand2"
        )
        bouton_fermer.pack(side="right")
        bouton_fermer.bind("<Button-1>", lambda e: self._fermer_panneau_detail())

        # Zone scrollable pour les champs
        cadre_scroll = tk.Frame(self.cadre_detail, bg=theme.get("bg_secondaire"))
        cadre_scroll.pack(fill="both", expand=True)

        self.canvas_detail = tk.Canvas(
            cadre_scroll,
            bg=theme.get("bg_secondaire"),
            highlightthickness=0
        )
        scroll_detail = ttk.Scrollbar(cadre_scroll, orient="vertical",
                                       command=self.canvas_detail.yview)
        self.canvas_detail.configure(yscrollcommand=scroll_detail.set)

        scroll_detail.pack(side="right", fill="y")
        self.canvas_detail.pack(side="left", fill="both", expand=True)

        # Frame intérieure du canvas (contenu des champs)
        self.cadre_champs_detail = tk.Frame(
            self.canvas_detail, bg=theme.get("bg_secondaire")
        )
        self._fenetre_canvas = self.canvas_detail.create_window(
            (0, 0), window=self.cadre_champs_detail, anchor="nw"
        )

        self.cadre_champs_detail.bind(
            "<Configure>",
            lambda e: self.canvas_detail.configure(
                scrollregion=self.canvas_detail.bbox("all")
            )
        )
        self.canvas_detail.bind(
            "<Configure>",
            lambda e: self.canvas_detail.itemconfig(
                self._fenetre_canvas, width=e.width
            )
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 7 — CHARGEMENT ET AFFICHAGE DES DONNÉES
    # ────────────────────────────────────────────────────────────

    def _charger_paquets(self):
        """
        Récupère les paquets depuis la base (avec filtres actifs si
        présents), vide le tableau et le remplit avec les nouvelles
        données. Affiche un état vide si aucune capture n'est active.

        Retourne :
            None
        """
        # Vider le tableau avant de le reremplir
        for item in self.tableau.get_children():
            self.tableau.delete(item)

        capture_id = self.controleur.capture_courante_id

        if capture_id is None:
            self.label_compteur.configure(
                text="Aucune capture active — sélectionnez une capture dans le tableau de bord."
            )
            return

        paquets = obtenir_paquets(capture_id, self._filtres_actifs or None)

        self.label_compteur.configure(
            text=f"{len(paquets)} paquet(s) affiché(s)"
        )

        for i, paquet in enumerate(paquets):
            tag = "pair" if i % 2 == 0 else "impair"
            valeurs = (
                paquet["numero"] or "",
                paquet["timestamp"] or "",
                paquet["ip_src"] or "",
                paquet["ip_dst"] or "",
                paquet["protocole"] or "",
                paquet["port_src"] or "",
                paquet["port_dst"] or "",
                paquet["taille"] or "",
                paquet["info"] or ""
            )
            # Stocker l'id SQLite dans iid pour le retrouver à la sélection
            self.tableau.insert(
                "", "end",
                iid=str(paquet["id"]),
                values=valeurs,
                tags=(tag,)
            )

        # Conserver la liste pour l'accès rapide au clic
        self._paquets_index = {str(p["id"]): p for p in paquets}

    # ────────────────────────────────────────────────────────────
    # SECTION 8 — SÉLECTION ET PANNEAU DE DÉTAIL
    # ────────────────────────────────────────────────────────────

    def _sur_selection_ligne(self, event):
        """
        Callback déclenché à chaque changement de sélection dans le
        Treeview. Récupère le paquet correspondant et ouvre le
        panneau de détail.

        Paramètres :
            event : Événement Tkinter (non utilisé directement)

        Retourne :
            None
        """
        selection = self.tableau.selection()
        if not selection:
            return

        paquet_id = selection[0]
        paquet = self._paquets_index.get(paquet_id)
        if paquet is None:
            return

        self._paquet_selectionne = paquet
        self._ouvrir_panneau_detail(paquet)

    def _ouvrir_panneau_detail(self, paquet):
        """
        Révèle le panneau de détail latéral (si masqué) et remplit
        ses champs avec les données du paquet sélectionné.

        Paramètres :
            paquet (sqlite3.Row) : Paquet à afficher en détail

        Retourne :
            None
        """
        # Remplir les champs avant de révéler le panneau
        self._remplir_champs_detail(paquet)

        if not self._panneau_detail_visible:
            self.cadre_detail.pack(side="left", fill="y",
                                   padx=(PADDING_MOYEN, 0))
            self._panneau_detail_visible = True

    def _fermer_panneau_detail(self):
        """
        Masque le panneau de détail latéral et désélectionne la
        ligne active dans le tableau.

        Retourne :
            None
        """
        self.cadre_detail.pack_forget()
        self._panneau_detail_visible = False
        self._paquet_selectionne = None

        for item in self.tableau.selection():
            self.tableau.selection_remove(item)

    def _remplir_champs_detail(self, paquet):
        """
        Vide et reconstruit le contenu du panneau de détail avec
        les champs du paquet passé en paramètre.

        Paramètres :
            paquet (sqlite3.Row) : Paquet dont les champs sont affichés

        Retourne :
            None
        """
        # Vider l'ancien contenu
        for widget in self.cadre_champs_detail.winfo_children():
            widget.destroy()

        # Définition des champs à afficher avec leur libellé
        champs = [
            ("Numéro",        paquet["numero"]),
            ("Horodatage",    paquet["timestamp"]),
            ("IP source",     paquet["ip_src"]),
            ("IP destination",paquet["ip_dst"]),
            ("Protocole",     paquet["protocole"]),
            ("Port source",   paquet["port_src"]),
            ("Port destination", paquet["port_dst"]),
            ("Taille (octets)", paquet["taille"]),
            ("Info",          paquet["info"]),
        ]

        for libelle, valeur in champs:
            cadre_champ = tk.Frame(
                self.cadre_champs_detail,
                bg=theme.get("bg_secondaire")
            )
            cadre_champ.pack(fill="x", pady=(0, PADDING_PETIT))

            tk.Label(
                cadre_champ,
                text=libelle,
                font=POLICE_PETIT,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_secondaire"),
                anchor="w"
            ).pack(anchor="w")

            tk.Label(
                cadre_champ,
                text=str(valeur) if valeur is not None else "—",
                font=POLICE_PETIT,
                bg=theme.get("bg_input"),
                fg=theme.get("texte_principal"),
                anchor="w",
                padx=6,
                pady=4,
                wraplength=250,
                justify="left"
            ).pack(fill="x")

        # Remettre le canvas en haut après reconstruction
        self.canvas_detail.yview_moveto(0)

    # ────────────────────────────────────────────────────────────
    # SECTION 9 — FILTRES
    # ────────────────────────────────────────────────────────────

    def _appliquer_filtres(self):
        """
        Lit les valeurs des champs de filtre, construit le dict
        de filtres et recharge le tableau.

        Retourne :
            None
        """
        filtres = {}

        ip_src = self.champ_ip_src.get().strip()
        if ip_src:
            filtres["ip_src"] = ip_src

        protocole = self.champ_protocole.get().strip().upper()
        if protocole:
            filtres["protocole"] = protocole

        port_dst = self.champ_port_dst.get().strip()
        if port_dst.isdigit():
            filtres["port_dst"] = int(port_dst)

        self._filtres_actifs = filtres
        self._charger_paquets()

        # Fermer le panneau de détail si ouvert (la sélection n'est plus valide)
        if self._panneau_detail_visible:
            self._fermer_panneau_detail()

    def _reinitialiser_filtres(self):
        """
        Vide les champs de filtre, réinitialise le dict de filtres
        actifs et recharge l'intégralité des paquets.

        Retourne :
            None
        """
        self.champ_ip_src.delete(0, "end")
        self.champ_protocole.delete(0, "end")
        self.champ_port_dst.delete(0, "end")

        self._filtres_actifs = {}
        self._charger_paquets()