from pathlib import Path
from unittest.mock import patch

import pytest

from dataharvest.config import Config
from dataharvest.orchestrator import Orchestrator

CONFIG_YAML = """
url: https://example.com/page/1/
pagination:
  pattern: /page/{{n}}/
  start: 1
  max_pages: 2
selectors:
  titre: h2.title a
  url: h2.title a
fetcher:
  delay: 0
  retries: 1
  timeout: 5
  user_agent: DataHarvest/1.0
store:
  backend: json
  path: {store_path}
"""

FAKE_HTML = """
<html><body>
  <div><h2 class="title"><a href="/item/1">Titre 1</a></h2></div>
  <div><h2 class="title"><a href="/item/2">Titre 2</a></h2></div>
</body></html>
"""


def _make_config(tmp_path):
    store_path = tmp_path / "output" / "items.json"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        CONFIG_YAML.format(store_path=store_path), encoding="utf-8"
    )
    return Config(config_path)


def test_orchestrator_run_returns_expected_report_keys(tmp_path):
    """Unitaire : Fetcher est mocke, aucune connexion internet requise."""
    config = _make_config(tmp_path)
    orchestrator = Orchestrator(config)

    with patch.object(orchestrator.fetcher, "fetch", return_value=FAKE_HTML):
        report = orchestrator.run()

    expected_keys = {
        "pages_scrapees",
        "items_trouves",
        "items_valides",
        "items_rejetes",
        "items_stockes",
        "duree_secondes",
    }
    assert expected_keys.issubset(report.keys())
    assert report["items_trouves"] == 4  # 2 pages x 2 items (max_pages=2)
    assert report["items_stockes"] == 2  # dedoublonnage par URL


@pytest.mark.integration
def test_orchestrator_run_on_real_site(tmp_path):
    """Necessite une connexion internet. Exclure avec: pytest -m 'not integration'."""
    config = Config(Path("configs/example_blog.yaml"))
    orchestrator = Orchestrator(config)
    report = orchestrator.run()

    assert report["items_stockes"] >= 5
    store_path = Path(config.store.path)
    assert store_path.exists()
    assert store_path.stat().st_size > 0
