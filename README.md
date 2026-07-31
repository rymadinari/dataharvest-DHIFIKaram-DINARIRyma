# DataHarvest

Framework de scraping modulaire, générique et configurable développé dans le cadre du projet final de **Web Scraping**.

**Master Dev, Data & IA – 4ème année**  
**IPSSI Nice**

---

# Auteurs

- **Karam DHIFI**
- **Ryma DINARI**

---

# Présentation

**DataHarvest** est un framework Python conçu pour automatiser l'extraction de données depuis des sites web HTML statiques.

Contrairement à un script de scraping classique développé pour un seul site, DataHarvest repose sur une architecture modulaire où chaque composant possède une responsabilité précise.

Grâce à un fichier de configuration **YAML ou JSON**, il est possible d'adapter le framework à un nouveau site sans modifier le code source.

L'objectif principal est de proposer un outil :

- réutilisable ;
- extensible ;
- configurable ;
- facilement maintenable.

---

# Fonctionnalités

DataHarvest propose les fonctionnalités suivantes :

- Chargement de configuration YAML ou JSON
- Téléchargement des pages avec Requests
- Gestion des middlewares
- Logging des requêtes HTTP
- Retry automatique avec backoff exponentiel
- Pagination configurable
- Extraction HTML avec sélecteurs CSS
- Validation des données collectées
- Stockage multi-format :
  - SQLite
  - JSON
  - CSV
- Export entre différents formats
- Interface CLI avec argparse
- Architecture modulaire orientée composants
- Tests unitaires avec Pytest

---

# Architecture du framework

```
                 Configuration YAML
                         |
                         v

                 +---------------+
                 |    Config     |
                 +---------------+
                         |
                         v

                 +---------------+
                 | Orchestrator  |
                 +---------------+
                   /     |      \
                  /      |       \
                 v       v        v

             Fetcher  Pipeline  Validator
                 |
                 v

          Middleware Chain

          - LoggingMiddleware
          - RetryMiddleware
          - RateLimitMiddleware
          
                 |
                 v

               Store
```

---

# Structure du projet

```
dataharvest/

├── dataharvest/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── fetcher.py
│   ├── middleware.py
│   ├── orchestrator.py
│   ├── pipeline.py
│   ├── store.py
│   └── validator.py
│
├── configs/
│
├── tests/
│
├── output/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

# Architecture des composants

## Config

Le composant **Config** est responsable du chargement et de la validation des fichiers de configuration.

Responsabilités :

- Lecture des fichiers YAML/JSON
- Vérification des clés obligatoires
- Mise à disposition des paramètres du scraping

---

## Fetcher

Le **Fetcher** gère la récupération des pages web.

Fonctionnalités :

- Requêtes HTTP avec Requests
- Gestion du User-Agent
- Utilisation des middlewares
- Gestion automatique des erreurs
- Retry avec backoff exponentiel

---

## Pipeline

Le **Pipeline** transforme le HTML brut en données structurées.

Implémentations disponibles :

- `GenericPipeline`
- `PaginationPipeline`

Il utilise les sélecteurs CSS définis dans les fichiers YAML.

---

## Validator

Le **Validator** vérifie la qualité des données extraites.

Contrôles réalisés :

- Présence des champs obligatoires
- Validation des URLs
- Vérification de longueur minimale
- Rejet des données invalides

---

## Store

Le composant **Store** permet la sauvegarde des résultats.

Backends supportés :

- SQLite
- JSON
- CSV

Il permet également l'export entre différents formats.

---

# Installation

## Cloner le projet

```bash
git clone <url-du-repository>
cd dataharvest
```

## Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# Utilisation

## Scraper un site

Exemple avec Books To Scrape :

```bash
python -m dataharvest crawl --config configs/books_toscrape.yaml
```

---

## Mode Dry Run

Le mode `--dry-run` permet de tester l'extraction sans enregistrer les résultats.

```bash
python -m dataharvest crawl --config configs/books_toscrape.yaml --dry-run
```

---

## Vérifier une configuration

```bash
python -m dataharvest validate --config configs/books_toscrape.yaml
```

---

## Exporter les données

Exemple SQLite vers CSV :

```bash
python -m dataharvest export \
--from output/books.db \
--to output/books.csv
```

---

# Sites testés

DataHarvest a été testé sur plusieurs sites présentant différents niveaux de difficulté.

| Site | Niveau | Données extraites | Stockage |
|---|---|---|---|
| books.toscrape.com | Niveau 1 | Livres, prix, disponibilité | SQLite |
| quotes.toscrape.com | Niveau 1 | Citations, auteurs, tags | JSON |
| fr.wikipedia.org | Niveau 2 | Données structurées | JSON |
| blogdumoderateur.com | Niveau 3 | Articles, dates, catégories | SQLite |
| github.com/trending | Niveau 4 | Dépôts, langages, étoiles | CSV |

Cette diversité permet de démontrer que DataHarvest peut fonctionner sur différentes structures HTML sans modification du code source.

---

# Exemple de configuration YAML

```yaml
url: https://books.toscrape.com/

pagination:
  pattern: /catalogue/page-{n}.html
  start: 1
  max_pages: 5

selectors:
  titre: article.product_pod h3 a
  url: article.product_pod h3 a
  prix: p.price_color

fetcher:
  delay: 1
  retries: 3
  timeout: 15
  user_agent: DataHarvest/1.0

store:
  backend: sqlite
  path: output/books.db
```

---

# Flux de données

```
Configuration YAML

        |
        v

      Config

        |
        v

   Orchestrator

        |
        |
 -------------------------
 |          |            |
 v          v            v

Fetcher  Pipeline   Validator

        |
        v

      Store

        |
        v

 SQLite / JSON / CSV
```

---

# Tests

Le projet contient :

- Tests unitaires
- Test d'intégration

Lancer les tests :

```bash
pytest
```

Avec couverture :

```bash
pytest --cov=dataharvest
```

---

# Technologies utilisées

- Python 3
- Requests
- BeautifulSoup4
- PyYAML
- SQLite3
- JSON
- CSV
- Pytest
- Argparse

---

# Limites du projet

DataHarvest est volontairement limité aux sites HTML statiques.

Fonctionnalités non prises en charge :

- Rendu JavaScript côté client
- Selenium
- Playwright
- Scraping asynchrone
- Authentification complexe

---

# Perspectives d'évolution

Améliorations possibles :

- Support Playwright pour les sites dynamiques
- Scraping asynchrone
- Système de notification
- Planificateur automatique
- Monitoring des changements HTML
- Publication sur PyPI

---

# Projet académique

Ce projet a été réalisé dans le cadre du module **Web Scraping** du :

**Master Dev, Data & IA – IPSSI Nice**

L'objectif était de concevoir un framework de scraping modulaire en appliquant des concepts avancés de conception logicielle :

- Injection de dépendances
- Middleware
- Architecture découplée
- Validation des données
- Stockage multi-backend

---

# Licence

Projet réalisé uniquement à des fins pédagogiques dans le cadre de la formation IPSSI.