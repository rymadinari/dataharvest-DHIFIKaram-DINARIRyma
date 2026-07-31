"""
pipeline.py -- Extraction des donnees structurees depuis le HTML brut.

BasePipeline est une ABC : elle garantit a l'Orchestrator que toute
implementation concrete expose process() et next_page_url() avec la
bonne signature, sans avoir a verifier duck-typing a l'execution.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


class BasePipeline(ABC):
    @abstractmethod
    def process(self, html: str) -> list[dict]:
        """Retourne TOUJOURS une liste, jamais None."""

    @abstractmethod
    def next_page_url(self, html: str, current_url: str) -> str | None:
        """Retourne l'URL de la page suivante ou None si fin."""


class GenericPipeline(BasePipeline):
    """Extrait des items a partir des selecteurs CSS fournis par la config.

    Ne code aucun selecteur en dur : ils viennent entierement de
    selectors (dict {nom_champ: selecteur_css}).
    """

    def __init__(self, selectors: dict, base_url: str = ""):
        self.selectors = dict(selectors)
        self.base_url = base_url

    def process(self, html: str) -> list[dict]:
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # On determine le nombre d'items via le premier selecteur (celui
        # qui identifie generalement le conteneur repete, ex: le titre).
        field_names = list(self.selectors.keys())
        if not field_names:
            return []

        anchor_field = field_names[0]
        anchor_matches = soup.select(self.selectors[anchor_field])

        items = []
        for index in range(len(anchor_matches)):
            item = {}
            for field in field_names:
                matches = soup.select(self.selectors[field])
                value = ""
                if index < len(matches):
                    value = self._extract_value(matches[index], field)
                if field == "url" and value:
                    value = self._resolve_url(value)
                item[field] = value
            items.append(item)

        return items

    def _extract_value(self, tag, field: str) -> str:
        """Extrait un texte lisible. Convention : le champ nomme 'url' recupere
        l'attribut href d'un <a>, un champ dont le tag a un attribut datetime
        recupere cet attribut ; sinon on prend le texte visible."""
        if field == "url" and tag.name == "a" and tag.has_attr("href"):
            return tag["href"].strip()
        if tag.has_attr("datetime"):
            return tag["datetime"].strip()
        return tag.get_text(strip=True)

    def _resolve_url(self, url: str) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        return urljoin(self.base_url, url)

    def next_page_url(self, html: str, current_url: str) -> str | None:
        """GenericPipeline ne gere pas la pagination : toujours None.
        PaginationPipeline surcharge cette methode pour la gerer reellement."""
        return None


class PaginationPipeline(GenericPipeline):
    """Etend GenericPipeline avec la gestion de la pagination."""

    def __init__(self, selectors: dict, pagination_config, base_url: str = ""):
        super().__init__(selectors, base_url=base_url)
        self.pagination_config = pagination_config

    def next_page_url(self, html: str, current_url: str) -> str | None:
        pattern = getattr(self.pagination_config, "pattern", None)
        if not pattern:
            return None

        max_pages = int(getattr(self.pagination_config, "max_pages", 1))
        start = int(getattr(self.pagination_config, "start", 1))

        # Si la page courante ne contient plus d'items, on arrete.
        items = self.process(html)
        if not items:
            return None

        current_page = self._extract_page_number(current_url, pattern, start)
        next_page = current_page + 1

        if next_page > start + max_pages - 1:
            return None

        parsed = urlparse(current_url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        next_path = pattern.format(n=next_page)
        return urljoin(base, next_path)

    def _extract_page_number(self, current_url: str, pattern: str, start: int) -> int:
        """Devine le numero de page courant a partir de l'URL, en se basant
        sur le pattern de pagination (ex: /page/{n}/)."""
        prefix, _, suffix = pattern.partition("{n}")
        suffix = suffix.split("}", 1)[-1] if "}" in suffix else suffix
        if prefix and prefix in current_url:
            after_prefix = current_url.split(prefix, 1)[1]
            digits = "".join(ch for ch in after_prefix.split("/")[0] if ch.isdigit())
            if digits:
                return int(digits)
        return start
