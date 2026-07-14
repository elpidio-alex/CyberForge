"""
════════════════════════════════════════════════════════════════
 gui/import_view.py — Vue d'importation de capture Wireshark
 Projet    : CyberForge — Superviseur de captures réseau
 Auteur    : Elpidio Alexis AMOUSSOU
 Institut  : iPNet Institute of Technology, Lomé - Togo
 Cours     : CSC 242 — Algorithmique avancée & POO
────────────────────────────────────────────────────────────────
 Rôle :
   Permet à l'utilisateur de sélectionner un fichier .txt exporté
   de Wireshark, de lancer son parsing (parser.py) avec une barre
   de progression, de calculer les flux, d'exécuter l'analyse IDS
   (ids.py), puis d'insérer paquets/flux/alertes en base (db.py).
   Une fois l'import terminé, définit la nouvelle capture comme
   capture active (controleur.capture_courante_id) et journalise
   l'action (history_log.py). Le traitement lourd s'exécute dans
   un thread séparé pour ne pas geler l'interface Tkinter.
════════════════════════════════════════════════════════════════
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

from gui.theme import (
    theme,
    POLICE_TITRE,
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

from parser import parser_fichier, calculer_flux, preparer_paquets_bd, preparer_flux_bd
from ids import analyser_capture, preparer_alertes_bd
from db import creer_capture, inserer_paquets, inserer_flux, inserer_alertes, mettre_a_jour_stats_capture
from history_log import log_import_capture


# ════════════════════════════════════════════════════════════════
# SECTION 1 — CLASSE IMPORTVIEW
# ════════════════════════════════════════════════════════════════

class ImportView(tk.Frame):
    """
    Vue permettant d'importer un fichier de capture Wireshark
    (.txt), de suivre sa progression, puis d'afficher un résumé
    du résultat (nb paquets, nb alertes par criticité).
    """

    def __init__(self, parent, controleur):
        """
        Construit la vue d'import.

        Paramètres :
            parent     (tk.Widget)      : Conteneur parent (MainView.zone_contenu)
            controleur (CyberForgeApp)  : Fenêtre principale, pour lire
                                          utilisateur_courant et écrire
                                          capture_courante_id après import

        Retourne :
            None
        """
        super().__init__(parent, bg=theme.get("bg_principal"))

        self.controleur = controleur
        self.utilisateur = controleur.utilisateur_courant

        # Chemin du fichier sélectionné par l'utilisateur (avant import)
        self.chemin_fichier = None

        # Indique si un import est en cours, pour désactiver les
        # boutons et éviter un double lancement
        self.import_en_cours = False

        self._construire_interface()

    # ────────────────────────────────────────────────────────────
    # SECTION 2 — CONSTRUCTION DE L'INTERFACE
    # ────────────────────────────────────────────────────────────

    def _construire_interface(self):
        """
        Construit l'en-tête, la zone de sélection de fichier, la
        barre de progression et la zone de résumé (masquée au départ).

        Retourne :
            None
        """
        cadre_principal = tk.Frame(self, bg=theme.get("bg_principal"))
        cadre_principal.pack(fill="both", expand=True, padx=PADDING_GRAND, pady=PADDING_GRAND)

        label_titre = tk.Label(
            cadre_principal,
            text="Importer une capture",
            font=POLICE_TITRE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_titre")
        )
        label_titre.pack(anchor="w")

        label_sous_titre = tk.Label(
            cadre_principal,
            text="Sélectionnez un export Wireshark au format texte (.txt) "
                 "pour l'analyser et détecter d'éventuelles anomalies réseau.",
            font=POLICE_TEXTE,
            bg=theme.get("bg_principal"),
            fg=theme.get("texte_secondaire"),
            wraplength=700,
            justify="left"
        )
        label_sous_titre.pack(anchor="w", pady=(0, PADDING_GRAND))

        # ─── Carte de sélection / lancement d'import ───
        self.carte = tk.Frame(
            cadre_principal,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_GRAND,
            pady=PADDING_GRAND
        )
        self.carte.pack(fill="x")

        self._construire_zone_selection()

        # ─── Zone de résumé, construite dynamiquement après import ───
        self.cadre_resume = tk.Frame(cadre_principal, bg=theme.get("bg_principal"))
        self.cadre_resume.pack(fill="both", expand=True, pady=(PADDING_MOYEN, 0))

    def _construire_zone_selection(self):
        """
        Affiche le bouton de sélection de fichier, le nom du
        fichier choisi, le bouton de lancement d'import et la
        barre de progression (masquée tant que l'import n'a pas
        démarré).

        Retourne :
            None
        """
        bouton_parcourir = tk.Label(
            self.carte,
            text="📁  Choisir un fichier .txt",
            font=POLICE_BOUTON,
            bg=theme.get("accent_principal"),
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_MOYEN,
            pady=PADDING_PETIT
        )
        bouton_parcourir.pack(anchor="w")
        bouton_parcourir.bind("<Button-1>", lambda e: self._choisir_fichier())

        self.label_fichier = tk.Label(
            self.carte,
            text="Aucun fichier sélectionné.",
            font=POLICE_TEXTE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        )
        self.label_fichier.pack(anchor="w", pady=(PADDING_MOYEN, PADDING_PETIT))

        # Barre de progression ttk, masquée tant qu'aucun import n'est lancé
        self.barre_progression = ttk.Progressbar(
            self.carte,
            style="Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.label_progression = tk.Label(
            self.carte,
            text="",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_secondaire")
        )

        self.bouton_lancer = tk.Label(
            self.carte,
            text="Lancer l'analyse",
            font=POLICE_BOUTON,
            bg=theme.get("accent_secondaire"),
            fg="#FFFFFF",
            cursor="hand2",
            padx=PADDING_MOYEN,
            pady=PADDING_PETIT
        )
        # Le bouton n'est affiché (pack) qu'une fois un fichier choisi
        self.bouton_lancer.bind("<Button-1>", lambda e: self._lancer_import())

        self.label_message = tk.Label(
            self.carte,
            text="",
            font=POLICE_PETIT,
            bg=theme.get("bg_secondaire"),
            wraplength=600,
            justify="left"
        )

    # ────────────────────────────────────────────────────────────
    # SECTION 3 — SÉLECTION DU FICHIER
    # ────────────────────────────────────────────────────────────

    def _choisir_fichier(self):
        """
        Ouvre une boîte de dialogue système pour choisir un fichier
        .txt, met à jour l'affichage et révèle le bouton de lancement.

        Retourne :
            None
        """
        if self.import_en_cours:
            return  # Ne rien faire si un import est déjà en cours

        chemin = filedialog.askopenfilename(
            title="Sélectionner un export Wireshark",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )

        if not chemin:
            return  # L'utilisateur a annulé la sélection

        self.chemin_fichier = chemin

        # Afficher uniquement le nom du fichier, pas le chemin complet
        nom_fichier = chemin.split("/")[-1].split("\\")[-1]
        self.label_fichier.configure(
            text=f"Fichier sélectionné : {nom_fichier}",
            fg=theme.get("texte_principal")
        )

        # Révéler le bouton de lancement (masqué jusqu'ici)
        self.bouton_lancer.pack(anchor="w", pady=(0, PADDING_MOYEN))

        # Réinitialiser un éventuel message précédent
        self.label_message.configure(text="")
        self.label_message.pack_forget()

    # ────────────────────────────────────────────────────────────
    # SECTION 4 — LANCEMENT DE L'IMPORT (EN ARRIÈRE-PLAN)
    # ────────────────────────────────────────────────────────────

    def _lancer_import(self):
        """
        Démarre le traitement complet (parsing, calcul de flux,
        analyse IDS, insertion en base) dans un thread séparé pour
        ne pas bloquer l'interface graphique pendant les fichiers
        volumineux.

        Retourne :
            None
        """
        if self.import_en_cours or not self.chemin_fichier:
            return

        self.import_en_cours = True

        # Désactiver les interactions et afficher la barre de progression
        self.bouton_lancer.configure(
            text="Analyse en cours...",
            bg=theme.get("texte_secondaire"),
            cursor="watch"
        )
        self.bouton_lancer.unbind("<Button-1>")

        self.barre_progression.pack(fill="x", pady=(0, PADDING_PETIT))
        self.barre_progression["value"] = 0

        self.label_progression.configure(text="Démarrage de l'analyse...")
        self.label_progression.pack(anchor="w")

        # Lancer le traitement lourd dans un thread pour ne pas geler l'UI
        thread = threading.Thread(target=self._traiter_import, daemon=True)
        thread.start()

    def _traiter_import(self):
        """
        Exécute le pipeline complet d'import dans un thread séparé :
        parsing, calcul des flux, analyse IDS, insertion en base.
        Chaque mise à jour de l'interface est replanifiée sur le
        thread principal via self.after() (Tkinter n'est pas
        thread-safe).

        Retourne :
            None
        """
        try:
            # ─── 1. Parsing du fichier avec suivi de progression ───
            def callback_progression(index, total):
                pourcentage = int((index / total) * 70) if total else 0
                self.after(0, self._mettre_a_jour_progression, pourcentage,
                           f"Parsing des paquets... ({index}/{total})")

            paquets = parser_fichier(self.chemin_fichier, callback_progression)

            if not paquets:
                self.after(0, self._afficher_erreur_import,
                           "Aucun paquet valide n'a pu être extrait de ce fichier.")
                return

            # ─── 2. Calcul des flux ───
            self.after(0, self._mettre_a_jour_progression, 75, "Calcul des flux réseau...")
            flux_list = calculer_flux(paquets)

            # ─── 3. Analyse IDS ───
            self.after(0, self._mettre_a_jour_progression, 85, "Analyse IDS en cours...")
            alertes = analyser_capture(paquets)

            # ─── 4. Création de la capture et insertion en base ───
            self.after(0, self._mettre_a_jour_progression, 90, "Enregistrement en base de données...")

            nom_fichier = self.chemin_fichier.split("/")[-1].split("\\")[-1]
            capture_id = creer_capture(self.utilisateur["id"], nom_fichier)

            inserer_paquets(preparer_paquets_bd(paquets, capture_id))
            inserer_flux(preparer_flux_bd(flux_list, capture_id))
            inserer_alertes(preparer_alertes_bd(alertes, capture_id))

            mettre_a_jour_stats_capture(capture_id, len(paquets), len(alertes))

            # ─── 5. Journalisation ───
            log_import_capture(self.utilisateur["id"], nom_fichier, len(paquets))

            self.after(0, self._mettre_a_jour_progression, 100, "Analyse terminée.")

            # ─── 6. Finalisation sur le thread principal ───
            self.after(0, self._finaliser_import, capture_id, nom_fichier,
                      len(paquets), len(flux_list), alertes)

        except FileNotFoundError as e:
            self.after(0, self._afficher_erreur_import, str(e))
        except Exception as e:
            self.after(0, self._afficher_erreur_import,
                       f"Erreur inattendue lors de l'analyse : {e}")

    def _mettre_a_jour_progression(self, pourcentage, message):
        """
        Met à jour la barre de progression et son label (appelé
        via self.after() depuis le thread de traitement).

        Paramètres :
            pourcentage (int) : Valeur de 0 à 100
            message     (str) : Texte décrivant l'étape en cours

        Retourne :
            None
        """
        self.barre_progression["value"] = pourcentage
        self.label_progression.configure(text=message)

    # ────────────────────────────────────────────────────────────
    # SECTION 5 — FINALISATION ET RÉSUMÉ
    # ────────────────────────────────────────────────────────────

    def _finaliser_import(self, capture_id, nom_fichier, nb_paquets, nb_flux, alertes):
        """
        Définit la nouvelle capture comme capture active, réinitialise
        le formulaire de sélection et affiche un résumé chiffré du
        résultat de l'analyse.

        Paramètres :
            capture_id  (int)        : ID de la capture créée
            nom_fichier (str)        : Nom du fichier importé
            nb_paquets  (int)        : Nombre de paquets extraits
            nb_flux     (int)        : Nombre de flux calculés
            alertes     (list[dict]) : Alertes détectées par l'IDS

        Retourne :
            None
        """
        # La capture importée devient automatiquement la capture active
        self.controleur.capture_courante_id = capture_id

        self.import_en_cours = False

        # Réinitialiser la zone de sélection pour un futur import
        self.chemin_fichier = None
        self.label_fichier.configure(text="Aucun fichier sélectionné.", fg=theme.get("texte_secondaire"))
        self.bouton_lancer.pack_forget()
        self.barre_progression.pack_forget()
        self.label_progression.pack_forget()

        # Afficher le résumé de l'import dans cadre_resume
        self._afficher_resume(nom_fichier, nb_paquets, nb_flux, alertes)

    def _afficher_resume(self, nom_fichier, nb_paquets, nb_flux, alertes):
        """
        Construit une carte de résumé après un import réussi :
        nombre de paquets/flux, répartition des alertes par
        criticité, et un lien pour consulter les alertes en détail.

        Paramètres :
            nom_fichier (str)        : Nom du fichier importé
            nb_paquets  (int)        : Nombre de paquets extraits
            nb_flux     (int)        : Nombre de flux calculés
            alertes     (list[dict]) : Alertes détectées par l'IDS

        Retourne :
            None
        """
        # Vider un éventuel résumé précédent
        for widget in self.cadre_resume.winfo_children():
            widget.destroy()

        # Compter les alertes par criticité pour l'affichage
        nb_haute   = sum(1 for a in alertes if a["criticite"] == "HAUTE")
        nb_moyenne = sum(1 for a in alertes if a["criticite"] == "MOYENNE")
        nb_faible  = sum(1 for a in alertes if a["criticite"] == "FAIBLE")

        carte_resume = tk.Frame(
            self.cadre_resume,
            bg=theme.get("bg_secondaire"),
            padx=PADDING_GRAND,
            pady=PADDING_GRAND
        )
        carte_resume.pack(fill="x")

        tk.Label(
            carte_resume,
            text=f"✅ Analyse de « {nom_fichier} » terminée",
            font=POLICE_TEXTE_GRAS,
            bg=theme.get("bg_secondaire"),
            fg=COULEUR_SUCCES
        ).pack(anchor="w")

        tk.Label(
            carte_resume,
            text=(
                f"{nb_paquets} paquets analysés  •  {nb_flux} flux détectés  •  "
                f"{len(alertes)} alertes générées"
            ),
            font=POLICE_TEXTE,
            bg=theme.get("bg_secondaire"),
            fg=theme.get("texte_principal")
        ).pack(anchor="w", pady=(PADDING_PETIT, PADDING_MOYEN))

        if alertes:
            tk.Label(
                carte_resume,
                text=(
                    f"🔴 {nb_haute} critique(s)   "
                    f"🟠 {nb_moyenne} moyenne(s)   "
                    f"🔵 {nb_faible} faible(s)"
                ),
                font=POLICE_TEXTE,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_principal")
            ).pack(anchor="w", pady=(0, PADDING_MOYEN))

            lien_alertes = tk.Label(
                carte_resume,
                text="Voir le détail des alertes →",
                font=POLICE_TEXTE_GRAS,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("accent_principal"),
                cursor="hand2"
            )
            lien_alertes.pack(anchor="w")
            lien_alertes.bind("<Button-1>", lambda e: self._aller_vers_alertes())
        else:
            tk.Label(
                carte_resume,
                text="Aucune anomalie détectée sur cette capture. 👍",
                font=POLICE_TEXTE,
                bg=theme.get("bg_secondaire"),
                fg=theme.get("texte_secondaire")
            ).pack(anchor="w")

    def _aller_vers_alertes(self):
        """
        Redirige l'utilisateur vers la vue Alertes en passant par
        la Sidebar de MainView (remonte de deux niveaux dans la
        hiérarchie de widgets : ImportView → zone_contenu → MainView).

        Retourne :
            None
        """
        main_view = self.master.master  # zone_contenu.master = MainView
        main_view.naviguer_vers("alerts")
        main_view.sidebar.sous_vue_active = "alerts"
        main_view.sidebar._mettre_a_jour_surlignage()

    # ────────────────────────────────────────────────────────────
    # SECTION 6 — GESTION DES ERREURS
    # ────────────────────────────────────────────────────────────

    def _afficher_erreur_import(self, message):
        """
        Réactive le formulaire d'import et affiche un message
        d'erreur après un échec de traitement.

        Paramètres :
            message (str) : Message d'erreur à afficher

        Retourne :
            None
        """
        self.import_en_cours = False

        self.bouton_lancer.configure(
            text="Lancer l'analyse",
            bg=theme.get("accent_secondaire"),
            cursor="hand2"
        )
        self.bouton_lancer.bind("<Button-1>", lambda e: self._lancer_import())

        self.barre_progression.pack_forget()
        self.label_progression.pack_forget()

        self.label_message.configure(text=f"❌ {message}", fg=COULEUR_DANGER)
        self.label_message.pack(anchor="w", pady=(PADDING_PETIT, 0))