"""
════════════════════════════════════════════════════════════════
 gui/sidebar.py — Barre latérale de navigation
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Affiche le menu de navigation permanent sur la gauche de la
   vue principale (MainView). Contient : logo/nom de l'app, liens
   vers chaque sous-vue (dashboard, import, paquets, alertes,
   historique, profil), bouton de bascule clair/sombre et bouton
   de déconnexion. Notifie MainView du lien cliqué via un callback.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk

from gui.theme import (
    theme,
    POLICE_TITRE,
    POLICE_SIDEBAR,
    POLICE_PETIT,
    LARGEUR_SIDEBAR,
    PADDING_MOYEN,
    PADDING_PETIT
)


# ════════════════════════════════════════════════════════════════
# SECTION 1 — DÉFINITION DES LIENS DE NAVIGATION
# ════════════════════════════════════════════════════════════════

# Chaque entrée : (nom_interne, libellé affiché, icône texte)
# Le nom_interne correspond à la clé utilisée dans MainView.naviguer_vers()
LIENS_NAVIGATION = [
    ("dashboard", "Tableau de bord", "📊"),
    ("import",    "Importer capture", "📥"),
    ("packets",   "Paquets",          "📦"),
    ("alerts",    "Alertes",          "🚨"),
    ("history",   "Historique",       "📜"),
    ("profile",   "Profil",           "👤"),
]


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CLASSE SIDEBAR
# ════════════════════════════════════════════════════════════════

class Sidebar(tk.Frame):
    """
    Barre latérale fixe affichant la navigation principale.
    Communique avec MainView via deux callbacks fournis au
    constructeur : on_navigation(nom_vue) et on_deconnexion().
    """

    def __init__(self, parent, on_navigation, on_deconnexion, sous_vue_active="dashboard"):
        """
        Construit la sidebar et tous ses widgets.

        Paramètres :
            parent          (tk.Widget) : Widget parent (MainView)
            on_navigation   (callable)  : Fonction appelée avec le nom
                                          de la sous-vue cliquée
            on_deconnexion  (callable)  : Fonction appelée au clic sur
                                          "Déconnexion"
            sous_vue_active (str)       : Nom de la sous-vue actuellement
                                          affichée, pour surligner le bon
                                          lien au chargement

        Retourne :
            None
        """
        # Largeur fixe pour que la sidebar ne bouge jamais entre les vues
        super().__init__(
            parent,
            bg=theme.get("bg_sidebar"),
            width=LARGEUR_SIDEBAR
        )
        # Empêcher le frame de se redimensionner selon son contenu
        self.pack_propagate(False)

        # Mémoriser les callbacks et l'état
        self.on_navigation   = on_navigation
        self.on_deconnexion  = on_deconnexion
        self.sous_vue_active = sous_vue_active

        # Dictionnaire pour retrouver chaque bouton de lien par son nom
        # (utile pour mettre à jour le surlignage du lien actif)
        self._boutons_liens = {}

        # Construction de l'interface, dans l'ordre visuel de haut en bas
        self._construire_logo()
        self._construire_liens_navigation()
        self._construire_pied_sidebar()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — LOGO / EN-TÊTE
    # ────────────────────────────────────────────────────────────

    def _construire_logo(self):
        """
        Affiche le nom de l'application en haut de la sidebar,
        avec la police de titre Cambria définie dans le thème.

        Retourne :
            None
        """
        cadre_logo = tk.Frame(self, bg=theme.get("bg_sidebar"))
        cadre_logo.pack(fill="x", pady=(PADDING_MOYEN * 2, PADDING_MOYEN))

        # Nom de l'application — utilise la police de titre (Cambria)
        # et l'ambre de marque pour se démarquer visuellement
        label_nom = tk.Label(
            cadre_logo,
            text="CyberForge",
            font=POLICE_TITRE,
            bg=theme.get("bg_sidebar"),
            fg=theme.get("accent_secondaire")  # Ambre — identité de marque
        )
        label_nom.pack(padx=PADDING_MOYEN, anchor="w")

        # Sous-titre discret sous le nom
        label_sous_titre = tk.Label(
            cadre_logo,
            text="Superviseur réseau",
            font=POLICE_PETIT,
            bg=theme.get("bg_sidebar"),
            fg=theme.get("texte_secondaire")
        )
        label_sous_titre.pack(padx=PADDING_MOYEN, anchor="w")

        # Séparateur visuel sous le logo
        separateur = tk.Frame(self, bg=theme.get("bordure"), height=1)
        separateur.pack(fill="x", pady=(PADDING_MOYEN, 0))

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — LIENS DE NAVIGATION
    # ────────────────────────────────────────────────────────────

    def _construire_liens_navigation(self):
        """
        Crée un bouton cliquable pour chaque entrée de LIENS_NAVIGATION.
        Le lien correspondant à sous_vue_active est surligné au violet
        de marque dès la construction.

        Retourne :
            None
        """
        cadre_liens = tk.Frame(self, bg=theme.get("bg_sidebar"))
        cadre_liens.pack(fill="x", pady=PADDING_MOYEN)

        for nom_interne, libelle, icone in LIENS_NAVIGATION:
            bouton = self._creer_bouton_lien(cadre_liens, nom_interne, libelle, icone)
            bouton.pack(fill="x", padx=PADDING_PETIT, pady=2)
            self._boutons_liens[nom_interne] = bouton

        # Appliquer le surlignage initial sur le lien actif
        self._mettre_a_jour_surlignage()

    def _creer_bouton_lien(self, parent, nom_interne, libelle, icone):
        """
        Construit un bouton de navigation individuel sous forme de
        Label cliquable (plus facile à styler qu'un tk.Button natif).

        Paramètres :
            parent      (tk.Widget) : Conteneur des liens
            nom_interne (str)       : Identifiant de la sous-vue ciblée
            libelle     (str)       : Texte affiché à l'utilisateur
            icone       (str)       : Émoji/symbole affiché avant le texte

        Retourne :
            tk.Label : Le widget bouton créé (cliquable)
        """
        bouton = tk.Label(
            parent,
            text=f"  {icone}   {libelle}",
            font=POLICE_SIDEBAR,
            bg=theme.get("bg_sidebar"),
            fg=theme.get("texte_principal") if theme.est_sombre() else "#E5E7EB",
            anchor="w",
            padx=PADDING_MOYEN,
            pady=10,
            cursor="hand2"  # Curseur "main" pour signaler la clicabilité
        )

        # Lier le clic à la navigation vers cette sous-vue
        bouton.bind("<Button-1>", lambda e, n=nom_interne: self._sur_clic_lien(n))

        # Effet de survol : léger changement de fond, sauf si le lien
        # est déjà celui actif (pour ne pas brouiller le surlignage)
        bouton.bind("<Enter>", lambda e, n=nom_interne: self._sur_survol(n, True))
        bouton.bind("<Leave>", lambda e, n=nom_interne: self._sur_survol(n, False))

        return bouton

    def _sur_clic_lien(self, nom_interne):
        """
        Gère le clic sur un lien de navigation : met à jour l'état
        interne, rafraîchit le surlignage et notifie MainView.

        Paramètres :
            nom_interne (str) : Nom de la sous-vue cliquée

        Retourne :
            None
        """
        # Ne rien faire si on clique sur le lien déjà actif
        if nom_interne == self.sous_vue_active:
            return

        self.sous_vue_active = nom_interne
        self._mettre_a_jour_surlignage()

        # Déléguer l'affichage réel de la sous-vue à MainView
        self.on_navigation(nom_interne)

    def _sur_survol(self, nom_interne, entree):
        """
        Applique ou retire l'effet de survol sur un bouton de lien,
        sauf s'il s'agit du lien actuellement actif (déjà surligné).

        Paramètres :
            nom_interne (str)  : Nom du lien survolé
            entree      (bool) : True à l'entrée de la souris, False à la sortie

        Retourne :
            None
        """
        # Le lien actif garde toujours son fond violet, pas d'effet de survol
        if nom_interne == self.sous_vue_active:
            return

        bouton = self._boutons_liens[nom_interne]
        if entree:
            bouton.configure(bg=theme.get("bg_survol"))
        else:
            bouton.configure(bg=theme.get("bg_sidebar"))

    def _mettre_a_jour_surlignage(self):
        """
        Reparcourt tous les boutons de lien et applique le style
        "actif" (fond violet, texte blanc) uniquement au lien
        correspondant à sous_vue_active ; les autres reprennent
        le style neutre de la sidebar.

        Retourne :
            None
        """
        for nom_interne, bouton in self._boutons_liens.items():
            if nom_interne == self.sous_vue_active:
                # Lien actif : fond violet de marque, texte blanc
                bouton.configure(
                    bg=theme.get("accent_principal"),
                    fg="#FFFFFF"
                )
            else:
                # Lien inactif : couleurs neutres de la sidebar
                bouton.configure(
                    bg=theme.get("bg_sidebar"),
                    fg=theme.get("texte_principal") if theme.est_sombre() else "#E5E7EB"
                )

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — PIED DE SIDEBAR (thème + déconnexion)
    # ────────────────────────────────────────────────────────────

    def _construire_pied_sidebar(self):
        """
        Affiche en bas de la sidebar le bouton de bascule de thème
        et le bouton de déconnexion.

        Retourne :
            None
        """
        cadre_pied = tk.Frame(self, bg=theme.get("bg_sidebar"))
        cadre_pied.pack(side="bottom", fill="x", pady=PADDING_MOYEN)

        # Séparateur au-dessus du pied de sidebar
        separateur = tk.Frame(self, bg=theme.get("bordure"), height=1)
        separateur.pack(side="bottom", fill="x")

        # ─── Bouton de bascule clair/sombre ───
        icone_theme = "☀️ Mode clair" if theme.est_sombre() else "🌙 Mode sombre"
        self.bouton_theme = tk.Label(
            cadre_pied,
            text=f"  {icone_theme}",
            font=POLICE_SIDEBAR,
            bg=theme.get("bg_sidebar"),
            fg=theme.get("accent_secondaire"),  # Ambre pour le distinguer des liens
            anchor="w",
            padx=PADDING_MOYEN,
            pady=8,
            cursor="hand2"
        )
        self.bouton_theme.pack(fill="x", padx=PADDING_PETIT)
        self.bouton_theme.bind("<Button-1>", lambda e: theme.basculer())

        # ─── Bouton de déconnexion ───
        bouton_deconnexion = tk.Label(
            cadre_pied,
            text="  🚪  Déconnexion",
            font=POLICE_SIDEBAR,
            bg=theme.get("bg_sidebar"),
            fg=theme.get("texte_secondaire"),
            anchor="w",
            padx=PADDING_MOYEN,
            pady=8,
            cursor="hand2"
        )
        bouton_deconnexion.pack(fill="x", padx=PADDING_PETIT)
        bouton_deconnexion.bind("<Button-1>", lambda e: self.on_deconnexion())