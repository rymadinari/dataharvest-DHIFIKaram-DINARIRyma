# DataHarvest

Framework de scraping modulaire, generique et configurable — projet final
Web Scraping, IPSSI, Master Dev Data & IA (4e annee).

Binome : **Prenom1 NOM1** & **Prenom2 NOM2**

## 1. Presentation

DataHarvest permet de scraper n'importe quel site HTML statique en
modifiant uniquement un fichier de configuration YAML/JSON — sans toucher
au code source. Le framework est decoupe en 5 composants independants,
relies exclusivement par injection de dependances (jamais d'import direct
entre composants metier).

## 2. Architecture

```
Config (YAML/JSON)
        |
        v
   Orchestrator
        |-- Fetcher [+ chaine de Middleware] --> HTML brut
        |-- Pipeline.process(html) -------------> list[dict]
        |-- Validator.validate(items) -----------> items valides / rejetes
        '-- Store.save(items) -------------------> csv / sqlite / json
```

```
dataharvest-prenom1-prenom2/
|-- dataharvest/
|   |-- __init__.py        # version = '1.0.0'
|   |-- config.py          # Config -- chargement + validation YAML/JSON
|   |-- fetcher.py         # Fetcher -- HTTP + retries via requests.Session
|   |-- pipeline.py        # BasePipeline (ABC), GenericPipeline, PaginationPipeline
|   |-- validator.py       # Validator -- filtre les items avant stockage
|   |-- store.py           # Store -- backends csv / sqlite / json
|   |-- orchestrator.py    # Orchestrator -- assemble tous les composants
|   |-- middleware.py      # BaseMiddleware, Logging/Retry/RateLimit
|   '-- app.py             # CLI (crawl / export / validate)
|-- tests/                 # pytest, couverture >= 80%
|-- configs/               # un fichier YAML par site scrape
|-- output/                # fichiers de sortie (ignores par git)
|-- README.md
|-- requirements.txt
'-- .gitignore
```

### Pourquoi cette architecture ?

- **Composants decouples** : chaque brique (Fetcher, Pipeline, Validator,
  Store) est testable isolement, sans dependre des autres — on peut
  remplacer le backend de stockage sans toucher au reste.
- **BasePipeline en ABC** : garantit a l'Orchestrator que toute pipeline
  concrete expose `process()` et `next_page_url()` avec la bonne
  signature ; une classe qui oublie une methode ne peut simplement pas
  etre instanciee (erreur a la construction, pas a l'execution).
- **Pattern middleware pour le Fetcher** : permet d'ajouter logging,
  retry ou rate-limiting sans modifier `Fetcher.fetch()`. Chaque
  middleware ne connait que `(url, headers)` / `response`.
- **Injection de dependances** : l'Orchestrator recoit un `Config` en
  entree et construit lui-meme ses composants ; en test, on peut injecter
  un `Fetcher` mocke sans toucher au reste de la chaine.

## 3. Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Usage

```bash
# Scraper un site
python -m dataharvest crawl --config configs/example_blog.yaml

# Mode dry-run (fetch + parse la 1ere page seulement, sans stocker)
python -m dataharvest crawl --config configs/example_blog.yaml --dry-run

# Valider un fichier de config sans scraper
python -m dataharvest validate --config configs/example_blog.yaml

# Exporter un store vers un autre backend
python -m dataharvest export --from output/articles.db --to output/articles.csv
```

## 5. Sites scrapes (5 minimum, >= 2 niveaux)

| Config | Site | Niveau | Backend |
|---|---|---|---|
| `configs/books_toscrape.yaml` | books.toscrape.com | N1 | sqlite |
| `configs/quotes_toscrape.yaml` | quotes.toscrape.com | N1 | json |
| `configs/pypi_search.yaml` | pypi.org/search | N2 | csv |
| `configs/openfoodfacts.yaml` | fr.openfoodfacts.org | N2 | sqlite |
| `configs/example_blog.yaml` | blogdumoderateur.com | N3 | sqlite |

> Note : les selecteurs CSS de `books_toscrape.yaml` et
> `openfoodfacts.yaml` sont a verifier/ajuster avec les DevTools sur le
> vrai DOM avant la restitution finale — ils ont ete ecrits sans acces
> reseau au site cible.

## 6. Tests

```bash
pytest -m "not integration" --cov=dataharvest --cov-report=term-missing -v
```

Couverture actuelle : **90 %** (36 tests unitaires). Le test
d'integration (`tests/test_integration.py::test_orchestrator_run_on_real_site`)
est marque `@pytest.mark.integration` et necessite une connexion internet ;
il est exclu par defaut de la commande ci-dessus.

## 7. Extensions implementees

- `RateLimitMiddleware` (bonus 3.2 / Extension C) : delai minimum garanti
  entre deux requetes vers le meme domaine, teste dans
  `tests/test_middleware.py`.

## 8. Limites connues (hors perimetre volontaire)

- Pas de support JavaScript/rendu dynamique (pas de Selenium/Playwright
  integre par defaut).
- Pas d'execution asynchrone (contrairement a Scrapy/Twisted) — voir le
  rapport technique, section 3, pour le calcul d'impact sur les
  performances.
- Detection du numero de page courant basee sur le pattern d'URL fourni
  en config (pas de parsing du DOM pour trouver le lien "page suivante").
