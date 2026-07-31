"""
config.py -- Chargement et validation de la configuration DataHarvest.

Charge un fichier YAML ou JSON, valide la presence des cles obligatoires,
et expose les valeurs sous forme d'attributs (avec sous-objets navigables
en notation pointee, ex: config.fetcher.delay).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

# Cles de premier niveau obligatoires dans tout fichier de config.
REQUIRED_TOP_LEVEL_KEYS = ("url", "pagination", "selectors", "fetcher", "store")

# Cles obligatoires a l'interieur de chaque section.
REQUIRED_SUB_KEYS = {
    "pagination": ("pattern", "start", "max_pages"),
    "fetcher": ("delay", "retries", "timeout", "user_agent"),
    "store": ("backend", "path"),
}


class ConfigSection:
    """Petit wrapper qui transforme un dict en objet a attributs.

    Permet d'ecrire config.fetcher.delay plutot que config['fetcher']['delay'],
    tout en restant indexable comme un dict si besoin.
    """

    def __init__(self, data: dict):
        self._data = dict(data)
        for key, value in self._data.items():
            if isinstance(value, dict):
                value = ConfigSection(value)
            setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def to_dict(self) -> dict:
        return dict(self._data)

    def __repr__(self) -> str:  # pragma: no cover - confort de debug
        return f"ConfigSection({self._data!r})"


class Config:
    """Charge, valide et expose la configuration d'un site a scraper.

    Usage:
        config = Config("configs/example_blog.yaml")
        config.url                  -> str
        config.selectors            -> dict
        config.fetcher.delay        -> float
        config.pagination.max_pages -> int
        config.store.backend        -> str
    """

    def __init__(self, path: str | os.PathLike):
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"Fichier de configuration introuvable : {self.path}")

        raw = self._load_raw(self.path)
        self._validate(raw)

        self._raw = raw
        self.url: str = raw["url"]
        # selectors reste un dict brut (les composants iterent dessus)
        self.selectors: dict = dict(raw["selectors"])
        self.pagination = ConfigSection(raw["pagination"])
        self.fetcher = ConfigSection(self._coerce_fetcher_types(raw["fetcher"]))
        self.store = ConfigSection(raw["store"])

    @staticmethod
    def _load_raw(path: Path) -> dict:
        suffix = path.suffix.lower()
        text = path.read_text(encoding="utf-8")
        if suffix in (".yaml", ".yml"):
            data = yaml.safe_load(text)
        elif suffix == ".json":
            data = json.loads(text)
        else:
            raise ValueError(
                f"Extension de fichier non supportee : {suffix} "
                "(attendu : .yaml, .yml ou .json)"
            )
        if not isinstance(data, dict):
            raise ValueError("Le fichier de configuration doit contenir un objet racine (mapping).")
        return data

    @staticmethod
    def _coerce_fetcher_types(fetcher_raw: dict) -> dict:
        """Force delay/timeout en float et retries en int, meme si le YAML
        les a charges comme int/str par accident."""
        coerced = dict(fetcher_raw)
        if "delay" in coerced:
            coerced["delay"] = float(coerced["delay"])
        if "timeout" in coerced:
            coerced["timeout"] = float(coerced["timeout"])
        if "retries" in coerced:
            coerced["retries"] = int(coerced["retries"])
        return coerced

    @classmethod
    def _validate(cls, raw: dict) -> None:
        missing_top = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in raw]
        if missing_top:
            raise ValueError(
                f"Cle(s) obligatoire(s) manquante(s) dans la config : {', '.join(missing_top)}"
            )

        if not isinstance(raw["selectors"], dict) or not raw["selectors"]:
            raise ValueError("La section 'selectors' doit etre un mapping non vide.")

        for section_name, required in REQUIRED_SUB_KEYS.items():
            section = raw[section_name]
            if not isinstance(section, dict):
                raise ValueError(f"La section '{section_name}' doit etre un mapping.")
            missing = [k for k in required if k not in section]
            if missing:
                raise ValueError(
                    f"Cle(s) obligatoire(s) manquante(s) dans '{section_name}' : "
                    f"{', '.join(missing)}"
                )

    def __repr__(self) -> str:  # pragma: no cover - confort de debug
        return f"Config(url={self.url!r}, backend={self.store.backend!r})"
