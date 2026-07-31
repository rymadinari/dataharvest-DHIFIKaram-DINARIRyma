#  DataHarvest

> Framework de scraping modulaire, générique et configurable développé dans le cadre du projet final de **Web Scraping**.

**Master Dev, Data & IA – 4ème année**  
**IPSSI Nice**

##  Auteurs

- **Karam DHIF**
- **Ryma DINARI**

---

#  Présentation

DataHarvest est un framework Python conçu pour automatiser l'extraction de données à partir de sites web HTML statiques.

Contrairement à un script de scraping classique développé pour un seul site, DataHarvest repose sur une architecture modulaire où chaque composant possède une responsabilité bien définie. Grâce à un fichier de configuration YAML ou JSON, il est possible d'adapter le framework à un nouveau site sans modifier le code source.

L'objectif principal est de proposer un framework réutilisable, facilement extensible et simple à maintenir.

---

#  Fonctionnalités

- Chargement de configuration YAML ou JSON
- Téléchargement des pages via Requests
- Gestion des middlewares
- Logging des requêtes HTTP
- Retry automatique avec backoff exponentiel
- Pagination configurable
- Extraction générique via des sélecteurs CSS
- Validation des données collectées
- Stockage des résultats en :
  - SQLite
  - JSON
  - CSV
- Export entre différents formats
- Interface en ligne de commande (CLI)
- Architecture modulaire orientée composants
- Tests unitaires avec Pytest

---

#  Architecture

```
                Configuration YAML
                        │
                        ▼
                +----------------+
                |     Config     |
                +----------------+
                        │
                        ▼
                +----------------+
                |  Orchestrator  |
                +----------------+
             /       |        |       \
            ▼        ▼        ▼        ▼
      Fetcher   Pipeline  Validator  Store
          │
          ▼
    Middleware Chain
   ├── LoggingMiddleware
   ├── RetryMiddleware
   └── RateLimitMiddleware
```

---

#  Structure du projet

```
dataharvest/

│
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

#  Architecture des composants

Le framework est composé de cinq briques principales :

## Config

Charge et valide les fichiers YAML ou JSON.

Responsabilités :

- lecture de la configuration
- validation des clés obligatoires
- exposition des paramètres au reste du framework

---

## Fetcher

Responsable des requêtes HTTP.

Fonctionnalités :

- téléchargement des pages
- gestion du User-Agent
- exécution de la chaîne de middlewares
- retry automatique

---

## Pipeline

Transforme le HTML brut en données structurées.

Deux implémentations :

- GenericPipeline
- PaginationPipeline

---

## Validator

Filtre les données extraites.

Il vérifie notamment :

- les champs obligatoires
- les URLs
- la longueur minimale de certains champs

---

## Store

Sauvegarde les données.

Backends disponibles :

- SQLite
- JSON
- CSV

---



## Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# Utilisation

## Scraper un site

```bash
python -m dataharvest crawl --config configs/books_toscrape.yaml
```

---

## Mode Dry Run

Le mode Dry Run récupère uniquement la première page sans enregistrer les données.

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

SQLite vers CSV :

```bash
python -m dataharvest export --from output/books.db --to output/books.csv
```

---

#  Sites testés

Le framework a été testé sur plusieurs sites présentant différents niveaux de difficulté.

| Site | Niveau | Backend |
|-------|---------|----------|
| Books To Scrape | Niveau 1 | SQLite |
| Quotes To Scrape | Niveau 1 | JSON |
| Wikipedia (Population) | Niveau 2 | JSON |
| Blog du Modérateur | Niveau 3 | SQLite |
| GitHub Trending | Niveau 4 | CSV |

Cette diversité permet de démontrer que le framework fonctionne sur plusieurs structures HTML sans modification du code source, uniquement grâce aux fichiers de configuration. :contentReference[oaicite:1]{index=1}

---

#  Exemple de configuration

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

# 🔄 Flux de données

```
Configuration YAML
        │
        ▼
      Config
        │
        ▼
   Orchestrator
        │
 ┌──────┼───────────────┐
 ▼      ▼               ▼
Fetcher Pipeline    Validator
        │
        ▼
      Store
        │
        ▼
SQLite / JSON / CSV
```

---

#  Tests

Le projet comprend :

- des tests unitaires
- un test d'intégration

Lancer tous les tests :

```bash
pytest
```

Lancer avec la couverture :

```bash
pytest --cov=dataharvest
```

---

#  Technologies utilisées

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

#  Limites du projet

DataHarvest est volontairement limité aux sites HTML statiques.

Ne sont pas pris en charge :

- le rendu JavaScript
- Selenium
- Playwright
- le scraping asynchrone
- les systèmes d'authentification complexes

Ces fonctionnalités pourraient être ajoutées dans une future version.

---

#  Perspectives

Plusieurs évolutions sont envisageables :

- ajout d'un moteur Playwright
- support des sites JavaScript
- exécution asynchrone
- système de notification
- planificateur automatique de scraping
- publication du framework sur PyPI

---

#  Projet académique

Ce projet a été réalisé dans le cadre du module **Web Scraping** du **Master Dev, Data & IA** à **IPSSI Nice**.

L'objectif était de concevoir un framework de scraping modulaire mettant en œuvre les principaux concepts d'architecture logicielle en Python (injection de dépendances, middleware, composants découplés, validation et stockage multi-backend).

---

#  Licence

Ce projet est fourni uniquement à des fins pédagogiques dans le cadre de la formation IPSSI.