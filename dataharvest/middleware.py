"""
middleware.py -- Chaine de middlewares interceptant requetes/reponses.

Meme pattern que Django/Flask : chaque middleware peut modifier la requete
avant envoi (process_request) et la reponse apres reception (process_response),
sans que le Fetcher n'ait besoin de connaitre leur logique interne.
"""
from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from urllib.parse import urlparse

logger = logging.getLogger("dataharvest.middleware")

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class BaseMiddleware(ABC):
    """Interface abstraite que tout middleware doit implementer."""

    @abstractmethod
    def process_request(self, url: str, headers: dict) -> tuple[str, dict]:
        """Retourne (url, headers) potentiellement modifies."""

    @abstractmethod
    def process_response(self, response):
        """Retourne la response potentiellement transformee."""


class LoggingMiddleware(BaseMiddleware):
    """Log chaque requete sortante et sa reponse avec le temps ecoule."""

    def __init__(self):
        self._start_times: dict[int, float] = {}

    def process_request(self, url: str, headers: dict) -> tuple[str, dict]:
        logger.info("[GET %s]", url)
        self._start_times[id(url)] = time.perf_counter()
        return url, headers

    def process_response(self, response):
        elapsed = time.perf_counter() - self._start_times.pop(id(response.url), time.perf_counter())
        logger.info("[%s - %.2fs]", getattr(response, "status_code", "?"), elapsed)
        return response


class RetryMiddleware(BaseMiddleware):
    """Reimplemente un backoff exponentiel pour les codes 429/5xx.

    Le retry effectif (nouvelle requete HTTP) est pilote par le Fetcher ;
    ce middleware expose la politique de delai et decide si une reponse
    doit declencher un nouvel essai.
    """

    def __init__(self, config=None, base_delay: float = 1.0, max_retries: int = 3):
        if config is not None:
            self.max_retries = int(config.fetcher.retries)
        else:
            self.max_retries = max_retries
        self.base_delay = base_delay

    def process_request(self, url: str, headers: dict) -> tuple[str, dict]:
        return url, headers

    def process_response(self, response):
        return response

    def should_retry(self, attempt: int, status_code: int | None = None, exception: Exception | None = None) -> bool:
        if attempt >= self.max_retries:
            return False
        if exception is not None:
            return True
        if status_code is not None and status_code in RETRYABLE_STATUS_CODES:
            return True
        return False

    def backoff_delay(self, attempt: int) -> float:
        """delai = base * (2 ** attempt)"""
        return self.base_delay * (2 ** attempt)


class RateLimitMiddleware(BaseMiddleware):
    """Garantit un delai minimum entre deux requetes vers le meme domaine.

    Bonus (section 3.2 du sujet).
    """

    def __init__(self, min_delay: float = 1.0):
        self.min_delay = min_delay
        self._last_request_at: dict[str, float] = {}

    def process_request(self, url: str, headers: dict) -> tuple[str, dict]:
        domain = urlparse(url).netloc
        now = time.perf_counter()
        last = self._last_request_at.get(domain)
        if last is not None:
            elapsed = now - last
            wait = self.min_delay - elapsed
            if wait > 0:
                time.sleep(wait)
        self._last_request_at[domain] = time.perf_counter()
        return url, headers

    def process_response(self, response):
        return response
