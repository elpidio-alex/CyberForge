"""
════════════════════════════════════════════════════════════════
 gui/theme.py — Système de thèmes de l'application (clair / sombre)
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Centralise toutes les constantes visuelles de l'application
   sous forme de deux palettes (SOMBRE et CLAIR), avec une
   identité de marque commune : Violet (#7C3AED) + Ambre (#F59E0B).
   Fournit un objet Theme dynamique que les vues interrogent via
   theme.get("cle") plutôt que d'importer des constantes figées,
   ce qui permet de basculer le thème à chaud sans redémarrer.
════════════════════════════════════════════════════════════════
"""

# ════════════════════════════════════════════════════════════════
# SECTION 1 — COULEURS DE MARQUE (identiques dans les deux thèmes)
# ════════════════════════════════════════════════════════════════

# Ces deux couleurs définissent l'identité visuelle de CyberForge
# et ne changent pas entre le mode clair et le mode sombre
VIOLET_MARQUE = "#7C3AED"   # Couleur principale — actions, accents, liens actifs
AMBRE_MARQUE  = "#F59E0B"   # Couleur secondaire — alertes, mise en valeur, CTA

# Variantes de survol (hover) dérivées des couleurs de marque
VIOLET_HOVER  = "#8B5CF6"   # Violet légèrement éclairci au survol
AMBRE_HOVER   = "#FBBF24"   # Ambre légèrement éclairci au survol

# Couleurs sémantiques communes (criticité, statuts) — identiques
# dans les deux thèmes pour garder une lecture cohérente des alertes
COULEUR_SUCCES        = "#22C55E"   # Vert — succès, connexion OK
COULEUR_AVERTISSEMENT = AMBRE_MARQUE  # Ambre — criticité MOYENNE
COULEUR_DANGER        = "#EF4444"   # Rouge — criticité HAUTE, erreurs
COULEUR_INFO          = VIOLET_MARQUE  # Violet — criticité FAIBLE, informations


# ════════════════════════════════════════════════════════════════
# SECTION 2 — PALETTE MODE SOMBRE
# ════════════════════════════════════════════════════════════════

THEME_SOMBRE = {
    "nom": "sombre",

    # Fonds
    "bg_principal"   : "#0d1117",   # Fond principal de l'application
    "bg_secondaire"  : "#161b22",   # Fond des panneaux/cartes
    "bg_sidebar"     : "#010409",   # Fond de la barre latérale
    "bg_survol"      : "#21262d",   # Fond au survol d'un élément cliquable
    "bg_input"       : "#0d1117",   # Fond des champs de saisie

    # Textes
    "texte_principal"  : "#c9d1d9",  # Texte principal (gris clair)
    "texte_secondaire" : "#8b949e",  # Texte secondaire / labels discrets
    "texte_titre"      : "#f0f6fc",  # Titres en blanc quasi pur
    "texte_inverse"    : "#0d1117",  # Texte sur fond coloré (boutons)

    # Accents (identité de marque)
    "accent_principal" : VIOLET_MARQUE,
    "accent_hover"     : VIOLET_HOVER,
    "accent_secondaire": AMBRE_MARQUE,
    "accent_secondaire_hover": AMBRE_HOVER,

    # Bordures
    "bordure" : "#30363d",
}


# ════════════════════════════════════════════════════════════════
# SECTION 3 — PALETTE MODE CLAIR
# ════════════════════════════════════════════════════════════════

THEME_CLAIR = {
    "nom": "clair",

    # Fonds
    "bg_principal"   : "#FFFFFF",   # Fond principal blanc
    "bg_secondaire"  : "#F3F4F6",   # Fond des panneaux/cartes (gris très clair)
    "bg_sidebar"     : "#1F2937",   # Barre latérale volontairement foncée
                                     # pour ancrer visuellement la navigation
    "bg_survol"      : "#E5E7EB",   # Fond au survol d'un élément cliquable
    "bg_input"       : "#FFFFFF",   # Fond des champs de saisie

    # Textes
    "texte_principal"  : "#111827",  # Texte principal (gris très foncé)
    "texte_secondaire" : "#6B7280",  # Texte secondaire / labels discrets
    "texte_titre"      : "#0F172A",  # Titres en noir bleuté
    "texte_inverse"    : "#FFFFFF",  # Texte sur fond coloré (boutons)

    # Accents (identité de marque — mêmes couleurs, cohérence de marque)
    "accent_principal" : VIOLET_MARQUE,
    "accent_hover"     : VIOLET_HOVER,
    "accent_secondaire": AMBRE_MARQUE,
    "accent_secondaire_hover": AMBRE_HOVER,

    # Bordures
    "bordure" : "#D1D5DB",
}


# ════════════════════════════════════════════════════════════════
# SECTION 4 — CORRESPONDANCE CRITICITÉ → COULEUR
# ════════════════════════════════════════════════════════════════

# Indépendant du thème clair/sombre : les couleurs de criticité
# restent identiques pour ne jamais tromper l'utilisateur
COULEURS_CRITICITE = {
    "FAIBLE"  : COULEUR_INFO,
    "MOYENNE" : COULEUR_AVERTISSEMENT,
    "HAUTE"   : COULEUR_DANGER
}


# ════════════════════════════════════════════════════════════════
# SECTION 5 — POLICES (communes aux deux thèmes)
# ════════════════════════════════════════════════════════════════

POLICE_BASE = "Times New Roman"

POLICE_TITRE       = (POLICE_BASE, 22, "bold")
POLICE_SOUS_TITRE  = (POLICE_BASE, 14, "bold")
POLICE_TEXTE       = (POLICE_BASE, 11, "normal")
POLICE_TEXTE_GRAS  = (POLICE_BASE, 11, "bold")
POLICE_PETIT       = (POLICE_BASE, 9,  "normal")
POLICE_BOUTON      = (POLICE_BASE, 11, "bold")
POLICE_SIDEBAR     = (POLICE_BASE, 12, "normal")
POLICE_CHIFFRE_CLE = (POLICE_BASE, 28, "bold")


# ════════════════════════════════════════════════════════════════
# SECTION 6 — DIMENSIONS ET ESPACEMENTS (communs aux deux thèmes)
# ════════════════════════════════════════════════════════════════

LARGEUR_FENETRE   = 1280
HAUTEUR_FENETRE   = 800
LARGEUR_SIDEBAR   = 220

PADDING_GRAND     = 24
PADDING_MOYEN     = 16
PADDING_PETIT     = 8

EPAISSEUR_BORDURE = 1


# ════════════════════════════════════════════════════════════════
# SECTION 7 — GESTIONNAIRE DE THÈME DYNAMIQUE
# ════════════════════════════════════════════════════════════════

class GestionnaireTheme:
    """
    Objet central qui détient le thème actif (clair ou sombre) et
    permet aux vues de récupérer les couleurs courantes sans les
    coder en dur. Une seule instance est partagée dans toute
    l'application (voir gui/app.py).

    Utilisation typique dans une vue :
        couleur_fond = theme.get("bg_principal")
    """

    def __init__(self, mode_initial="sombre"):
        """
        Initialise le gestionnaire avec un mode de départ.

        Paramètres :
            mode_initial (str) : "sombre" ou "clair" (défaut : "sombre")

        Retourne :
            None
        """
        # Liste des abonnés (callbacks) à notifier lors d'un changement
        # de thème, typiquement les vues qui doivent se redessiner
        self._abonnes = []

        # Sélectionner la palette de départ
        self._palette_active = (
            THEME_SOMBRE if mode_initial == "sombre" else THEME_CLAIR
        )

    def get(self, cle):
        """
        Récupère une valeur de couleur depuis la palette active.

        Paramètres :
            cle (str) : Nom de la clé de couleur (ex: "bg_principal")

        Retourne :
            str : Code couleur hexadécimal correspondant
        """
        return self._palette_active[cle]

    def mode_actuel(self):
        """
        Retourne le nom du mode actuellement actif.

        Retourne :
            str : "sombre" ou "clair"
        """
        return self._palette_active["nom"]

    def est_sombre(self):
        """
        Indique si le thème actif est le mode sombre.

        Retourne :
            bool : True si mode sombre, False si mode clair
        """
        return self._palette_active["nom"] == "sombre"

    def basculer(self):
        """
        Bascule entre le mode sombre et le mode clair, puis notifie
        tous les abonnés (vues) pour qu'ils se redessinent avec les
        nouvelles couleurs.

        Retourne :
            None
        """
        # Inverser la palette active
        if self.est_sombre():
            self._palette_active = THEME_CLAIR
        else:
            self._palette_active = THEME_SOMBRE

        # Prévenir chaque vue abonnée que le thème a changé
        self._notifier_abonnes()

    def definir_mode(self, mode):
        """
        Force un mode de thème précis ("sombre" ou "clair").

        Paramètres :
            mode (str) : "sombre" ou "clair"

        Retourne :
            None
        """
        nouvelle_palette = THEME_SOMBRE if mode == "sombre" else THEME_CLAIR

        # Ne rien faire si le mode demandé est déjà actif (évite un
        # redessin inutile de toute l'interface)
        if nouvelle_palette["nom"] == self._palette_active["nom"]:
            return

        self._palette_active = nouvelle_palette
        self._notifier_abonnes()

    def abonner(self, callback):
        """
        Enregistre une fonction à appeler à chaque changement de thème.
        Utilisé par les vues Tkinter pour se redessiner automatiquement.

        Paramètres :
            callback (callable) : Fonction sans argument à appeler
                                  lors d'un changement de thème

        Retourne :
            None
        """
        self._abonnes.append(callback)

    def _notifier_abonnes(self):
        """
        Appelle tous les callbacks abonnés après un changement de thème.

        Retourne :
            None
        """
        for callback in self._abonnes:
            callback()


# ════════════════════════════════════════════════════════════════
# SECTION 8 — INSTANCE GLOBALE PARTAGÉE
# ════════════════════════════════════════════════════════════════

# Instance unique du gestionnaire de thème, importée par toutes les
# vues de l'application. Démarre en mode clair par défaut.
theme = GestionnaireTheme(mode_initial="clair")


# ════════════════════════════════════════════════════════════════
# SECTION 9 — FONCTIONS UTILITAIRES DE STYLE
# ════════════════════════════════════════════════════════════════

def obtenir_couleur_criticite(criticite):
    """
    Retourne la couleur associée à un niveau de criticité d'alerte.
    Indépendant du thème actif : une alerte HAUTE reste rouge
    en mode clair comme en mode sombre.

    Paramètres :
        criticite (str) : "FAIBLE", "MOYENNE" ou "HAUTE"

    Retourne :
        str : Code couleur hexadécimal correspondant.
              Retourne une couleur neutre si la criticité est inconnue.
    """
    return COULEURS_CRITICITE.get(criticite, "#8b949e")


def configurer_style_ttk(style):
    """
    Configure les styles ttk globaux (Treeview, Progressbar, etc.)
    selon le thème actuellement actif. À appeler à l'initialisation
    ET à chaque bascule de thème.

    Paramètres :
        style (ttk.Style) : Instance de style ttk à configurer

    Retourne :
        None
    """
    style.theme_use("clam")  # Thème de base neutre, nécessaire avant personnalisation

    # ─── Style du Treeview (packets_view, history_view) ───
    style.configure(
        "Treeview",
        background=theme.get("bg_secondaire"),
        foreground=theme.get("texte_principal"),
        fieldbackground=theme.get("bg_secondaire"),
        borderwidth=0,
        font=POLICE_TEXTE,
        rowheight=28
    )

    # En-têtes de colonnes du Treeview
    style.configure(
        "Treeview.Heading",
        background=theme.get("bg_sidebar"),
        foreground=theme.get("texte_titre") if theme.est_sombre() else "#FFFFFF",
        font=POLICE_TEXTE_GRAS,
        borderwidth=0
    )

    # Couleur de sélection dans le Treeview — violet de marque
    style.map(
        "Treeview",
        background=[("selected", theme.get("accent_principal"))],
        foreground=[("selected", theme.get("texte_inverse"))]
    )

    # ─── Style de la barre de progression (import_view) ───
    # Utilise l'ambre de marque pour se distinguer visuellement
    # du violet réservé aux actions/navigation
    style.configure(
        "Horizontal.TProgressbar",
        background=theme.get("accent_secondaire"),
        troughcolor=theme.get("bg_secondaire"),
        borderwidth=0,
        thickness=10
    )