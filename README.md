# 🩺 DermaVision — Plateforme IA de Détection du Cancer de la Peau

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-Keras-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_API-LLaMA_3.1-00C853?style=for-the-badge)

**DermaVision** est une application web intelligente d'aide au diagnostic dermatologique, utilisant un modèle de Deep Learning (VGG16) pour classifier les lésions cutanées en **Bénin** ou **Malin**, accompagnée d'un assistant IA conversationnel.

</div>

---

## 📋 Table des Matières

- [Présentation du Projet](#-présentation-du-projet)
- [Fonctionnalités](#-fonctionnalités)
- [Architecture Technique](#-architecture-technique)
- [Technologies Utilisées](#-technologies-utilisées)
- [Structure du Projet](#-structure-du-projet)
- [Prérequis](#-prérequis)
- [Installation & Configuration](#-installation--configuration)
- [Base de Données](#-base-de-données)
- [Utilisation](#-utilisation)
- [Captures d'Écran](#-captures-décran)
- [Auteurs](#-auteurs)

---

## 🎯 Présentation du Projet

DermaVision est un **Projet de Fin d'Année (PFA)** qui vise à assister les professionnels de la santé dans le dépistage précoce du cancer de la peau. L'application combine :

- Un modèle de **classification d'images** basé sur l'architecture **VGG16** (Deep Learning)
- Un **assistant IA conversationnel** (chatbot) propulsé par l'API **Groq** (modèle LLaMA 3.1)
- Une interface web **moderne et responsive** pour la gestion complète des patients

Le modèle IA analyse les images dermoscopiques et fournit une probabilité de malignité, permettant aux médecins de prioriser les cas critiques.

---

## ✨ Fonctionnalités

### 🔐 1. Authentification & Gestion des Utilisateurs
| Fonctionnalité | Description |
|---|---|
| **Inscription (Sign Up)** | Création de compte avec validation robuste (nom, prénom, email, identifiant, rôle) |
| **Connexion (Login)** | Authentification sécurisée par identifiant et mot de passe |
| **Gestion des sessions** | Sessions Flask pour maintenir l'état de connexion de l'utilisateur |
| **Redirection automatique** | Si l'utilisateur n'existe pas, redirection vers la page d'inscription |
| **Validation du mot de passe** | Au moins 8 caractères, majuscule, minuscule, chiffre et caractère spécial |
| **Déconnexion** | Nettoyage complet de la session |

### 🏠 2. Page d'Accueil (Landing Page)
| Fonctionnalité | Description |
|---|---|
| **Design premium** | Interface élégante avec animations CSS, gradients et effets de glassmorphisme |
| **Section Hero** | Présentation visuelle dynamique avec animations de scan |
| **Section À Propos** | Explication de la technologie et de la méthodologie utilisée |
| **Section Fonctionnalités** | Présentation des 6 fonctionnalités clés avec des cartes interactives |
| **Appel à l'action (CTA)** | Boutons d'accès rapide vers la connexion et l'inscription |
| **Responsive Design** | Adaptation à toutes les tailles d'écran (mobile, tablette, desktop) |

### 📊 3. Tableau de Bord (Dashboard)
| Fonctionnalité | Description |
|---|---|
| **Vue d'ensemble** | Affichage des KPIs : nombre de patients, analyses effectuées, cas critiques |
| **Patients prioritaires** | Liste des 3 patients les plus critiques (Malin ou probabilité ≥ 50%), triés par score |
| **Système de notifications** | Alertes en temps réel pour les cas nécessitant une attention urgente |
| **Accès rapide** | Cartes d'action vers les principales fonctionnalités (analyse, patients, stats, chatbot) |
| **Barre latérale (Sidebar)** | Navigation intuitive avec indicateurs visuels de la section active |
| **Profil utilisateur** | Affichage du nom et du rôle de l'utilisateur connecté |

### 🔬 4. Prédiction IA (Analyse Dermoscopique)
| Fonctionnalité | Description |
|---|---|
| **Upload d'image** | Téléchargement d'images de lésions cutanées (formats image standard) |
| **Classification IA** | Modèle VGG16 pré-entraîné classifiant en **Bénin** ou **Malin** |
| **Score de confiance** | Probabilité en pourcentage de la prédiction du modèle |
| **Prétraitement** | Redimensionnement automatique (224×224 pixels) et normalisation |
| **Sauvegarde automatique** | Enregistrement du patient, du résultat et de l'image en base de données |
| **Formulaire patient** | Collecte du nom, âge et email du patient |

### 👥 5. Gestion des Patients
| Fonctionnalité | Description |
|---|---|
| **Liste complète** | Tableau récapitulatif de tous les patients analysés |
| **Diagnostic visuel** | Badges colorés (vert/rouge) pour identifier rapidement les cas bénins/malins |
| **Score IA** | Barre de progression visuelle du score de confiance |
| **Aperçu d'image** | Miniature de la lésion analysée dans le tableau |
| **Tri chronologique** | Patients triés par date d'ajout (les plus récents en premier) |
| **Informations de contact** | Affichage de l'email pour le suivi des patients |
| **✏️ Modifier un patient** | Formulaire d'édition pré-rempli pour modifier le nom, l'âge et l'email d'un patient |
| **🗑️ Supprimer un patient** | Suppression d'un patient avec confirmation JavaScript et nettoyage de l'image uploadée |
| **Boutons d'actions** | Chaque ligne du tableau contient des boutons Modifier, Historique et Supprimer |

### 📜 6. Historique d'Analyses par Patient
| Fonctionnalité | Description |
|---|---|
| **Vue timeline** | Affichage chronologique de toutes les analyses effectuées pour un même patient |
| **Statistiques résumées** | Cartes de synthèse : nombre total d'analyses, cas bénins, cas malins, score moyen |
| **Détails par analyse** | Pour chaque analyse : date, résultat IA, score de confiance, aperçu de l'image |
| **Indicateurs visuels** | Points colorés (vert/rouge) sur la timeline pour distinguer les résultats |
| **Barres de progression** | Animation des scores de confiance pour chaque analyse |
| **Recherche par nom** | L'historique regroupe automatiquement toutes les analyses d'un même nom de patient |

### 📈 7. Statistiques & Graphiques
| Fonctionnalité | Description |
|---|---|
| **Statistiques globales** | Total patients, cas bénins, cas malins, confiance moyenne |
| **Graphique Doughnut** | Visualisation interactive de la répartition Bénin/Malin (Chart.js) |
| **Cartes de stats** | Affichage visuel avec icônes et compteurs animés |

### 🤖 8. Assistant IA (Chatbot — DermaAssist)
| Fonctionnalité | Description |
|---|---|
| **Chatbot intelligent** | Assistant conversationnel propulsé par l'API Groq (LLaMA 3.1 8B) |
| **Contexte médical** | Connaissance en dermatologie et oncologie cutanée |
| **Accès aux données patients** | Peut analyser et commenter les résultats des patients enregistrés |
| **Recommandations** | Suggestions de suivi médical basées sur les résultats IA |
| **Widget flottant** | Bulle de chat accessible depuis le dashboard |
| **Interface dédiée** | Page chatbot complète avec historique de conversation |

### 📧 9. Envoi d'Emails Automatiques
| Fonctionnalité | Description |
|---|---|
| **Convocation automatique** | Email de convocation pour les patients à risque (résultat Malin) |
| **SMTP Gmail** | Envoi via le serveur SMTP de Gmail avec TLS |
| **Configuration sécurisée** | Identifiants email stockés dans un fichier `.env` |
| **Vérification** | Contrôle de l'existence de l'email du patient avant envoi |

### ⚙️ 10. Paramètres du Compte
| Fonctionnalité | Description |
|---|---|
| **Modification du profil** | Mise à jour de l'identifiant et du rôle |
| **Changement de mot de passe** | Vérification de l'ancien mot de passe avant la mise à jour |
| **Validation** | Vérification de l'unicité de l'identifiant |

### ❓ 11. Page d'Aide (FAQ)
| Fonctionnalité | Description |
|---|---|
| **FAQ interactive** | Accordéon avec les questions fréquentes |
| **Guide d'utilisation** | Explications pour chaque fonctionnalité de la plateforme |
| **Support technique** | Carte de contact avec lien mailto pour l'assistance |

---

## 🏗 Architecture Technique

```
┌─────────────────────────────────────────────────────┐
│                   NAVIGATEUR WEB                     │
│          (HTML / CSS / JS / Chart.js)                │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (GET/POST)
                       ▼
┌─────────────────────────────────────────────────────┐
│               SERVEUR FLASK (app.py)                 │
│  ┌────────────┐ ┌──────────────┐ ┌───────────────┐  │
│  │   Routes   │ │   Sessions   │ │  Flash Msgs   │  │
│  └────────────┘ └──────────────┘ └───────────────┘  │
└────┬──────────────┬───────────────────┬─────────────┘
     │              │                   │
     ▼              ▼                   ▼
┌──────────┐  ┌───────────┐    ┌───────────────┐
│  MySQL   │  │  VGG16    │    │  Groq API     │
│  (BDD)   │  │  (Model)  │    │  (Chatbot)    │
│          │  │  .h5 file  │    │  LLaMA 3.1   │
└──────────┘  └───────────┘    └───────────────┘
```

---

## 🛠 Technologies Utilisées

| Catégorie | Technologie | Version / Détail |
|---|---|---|
| **Backend** | Python + Flask | Python 3.9+, Flask 2.x |
| **IA / Deep Learning** | TensorFlow / Keras | Modèle VGG16 pré-entraîné |
| **Chatbot** | Groq API | Modèle LLaMA 3.1 8B Instant |
| **Base de données** | MySQL | Via `mysql-connector-python` |
| **Frontend** | HTML5 / CSS3 / JavaScript | Bootstrap 5.3, Chart.js |
| **Icônes** | Bootstrap Icons + Font Awesome | v1.10.5 / v6.4.0 |
| **Polices** | Google Fonts | DM Sans, Syne, Playfair Display |
| **Email** | SMTP (Gmail) | smtplib + email.mime |
| **Env. Variables** | python-dotenv | Fichier `.env` |

---

## 📁 Structure du Projet

```
SKIN_CANCER_APP/
│
├── app.py                          # Application principale Flask (routes, logique métier)
│
├── model/
│   └── vgg16_malignant_vs_benign.h5  # Modèle VGG16 pré-entraîné (~136 Mo)
│
├── static/
│   ├── style.css                   # Feuille de styles globale
│   ├── images/                     # Images statiques (logos, illustrations)
│   └── uploads/                    # Images de lésions uploadées par les utilisateurs
│
├── templates/
│   ├── landing.html                # Page d'accueil publique
│   ├── login.html                  # Page de connexion
│   ├── signup.html                 # Page d'inscription
│   ├── dashboard.html              # Tableau de bord principal
│   ├── predict.html                # Formulaire d'analyse IA
│   ├── result.html                 # Page de résultat d'analyse
│   ├── patients.html               # Liste des patients (avec actions Modifier/Supprimer/Historique)
│   ├── edit_patient.html           # Formulaire de modification d'un patient
│   ├── patient_history.html        # Historique des analyses d'un patient (timeline)
│   ├── stats.html                  # Page de statistiques et graphiques
│   ├── chatbot.html                # Interface du chatbot IA
│   ├── settings.html               # Paramètres du compte
│   ├── help.html                   # Page d'aide / FAQ
│   └── .env                        # Variables d'environnement (clés API, credentials)
│
├── PHPMailer/                      # (Module optionnel pour l'envoi d'emails)
├── venv/                           # Environnement virtuel Python
│
└── README.md                       # Ce fichier
```

---

## 📦 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python** 3.9 ou supérieur → [Télécharger Python](https://www.python.org/downloads/)
- **MySQL Server** (XAMPP, WAMP ou MySQL standalone) → [Télécharger XAMPP](https://www.apachefriends.org/)
- **pip** (gestionnaire de paquets Python, inclus avec Python)
- **Git** (optionnel, pour cloner le dépôt)

---

## 🚀 Installation & Configuration

### Étape 1 : Cloner le projet

```bash
git clone https://github.com/votre-repo/SKIN_CANCER_APP.git
cd SKIN_CANCER_APP
```

### Étape 2 : Créer un environnement virtuel

```bash
python -m venv venv
```

Activation :
- **Windows** : `venv\Scripts\activate`
- **Linux/Mac** : `source venv/bin/activate`

### Étape 3 : Installer les dépendances

```bash
pip install flask tensorflow mysql-connector-python python-dotenv groq numpy
```

### Étape 3.5 : Télécharger et placer le modèle IA

Le modèle de prédiction (`vgg16_malignant_vs_benign.h5`) étant supérieur à 100 Mo, il est ignoré par Git.
1. Téléchargez le fichier du modèle.
2. Créez un dossier nommé `model` à la racine du projet (s'il n'existe pas).
3. Placez-y le fichier pour obtenir la structure suivante : `model/vgg16_malignant_vs_benign.h5`.

### Étape 4 : Configurer la base de données

1. Démarrez votre serveur MySQL (via XAMPP ou autre)
2. Créez la base de données :

```sql
CREATE DATABASE skin_cancer_db;
USE skin_cancer_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    role VARCHAR(100) DEFAULT 'Médecin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    email VARCHAR(255),
    result VARCHAR(50),
    probability FLOAT,
    image_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Étape 5 : Configurer les variables d'environnement

Éditez le fichier `templates/.env` :

```env
GROQ_API_KEY=votre_cle_api_groq
EMAIL_USER=votre_adresse@gmail.com
EMAIL_PASS=votre_mot_de_passe_application
```

> **Note :** Pour Gmail, utilisez un [mot de passe d'application](https://support.google.com/accounts/answer/185833) et non votre mot de passe principal.

### Étape 6 : Lancer l'application

```bash
python app.py
```

L'application sera accessible à l'adresse : **http://127.0.0.1:5000**

---

## 🗄 Base de Données

### Diagramme des tables

```
┌──────────────────────┐        ┌──────────────────────┐
│       users          │        │      patients         │
├──────────────────────┤        ├──────────────────────┤
│ id (PK, AUTO_INCR)   │        │ id (PK, AUTO_INCR)   │
│ username (UNIQUE)     │        │ name                 │
│ password              │        │ age                  │
│ first_name            │        │ email                │
│ last_name             │        │ result               │
│ email (UNIQUE)        │        │ probability          │
│ role                  │        │ image_path           │
│ created_at            │        │ created_at           │
└──────────────────────┘        └──────────────────────┘
```

---

## 📖 Utilisation

### Workflow Principal

1. **Accéder** à la page d'accueil → `http://127.0.0.1:5000`
2. **Créer un compte** ou se **connecter**
3. **Accéder au dashboard** pour voir les KPIs et les patients prioritaires
4. **Nouvelle Analyse** : uploader une image dermoscopique → obtenir la prédiction IA
5. **Consulter la liste des patients** avec leurs résultats
6. **Modifier / Supprimer** un patient depuis les boutons d'action du tableau
7. **Consulter l'historique** d'un patient pour voir l'évolution de ses analyses dans le temps
8. **Envoyer un email** de convocation pour les patients à risque
9. **Utiliser le chatbot** pour obtenir des recommandations médicales
10. **Consulter les statistiques** pour une vue globale des diagnostics

---

## 👨‍💻 Auteurs

| Rôle | Nom |
|---|---|
| **Développeur** | LOBNA |
| **Encadrant** | [Nom du professeur] |

---

## 📄 Licence

Ce projet est réalisé dans le cadre académique (Projet de Fin d'Année). Toute reproduction ou utilisation commerciale est soumise à autorisation.

---

<div align="center">

**⚠️ Avertissement Médical**

*DermaVision est un outil d'aide au diagnostic et ne remplace en aucun cas l'avis d'un dermatologue qualifié. Les résultats fournis par l'IA doivent toujours être confirmés par un examen clinique professionnel.*

</div>
