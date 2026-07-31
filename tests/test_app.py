import json
from unittest.mock import patch

from dataharvest.app import main

VALID_CONFIG = """
url: https://example.com/
pagination:
  pattern: null
  start: 1
  max_pages: 1
selectors:
  titre: h2 a
  url: h2 a
fetcher:
  delay: 0
  retries: 1
  timeout: 5
  user_agent: DataHarvest/1.0
store:
  backend: json
  path: {store_path}
"""


def _write_config(tmp_path):
    store_path = tmp_path / "output" / "items.json"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(VALID_CONFIG.format(store_path=store_path), encoding="utf-8")
    return config_path


def test_cli_validate_returns_0_on_valid_config(tmp_path, capsys):
    config_path = _write_config(tmp_path)
    exit_code = main(["validate", "--config", str(config_path)])
    captured = capsys.readouterr()
    assert exit_code == 0
    assert "valide" in captured.out.lower()


def test_cli_validate_returns_1_on_missing_file(tmp_path, capsys):
    exit_code = main(["validate", "--config", str(tmp_path / "nope.yaml")])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "invalide" in captured.out.lower()


def test_cli_crawl_dry_run_does_not_store(tmp_path, capsys):
    config_path = _write_config(tmp_path)
    fake_html = '<html><h2><a href="/x">Titre</a></h2></html>'

    with patch("dataharvest.fetcher.Fetcher.fetch", return_value=fake_html):
        exit_code = main(["crawl", "--config", str(config_path), "--dry-run"])

    assert exit_code == 0
    store_path = tmp_path / "output" / "items.json"
    assert not store_path.exists()


def test_cli_crawl_stores_items(tmp_path):
    config_path = _write_config(tmp_path)
    fake_html = '<html><h2><a href="/x">Titre</a></h2></html>'

    with patch("dataharvest.fetcher.Fetcher.fetch", return_value=fake_html):
        exit_code = main(["crawl", "--config", str(config_path)])

    assert exit_code == 0
    store_path = tmp_path / "output" / "items.json"
    assert store_path.exists()
    data = json.loads(store_path.read_text(encoding="utf-8"))
    assert len(data) == 1


def test_cli_export_transfers_items(tmp_path):
    source = tmp_path / "items.json"
    source.write_text(
        json.dumps([{"titre": "A", "url": "https://example.com/1"}]), encoding="utf-8"
    )
    target = tmp_path / "items.csv"

    exit_code = main(["export", "--from", str(source), "--to", str(target)])

    assert exit_code == 0
    assert target.exists()
