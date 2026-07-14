"""
════════════════════════════════════════════════════════════════
 gui/app.py — Fenêtre principale et orchestrateur de l'application
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Point d'entrée graphique de l'application. Crée la fenêtre
   Tkinter principale, gère la navigation entre les vues (login,
   dashboard, import, paquets, alertes, historique, profil) et
   maintient l'état global (utilisateur connecté, capture active).
   Utilise exclusivement Tkinter/ttk — aucune dépendance externe.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import ttk

# Import du gestionnaire de thème et des constantes visuelles
from gui.theme import (
    theme,
    configurer_style_ttk,
    LARGEUR_FENETRE,
    HAUTEUR_FENETRE
)

# Import des vues (chaque vue est une classe Frame Tkinter)
from gui.login_view import LoginView
from gui.main_view import MainView


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE PRINCIPALE DE L'APPLICATION
# ════════════════════════════════════════════════════════════════

class CyberForgeApp(tk.Tk):
    """
    Fenêtre racine de l'application CyberForge. Hérite de tk.Tk
    pour être directement la fenêtre principale. Gère :
      - L'état global (utilisateur connecté, capture sélectionnée)
      - La navigation entre la vue de connexion et la vue principale
      - L'application du thème (clair/sombre) à toute l'application
    """

    def __init__(self):
        """
        Initialise la fenêtre principale, configure ses dimensions,
        son titre, son style ttk, puis affiche la vue de connexion.

        Retourne :
            None
        """
        super().__init__()  # Initialisation standard de tk.Tk

        # ─── Configuration de la fenêtre ───
        self.title("CyberForge — Superviseur de captures réseau")
        self.geometry(f"{LARGEUR_FENETRE}x{HAUTEUR_FENETRE}")
        self.minsize(1024, 700)  # Taille minimale pour garder une UI lisible

        # ─── État global de l'application ───
        # Ces attributs sont partagés entre toutes les vues via self.controleur
        self.utilisateur_courant = None   # Row SQLite de l'utilisateur connecté
        self.capture_courante_id = None   # ID de la capture actuellement affichée

        # ─── Style ttk (Treeview, Progressbar) selon le thème actif ───
        self.style_ttk = ttk.Style(self)
        configurer_style_ttk(self.style_ttk)

        # Appliquer la couleur de fond de la fenêtre selon le thème
        self.configure(bg=theme.get("bg_principal"))

        # S'abonner aux changements de thème pour redessiner la fenêtre
        theme.abonner(self._sur_changement_theme)

        # ─── Conteneur qui accueillera la vue active ───
        # On utilise un seul conteneur et on détruit/recrée la vue
        # affichée à chaque navigation (plus simple qu'un système
        # de stacked frames pour un projet de cette taille)
        self.conteneur = tk.Frame(self, bg=theme.get("bg_principal"))
        self.conteneur.pack(fill="both", expand=True)

        self.vue_active = None  # Référence vers la vue Frame actuellement affichée

        # ─── Démarrage : afficher la vue de connexion ───
        self.afficher_login()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — NAVIGATION ENTRE VUES
    # ────────────────────────────────────────────────────────────

    def _vider_conteneur(self):
        """
        Détruit la vue actuellement affichée dans le conteneur
        avant d'en afficher une nouvelle. Évite l'accumulation
        de widgets invisibles en mémoire.

        Retourne :
            None
        """
        if self.vue_active is not None:
            self.vue_active.destroy()
            self.vue_active = None

    def afficher_login(self):
        """
        Affiche la vue de connexion/inscription. Appelée au
        démarrage de l'application et après une déconnexion.

        Retourne :
            None
        """
        self._vider_conteneur()

        # La vue de login reçoit une référence à l'app (self) pour
        # pouvoir déclencher la navigation vers la vue principale
        # une fois la connexion réussie (callback on_connexion_reussie)
        self.vue_active = LoginView(
            self.conteneur,
            controleur=self
        )
        self.vue_active.pack(fill="both", expand=True)

    def afficher_application_principale(self, utilisateur):
        """
        Affiche la vue principale (avec sidebar + dashboard) après
        une connexion réussie.

        Paramètres :
            utilisateur (sqlite3.Row) : Utilisateur qui vient de se
                                        connecter, retourné par auth.py

        Retourne :
            None
        """
        # Mémoriser l'utilisateur connecté dans l'état global
        self.utilisateur_courant = utilisateur

        self._vider_conteneur()

        # MainView orchestre elle-même la sidebar et les sous-vues
        # (dashboard, import, paquets, alertes, historique, profil)
        self.vue_active = MainView(
            self.conteneur,
            controleur=self
        )
        self.vue_active.pack(fill="both", expand=True)

    def deconnecter(self):
        """
        Déconnecte l'utilisateur courant : réinitialise l'état
        global et revient à la vue de connexion.

        Retourne :
            None
        """
        # Journaliser la déconnexion avant de perdre la référence utilisateur
        if self.utilisateur_courant is not None:
            from history_log import log_deconnexion
            log_deconnexion(self.utilisateur_courant["id"])

        # Réinitialiser l'état global
        self.utilisateur_courant = None
        self.capture_courante_id = None

        # Retour à l'écran de connexion
        self.afficher_login()

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — GESTION DU THÈME
    # ────────────────────────────────────────────────────────────

    def _sur_changement_theme(self):
        """
        Callback appelé automatiquement par le GestionnaireTheme
        (gui/theme.py) à chaque bascule clair/sombre. Reconfigure
        le style ttk et le fond de la fenêtre, puis redessine
        entièrement la vue active pour appliquer les nouvelles
        couleurs (les vues Tkinter ne mettent pas à jour leurs
        couleurs automatiquement).

        Retourne :
            None
        """
        # Reconfigurer le style ttk avec la nouvelle palette
        configurer_style_ttk(self.style_ttk)

        # Mettre à jour le fond de la fenêtre et du conteneur
        self.configure(bg=theme.get("bg_principal"))
        self.conteneur.configure(bg=theme.get("bg_principal"))

        # Redessiner entièrement la vue active pour appliquer le thème
        # (on la reconstruit plutôt que de tenter de reconfigurer
        # chaque widget individuellement — plus simple et plus fiable)
        if isinstance(self.vue_active, MainView):
            # Rester sur la même sous-vue après le redessin si possible
            sous_vue_active = self.vue_active.nom_sous_vue_active
            self.afficher_application_principale(self.utilisateur_courant)
            self.vue_active.naviguer_vers(sous_vue_active)
        elif self.vue_active is not None:
            self.afficher_login()


# ════════════════════════════════════════════════════════════════
# SECTION 4 — POINT D'ENTRÉE (si lancé directement pour test)
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Ce bloc permet de tester gui/app.py isolément, mais l'entrée
    # normale de l'application reste main.py à la racine du projet
    from db import initialiser_bd

    initialiser_bd()  # S'assurer que les tables existent

    app = CyberForgeApp()
    app.mainloop()