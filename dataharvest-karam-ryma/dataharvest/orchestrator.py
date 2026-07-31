"""
orchestrator.py -- Assemble tous les composants et pilote le scraping complet.
C'est le seul composant qui connait tous les autres (couplage centralise
volontairement ici, pour que le reste du systeme reste decouple).
"""
from __future__ import annotations

import logging
import time

from .config import Config
from .fetcher import Fetcher, FetchError
from .middleware import LoggingMiddleware, RetryMiddleware
from .pipeline import PaginationPipeline
from .store import Store
from .validator import Validator

logger = logging.getLogger("dataharvest.orchestrator")


class Orchestrator:
    def __init__(self, config: Config):
        self.config = config
        self.fetcher = Fetcher(
            config, middlewares=[LoggingMiddleware(), RetryMiddleware(config)]
        )
        self.pipeline = PaginationPipeline(
            config.selectors, config.pagination, base_url=config.url
        )
        self.validator = Validator(required_fields=["titre", "url"])
        self.store = Store(config.store.backend, config.store.path)

    def run(self, dry_run: bool = False) -> dict:
        """Lance le scraping complet. Retourne un rapport de session."""
        start_time = time.perf_counter()

        pages_scrapees = 0
        items_trouves = 0
        items_valides = 0
        items_rejetes = 0
        items_stockes = 0

        current_url = self.config.url
        seen_urls = set()

        while current_url and current_url not in seen_urls:
            seen_urls.add(current_url)
            try:
                html = self.fetcher.fetch(current_url)
            except FetchError as exc:
                logger.error("Abandon du crawl : %s", exc)
                break

            pages_scrapees += 1
            items = self.pipeline.process(html)
            items_trouves += len(items)

            valid, rejected = self.validator.validate(items)
            items_valides += len(valid)
            items_rejetes += len(rejected)

            if not dry_run and valid:
                items_stockes += self.store.save(valid)
            elif dry_run:
                for item in valid:
                    print(item)

            if dry_run:
                break

            next_url = self.pipeline.next_page_url(html, current_url)
            current_url = next_url

        duree_secondes = round(time.perf_counter() - start_time, 3)

        return self._build_report(
            pages_scrapees=pages_scrapees,
            items_trouves=items_trouves,
            items_valides=items_valides,
            items_rejetes=items_rejetes,
            items_stockes=items_stockes,
            duree_secondes=duree_secondes,
        )

    def _build_report(
        self,
        pages_scrapees: int,
        items_trouves: int,
        items_valides: int,
        items_rejetes: int,
        items_stockes: int,
        duree_secondes: float,
    ) -> dict:
        """Construit le rapport JSON de la session."""
        return {
            "pages_scrapees": pages_scrapees,
            "items_trouves": items_trouves,
            "items_valides": items_valides,
            "items_rejetes": items_rejetes,
            "items_stockes": items_stockes,
            "duree_secondes": duree_secondes,
        }
