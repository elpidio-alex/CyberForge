"""
════════════════════════════════════════════════════════════════
 gui/main_view.py — Vue principale (sidebar + zone de contenu)
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Orchestre l'affichage après connexion : place la Sidebar à
   gauche et une zone de contenu à droite qui héberge la sous-vue
   active (dashboard, import, paquets, alertes, historique,
   profil). Gère la navigation entre sous-vues et expose
   l'interface attendue par gui/app.py (nom_sous_vue_active,
   naviguer_vers) pour survivre à un changement de thème.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk

from gui.theme import theme
from gui.sidebar import Sidebar

# Import des sous-vues (chacune est un Frame Tkinter)
from gui.dashboard_view import DashboardView
from gui.import_view import ImportView
from gui.packets_view import PacketsView
from gui.alerts_view import AlertsView
from gui.history_view import HistoryView
from gui.profile_view import ProfileView


# ════════════════════════════════════════════════════════════════
# SECTION 1 — REGISTRE DES SOUS-VUES
# ════════════════════════════════════════════════════════════════

# Associe chaque nom interne de navigation (utilisé par la Sidebar)
# à la classe Frame correspondante. Permet d'instancier dynamiquement
# la bonne sous-vue sans longue chaîne de if/elif.
CLASSES_SOUS_VUES = {
    "dashboard": DashboardView,
    "import":    ImportView,
    "packets":   PacketsView,
    "alerts":    AlertsView,
    "history":   HistoryView,
    "profile":   ProfileView,
}


# ════════════════════════════════════════════════════════════════
# SECTION 2 — CLASSE MAINVIEW
# ════════════════════════════════════════════════════════════════

class MainView(tk.Frame):
    """
    Conteneur principal affiché après une connexion réussie.
    Structure horizontale : Sidebar (fixe, à gauche) + zone de
    contenu (à droite) qui accueille la sous-vue active.
    """

    def __init__(self, parent, controleur):
        """
        Construit la sidebar et affiche le dashboard par défaut.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (CyberForgeApp.conteneur)
            controleur (CyberForgeApp)  : Fenêtre principale, pour accéder à
                                          l'état global (utilisateur_courant,
                                          capture_courante_id) et pour se
                                          déconnecter/naviguer

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur

        # Nom de la sous-vue actuellement affichée — lu par app.py
        # après un changement de thème pour rester sur la même page
        self.nom_sous_vue_active = "dashboard"

        # Référence vers l'instance de sous-vue actuellement affichée
        self.sous_vue_active = None

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — CONSTRUCTION DE LA STRUCTURE GÉNÉRALE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Crée la Sidebar et la zone de contenu, puis affiche la
        sous-vue initiale (dashboard).

        Retourne :
            None
        """
        # ─── Sidebar à gauche ───
        self.sidebar = Sidebar(
            self,
            on_navigation=self.naviguer_vers,
            on_deconnexion=self._sur_deconnexion,
            sous_vue_active=self.nom_sous_vue_active
        )
        self.sidebar.pack(side="left", fill="y")

        # ─── Zone de contenu à droite ───
        # Un Frame conteneur qui accueillera la sous-vue active ;
        # on détruit/recrée son contenu à chaque navigation
        self.zone_contenu = tk.Frame(self, bg=theme.get("bg_principal"))
        self.zone_contenu.pack(side="left", fill="both", expand=True)

        # Afficher la sous-vue initiale
        self._afficher_sous_vue(self.nom_sous_vue_active)

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — NAVIGATION ENTRE SOUS-VUES
    # ────────────────────────────────────────────────────────────

    def naviguer_vers(self, nom_sous_vue):
        """
        Change la sous-vue affichée dans la zone de contenu. Appelée
        par la Sidebar au clic sur un lien, et par gui/app.py après
        un changement de thème pour revenir sur la même page.

        Paramètres :
            nom_sous_vue (str) : Nom interne de la sous-vue cible
                                 (clé de CLASSES_SOUS_VUES)

        Retourne :
            None
        """
        self.nom_sous_vue_active = nom_sous_vue
        self._afficher_sous_vue(nom_sous_vue)

    def _afficher_sous_vue(self, nom_sous_vue):
        """
        Détruit la sous-vue actuellement affichée (le cas échéant)
        et instancie la nouvelle sous-vue correspondant à nom_sous_vue.

        Paramètres :
            nom_sous_vue (str) : Nom interne de la sous-vue à afficher

        Retourne :
            None
        """
        # Détruire l'ancienne sous-vue pour éviter l'accumulation
        # de widgets invisibles en mémoire
        if self.sous_vue_active is not None:
            self.sous_vue_active.destroy()
            self.sous_vue_active = None

        # Récupérer la classe correspondant au nom demandé
        classe_vue = CLASSES_SOUS_VUES.get(nom_sous_vue, DashboardView)

        # Chaque sous-vue reçoit le contrôleur (CyberForgeApp) pour
        # accéder à l'utilisateur connecté, la capture active, etc.
        self.sous_vue_active = classe_vue(
            self.zone_contenu,
            controleur=self.controleur
        )
        self.sous_vue_active.pack(fill="both", expand=True)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — DÉCONNEXION
    # ────────────────────────────────────────────────────────────

    def _sur_deconnexion(self):
        """
        Callback transmis à la Sidebar : délègue la déconnexion
        réelle au contrôleur (CyberForgeApp.deconnecter), qui gère
        la journalisation et le retour à l'écran de connexion.

        Retourne :
            None
        """
        self.controleur.deconnecter()