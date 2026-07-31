"""
app.py -- Point d'entree CLI. python -m dataharvest <sous-commande> ...
"""
from __future__ import annotations

import argparse
import logging
import sys

from .config import Config
from .orchestrator import Orchestrator
from .store import Store

logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dataharvest", description="Framework de scraping modulaire")
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl = subparsers.add_parser("crawl", help="Scrape un site selon un fichier de config")
    crawl.add_argument("--config", required=True, help="Chemin du fichier YAML/JSON")
    crawl.add_argument(
        "--dry-run", action="store_true",
        help="Fetche/parse uniquement la 1ere page, affiche les items sans stocker",
    )

    export = subparsers.add_parser("export", help="Exporte un store vers un autre backend")
    export.add_argument("--from", dest="from_path", required=True, help="Chemin du store source")
    export.add_argument("--to", dest="to_path", required=True, help="Chemin du store cible")

    validate = subparsers.add_parser("validate", help="Verifie un fichier de config sans scraper")
    validate.add_argument("--config", required=True, help="Chemin du fichier YAML/JSON")

    return parser


def _backend_from_path(path: str) -> str:
    suffix = path.rsplit(".", 1)[-1].lower()
    return {"db": "sqlite", "sqlite": "sqlite", "csv": "csv", "json": "json"}.get(suffix, suffix)


def cmd_crawl(args: argparse.Namespace) -> int:
    config = Config(args.config)
    orchestrator = Orchestrator(config)
    report = orchestrator.run(dry_run=args.dry_run)
    print(report)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    source_backend = _backend_from_path(args.from_path)
    target_backend = _backend_from_path(args.to_path)
    store = Store(source_backend, args.from_path)
    exported = store.export_to(target_backend, args.to_path)
    print(f"{exported} item(s) exporte(s) vers {args.to_path}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        Config(args.config)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Configuration invalide : {exc}")
        return 1
    print("Configuration valide.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {"crawl": cmd_crawl, "export": cmd_export, "validate": cmd_validate}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
