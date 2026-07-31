"""
fetcher.py -- Telechargement HTTP via requests.Session, avec chaine de
middlewares et retries geres par RetryMiddleware.
"""
from __future__ import annotations

import time

import requests

from .middleware import BaseMiddleware, RetryMiddleware


class FetchError(Exception):
    """Levee quand fetch() epuise tous ses essais sans succes."""


class Fetcher:
    """Responsable du telechargement HTML. Orchestre la chaine de
    middlewares et retourne le HTML brut sous forme de str.
    """

    def __init__(self, config, middlewares: list[BaseMiddleware] | None = None, session: requests.Session | None = None):
        self.config = config
        self.middlewares = middlewares or []
        self.session = session or requests.Session()

        # Retrouve le RetryMiddleware dans la chaine s'il existe, sinon
        # cree une politique de retry par defaut a partir de la config.
        self._retry_policy = next(
            (m for m in self.middlewares if isinstance(m, RetryMiddleware)),
            RetryMiddleware(config),
        )

    def fetch(self, url: str) -> str:
        """Retourne le HTML ou leve FetchError apres epuisement des retries."""
        headers = {"User-Agent": self.config.fetcher.user_agent}

        for middleware in self.middlewares:
            url, headers = middleware.process_request(url, headers)

        attempt = 0
        last_exception: Exception | None = None
        while True:
            try:
                response = self.session.get(
                    url, headers=headers, timeout=self.config.fetcher.timeout
                )
                response.url = url  # utilise par LoggingMiddleware
                # Corrige l'encodage : requests retombe parfois sur ISO-8859-1
                # par defaut quand le serveur n'envoie pas de charset explicite,
                # meme si le contenu reel est en UTF-8 (cas frequent, ex: books.toscrape.com).
                response.encoding = response.apparent_encoding

                for middleware in self.middlewares:
                    response = middleware.process_response(response)

                if response.status_code >= 400:
                    if self._retry_policy.should_retry(attempt, status_code=response.status_code):
                        time.sleep(self._retry_policy.backoff_delay(attempt))
                        attempt += 1
                        continue
                    raise FetchError(
                        f"Echec du fetch pour {url} : HTTP {response.status_code} "
                        f"apres {attempt + 1} tentative(s)"
                    )

                return response.text

            except requests.RequestException as exc:
                last_exception = exc
                if self._retry_policy.should_retry(attempt, exception=exc):
                    time.sleep(self._retry_policy.backoff_delay(attempt))
                    attempt += 1
                    continue
                raise FetchError(
                    f"Echec du fetch pour {url} apres {attempt + 1} tentative(s) : {exc}"
                ) from last_exception

    def fetch_all(self, urls: list[str]) -> list[str]:
        """Fetche une liste d'URLs en respectant config.fetcher.delay entre chaque."""
        results = []
        for index, url in enumerate(urls):
            if index > 0:
                time.sleep(self.config.fetcher.delay)
            results.append(self.fetch(url))
        return results