# 🎾 Corpo Padel - Gestion de Tournois

Application complète pour la gestion de tournois corporatifs de padel, centralisant la gestion des événements, des matchs, des résultats et des plannings.

## 🛠 Technologies
- **Backend** : FastAPI (Python), SQLAlchemy, SQLite.
- **Frontend** : Vue.js 3, Pinia, TailwindCSS.
- **Tests** : Pytest (Backend), Cypress (Frontend E2E).

## 🚀 Installation et Lancement

### 1. Backend (API)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt

# Copier les variables d'environnement (si nécessaire)
cp .env.example .env

# Initialiser la base de données
python3 -c "from app.database import init_db; init_db()"

# Lancer le serveur
uvicorn app.main:app --reload
```
Le backend sera accessible sur `http://localhost:8000`.

### 2. Frontend (Interface)
```bash
cd frontend
npm install

# Copier les variables d'environnement
cp .env.example .env

# Lancer le serveur de développement
npm run dev
```
L'application sera accessible sur `http://localhost:5173`.

## 🧪 Exécution des Tests

Ce projet intègre une suite de tests automatisés pour garantir la stabilité du backend et du frontend.

### ✅ Méthode Automatique (Script Global)

Le moyen le plus simple de vérifier l'ensemble du projet :
```bash
# Depuis la racine du projet
chmod +x auto_tests/run.sh  # (Une seule fois si nécessaire)
./auto_tests/run.sh
```
Ce script lance les tests backend (Pytest) puis les tests frontend (Cypress) et affiche un rapport global.

### 🐍 Tests Backend (Pytest)

Pour exécuter manuellement les tests de l'API :
```bash
cd backend
# Activer l'environnement virtuel si ce n'est pas déjà fait
source venv/bin/activate

# Lancer tous les tests
pytest

# Lancer un fichier de test spécifique
pytest tests/test_matches.py
```

### 🌲 Tests Frontend (Cypress)

Pour exécuter manuellement les tests d'interface :
```bash
cd frontend

# Lancer tous les tests en mode console (Headless)
npx cypress run

# Ouvrir l'interface interactive de Cypress pour le débogage
npx cypress open
```

## ✨ Fonctionnalités
- **Authentification Sécurisée** : Connexion JWT, protection anti-brute force.
- **Gestion des Matchs** : Saisie des scores, validation des formats, historique.
- **Planning** : Vue d'ensemble des événements et des disponibilités.
- **Résultats** : Tableaux des scores et mises à jour en temps réel.
- **Administration** : Gestion des utilisateurs et configuration globale.

## 🔐 Identifiants de Démonstration

Un compte administrateur est pré-configuré pour tester l'application :
- **Email** : `admin@padel.com`
- **Mot de passe** : `Test@2025_2026`

## 📞 Support

Pour plus de détails techniques, consultez les fichiers `README.md` spécifiques dans les dossiers `backend/` et `frontend/`.
