"""
validator.py -- Filtre les items invalides avant stockage.

Le Validator n'a jamais le droit de modifier un item : il l'accepte tel
quel ou le rejette. Toute normalisation/nettoyage releve de la Pipeline.
"""
from __future__ import annotations

import logging
from urllib.parse import urlparse

logger = logging.getLogger("dataharvest.validator")


class Validator:
    def __init__(self, required_fields: list[str], min_lengths: dict | None = None):
        self.required_fields = list(required_fields)
        self.min_lengths = dict(min_lengths or {})

    def validate(self, items: list[dict]) -> tuple[list[dict], list[dict]]:
        """Retourne (valides, rejetes)."""
        valid, rejected = [], []
        for item in items:
            reason = self._rejection_reason(item)
            if reason is None:
                valid.append(item)
            else:
                logger.warning("Item rejete (%s) : %r", reason, item)
                rejected.append(item)
        return valid, rejected

    def _rejection_reason(self, item: dict) -> str | None:
        for field in self.required_fields:
            if not item.get(field):
                return f"champ manquant ou vide: {field}"

        url = item.get("url")
        if url and not self.is_valid_url(url):
            return "url invalide"

        for field, min_len in self.min_lengths.items():
            value = item.get(field, "")
            if value and len(value) < min_len:
                return f"{field} trop court (< {min_len} caracteres)"

        return None

    def is_valid_url(self, url: str) -> bool:
        """True si l'URL commence par http(s):// et contient un domaine."""
        if not isinstance(url, str):
            return False
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
