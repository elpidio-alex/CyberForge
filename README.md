# CyberForge

**Superviseur de captures réseau — Détection d'intrusions basée sur l'analyse heuristique de trafic**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-Academic-lightgrey)
![Status](https://img.shields.io/badge/status-Projet%20académique-orange)

---

## Sommaire

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Architecture du projet](#architecture-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Format des captures supportées](#format-des-captures-supportées)
- [Moteur de détection (IDS)](#moteur-de-détection-ids)
- [Modèle de données](#modèle-de-données)
- [Sécurité](#sécurité)
- [Configuration](#configuration)
- [Auteur](#auteur)

---

## Présentation

**CyberForge** est une application de bureau développée en Python permettant d'importer, d'analyser et de superviser des captures réseau exportées depuis **Wireshark** (format texte). L'application applique un ensemble de règles heuristiques configurables pour détecter des comportements réseau suspects (flood/DoS, scans de ports, protocoles anormaux, accès à des ports sensibles, etc.) et génère des alertes classées par niveau de criticité.

Le projet a été réalisé dans le cadre du cours **CSC 242 — Algorithmique avancée & Programmation Orientée Objet**, à l'**iPNet Institute of Technology** (Lomé, Togo).

---

## Fonctionnalités

- 🔐 **Authentification sécurisée** — inscription et connexion utilisateur avec hachage des mots de passe via `bcrypt`
- 📥 **Import de captures** — analyse de fichiers `.txt` exportés depuis Wireshark
- 📊 **Tableau de bord** — vue synthétique des statistiques de trafic
- 🚨 **Détection d'intrusions (IDS)** — 5 règles heuristiques configurables
- 📦 **Exploration des paquets** — visualisation détaillée des paquets capturés
- 🔎 **Analyse des flux** — agrégation des conversations entre IPs
- 🕘 **Historique des actions** — traçabilité des imports, suppressions et connexions
- 👤 **Gestion de profil** — modification des informations personnelles et du mot de passe
- 🎨 **Interface graphique native** — Tkinter/ttk avec thème sombre/clair
- 💾 **Persistance locale** — stockage SQLite embarqué, aucune dépendance à un serveur externe

---

## Architecture du projet

```
CyberForge/
├── main.py                  # Point d'entrée de l'application
├── auth.py                  # Authentification (inscription, connexion, profil)
├── db.py                    # Couche d'accès aux données (SQLite)
├── parser.py                # Parsing des exports Wireshark (.txt)
├── ids.py                   # Moteur de détection d'intrusions (règles heuristiques)
├── history_log.py           # Journalisation des actions utilisateur
├── config.json               # Configuration de l'application et des seuils IDS
├── requirements.txt          # Dépendances Python
├── cyberforge.db              # Base de données SQLite (générée automatiquement)
├── assets/
│   ├── icon.ico
│   └── logo.png
└── gui/
    ├── app.py                # Fenêtre principale et orchestrateur de navigation
    ├── login_view.py          # Vue de connexion / inscription
    ├── dashboard_view.py       # Tableau de bord
    ├── import_view.py          # Import de captures
    ├── packets_view.py         # Exploration des paquets
    ├── alerts_view.py           # Visualisation des alertes IDS
    ├── history_view.py          # Historique des actions
    ├── profile_view.py          # Gestion du profil utilisateur
    ├── sidebar.py               # Barre de navigation latérale
    └── theme.py                  # Thème visuel (couleurs, polices, styles ttk)
```

---

## Prérequis

- **Python 3.10** ou supérieur
- **pip** (gestionnaire de paquets Python)
- Système d'exploitation : Windows, macOS ou Linux (Tkinter inclus nativement avec Python)

---

## Installation

1. **Cloner ou extraire le projet**

```bash
git clone https://github.com/elpidio-alex/CyberForge.git
cd CyberForge
```

2. **Créer un environnement virtuel** *(recommandé)*

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. **Installer les dépendances**

```bash
pip install -r requirements.txt
```

4. **Lancer l'application**

```bash
python main.py
```

> La base de données SQLite (`cyberforge.db`) et ses tables sont créées automatiquement au premier lancement.

---

## Utilisation

1. Lancer l'application via `python main.py`
2. Créer un compte utilisateur ou se connecter
3. Importer une capture réseau au format `.txt` (export Wireshark)
4. Consulter le tableau de bord, les paquets, les flux et les alertes générées automatiquement
5. Retrouver l'historique complet des actions dans l'onglet dédié

---

## Format des captures supportées

CyberForge attend un export **Wireshark** au format texte brut (`.txt`), obtenu via *File → Export Packet Dissections → As Plain Text* ou équivalent, avec les colonnes suivantes :

```
No.   Time        Source          Destination     Protocol   Length   Info
1     0.000000    192.168.1.1     8.8.8.8         DNS        74       Standard query
```

Chaque paquet est parsé et normalisé en un enregistrement contenant : numéro, timestamp, IP source, IP destination, protocole, ports source/destination, taille et informations complémentaires.

---

## Moteur de détection (IDS)

Le module `ids.py` applique cinq règles heuristiques, avec seuils configurables dans `config.json` :

| Règle | Détection | Criticité |
|---|---|---|
| **Flood / DoS** | Volume excessif de paquets envoyés par une même IP source | Faible → Haute (selon dépassement) |
| **Scan de ports** | Une IP source contacte un nombre anormal de ports distincts sur une même IP destination | Moyenne / Haute |
| **Paquets volumineux** | Taille de paquet dépassant le seuil configuré | Faible |
| **Protocoles suspects** | Volume élevé de trafic ICMP, ARP ou DNS depuis une même IP | Moyenne |
| **Ports sensibles** | Tentatives répétées vers des ports critiques (SSH, RDP, MySQL, etc.) | Haute |

Chaque alerte générée contient : type, criticité, IP source/destination, description et horodatage, puis est persistée en base pour consultation ultérieure.

---

## Modèle de données

La base SQLite embarquée comprend six tables principales :

- `utilisateurs` — comptes et mots de passe hachés
- `captures` — métadonnées des fichiers importés
- `paquets` — détail de chaque paquet parsé
- `flux` — conversations agrégées entre paires d'IPs
- `alertes` — résultats du moteur IDS
- `historique` — journal des actions utilisateur (connexions, imports, suppressions)

---

## Sécurité

- Les mots de passe ne sont **jamais stockés en clair** : hachage via `bcrypt` avec sel aléatoire (`bcrypt.gensalt()`)
- Vérification systématique de l'unicité des emails à l'inscription
- Contrôle de longueur minimale (6 caractères) sur les mots de passe
- Toute modification sensible (mot de passe, profil) requiert une revalidation des identifiants

---

## Configuration

Le fichier `config.json` centralise l'ensemble des paramètres ajustables :

```json
{
  "ids": {
    "seuil_paquets_par_ip": 500,
    "seuil_ports_scannes": 20,
    "seuil_taille_paquet": 9000,
    "protocoles_suspects": ["ICMP", "ARP", "DNS"],
    "ports_sensibles": [22, 23, 80, 443, 3306, 3389, 8080]
  },
  "parser": {
    "encodage": "utf-8",
    "max_paquets": 100000
  }
}
```

Ces seuils peuvent être ajustés sans modifier le code source, afin d'adapter la sensibilité de la détection au contexte réseau analysé.

---

## Auteur

**Elpidio Alexis AMOUSSOU**
iPNet Institute of Technology — Lomé, Togo
Cours : CSC 242 — Algorithmique avancée & Programmation Orientée Objet

---

*CyberForge est un projet académique développé à des fins pédagogiques dans le cadre de l'apprentissage de la programmation orientée objet et des concepts fondamentaux de la cybersécurité réseau.*
```