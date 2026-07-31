import pytest

from dataharvest.config import Config

VALID_YAML = """
url: https://example.com/
pagination:
  pattern: /page/{n}/
  start: 1
  max_pages: 3
selectors:
  titre: h2.title a
  url: h2.title a
fetcher:
  delay: 1.5
  retries: 3
  timeout: 15
  user_agent: DataHarvest/1.0
store:
  backend: sqlite
  path: output/test.db
"""

MISSING_KEY_YAML = """
url: https://example.com/
pagination:
  pattern: /page/{n}/
  start: 1
  max_pages: 3
selectors:
  titre: h2.title a
fetcher:
  delay: 1.5
  retries: 3
  timeout: 15
  user_agent: DataHarvest/1.0
"""


def test_config_raises_filenotfounderror_on_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        Config(tmp_path / "does_not_exist.yaml")


def test_config_raises_valueerror_on_missing_required_key(tmp_path):
    path = tmp_path / "bad_config.yaml"
    path.write_text(MISSING_KEY_YAML, encoding="utf-8")
    with pytest.raises(ValueError):
        Config(path)


def test_config_loads_valid_yaml(tmp_path):
    path = tmp_path / "good_config.yaml"
    path.write_text(VALID_YAML, encoding="utf-8")
    config = Config(path)

    assert config.url == "https://example.com/"
    assert isinstance(config.fetcher.delay, float)
    assert config.fetcher.delay == 1.5
    assert config.pagination.max_pages == 3
    assert config.store.backend == "sqlite"
    assert isinstance(config.selectors, dict)


def test_config_supports_json(tmp_path):
    import json

    data = {
        "url": "https://example.com/",
        "pagination": {"pattern": None, "start": 1, "max_pages": 1},
        "selectors": {"titre": "h2 a", "url": "h2 a"},
        "fetcher": {"delay": 1, "retries": 2, "timeout": 10, "user_agent": "UA"},
        "store": {"backend": "json", "path": "output/test.json"},
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    config = Config(path)
    assert config.url == "https://example.com/"
    assert config.fetcher.delay == 1.0


def test_config_rejects_unsupported_extension(tmp_path):
    path = tmp_path / "config.txt"
    path.write_text("url: https://example.com/", encoding="utf-8")
    with pytest.raises(ValueError):
        Config(path)
