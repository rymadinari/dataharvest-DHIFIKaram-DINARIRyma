import json

import pytest

from dataharvest.store import Store


def test_store_raises_valueerror_on_unknown_backend(tmp_path):
    with pytest.raises(ValueError):
        Store("xml", tmp_path / "out.xml")


def test_json_store_creates_valid_json_file(tmp_path):
    path = tmp_path / "items.json"
    store = Store("json", path)
    inserted = store.save([{"titre": "A", "url": "https://example.com/1"}])

    assert inserted == 1
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["titre"] == "A"


def test_sqlite_store_does_not_duplicate_same_url(tmp_path):
    path = tmp_path / "items.db"
    store = Store("sqlite", path)
    item = {"titre": "A", "url": "https://example.com/1"}

    first = store.save([item, item])
    assert first == 1
    assert store.count() == 1

    second = store.save([item])
    assert second == 0
    assert store.count() == 1


def test_csv_store_appends_without_duplicate_header(tmp_path):
    path = tmp_path / "items.csv"
    store = Store("csv", path)
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    store.save([{"titre": "B", "url": "https://example.com/2"}])

    content = path.read_text(encoding="utf-8")
    assert content.count("titre,url") == 1
    assert "A" in content and "B" in content


def test_export_to_transfers_all_items(tmp_path):
    source_path = tmp_path / "items.json"
    target_path = tmp_path / "items.db"

    source = Store("json", source_path)
    source.save([
        {"titre": "A", "url": "https://example.com/1"},
        {"titre": "B", "url": "https://example.com/2"},
    ])

    exported = source.export_to("sqlite", target_path)
    assert exported == 2

    target = Store("sqlite", target_path)
    assert target.count() == 2
def test_save_empty_list_returns_zero(tmp_path):
    store = Store("json", tmp_path / "items.json")
    assert store.save([]) == 0


def test_count_csv_backend(tmp_path):
    store = Store("csv", tmp_path / "items.csv")
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    assert store.count() == 1


def test_count_json_backend(tmp_path):
    store = Store("json", tmp_path / "items.json")
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    assert store.count() == 1


def test_export_to_unknown_backend_raises(tmp_path):
    store = Store("json", tmp_path / "items.json")
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    with pytest.raises(ValueError):
        store.export_to("xml", tmp_path / "out.xml")


def test_export_from_csv_backend(tmp_path):
    source = Store("csv", tmp_path / "items.csv")
    source.save([{"titre": "A", "url": "https://example.com/1"}])
    exported = source.export_to("json", tmp_path / "out.json")
    assert exported == 1


def test_export_from_sqlite_backend(tmp_path):
    source = Store("sqlite", tmp_path / "items.db")
    source.save([{"titre": "A", "url": "https://example.com/1"}])
    exported = source.export_to("json", tmp_path / "out.json")
    assert exported == 1


def test_save_csv_skips_duplicate_url(tmp_path):
    store = Store("csv", tmp_path / "items.csv")
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    inserted = store.save([{"titre": "A-bis", "url": "https://example.com/1"}])
    assert inserted == 0


def test_read_csv_when_file_missing(tmp_path):
    store = Store("csv", tmp_path / "missing.csv")
    assert store._read_csv() == []


def test_save_sqlite_adds_url_column_when_missing(tmp_path):
    store = Store("sqlite", tmp_path / "items.db")
    inserted = store.save([{"titre": "Sans URL"}])
    assert inserted == 1


def test_count_sqlite_when_file_missing(tmp_path):
    store = Store("sqlite", tmp_path / "missing.db")
    assert store.count() == 0


def test_count_sqlite_when_table_missing(tmp_path):
    db_path = tmp_path / "empty.db"
    db_path.touch()
    store = Store("sqlite", db_path)
    assert store.count() == 0


def test_read_sqlite_returns_items(tmp_path):
    store = Store("sqlite", tmp_path / "items.db")
    store.save([{"titre": "A", "url": "https://example.com/1"}])
    items = store._read_sqlite()
    assert items == [{"titre": "A", "url": "https://example.com/1"}]


def test_read_sqlite_when_file_missing(tmp_path):
    store = Store("sqlite", tmp_path / "missing.db")
    assert store._read_sqlite() == []


def test_read_json_on_empty_file(tmp_path):
    path = tmp_path / "empty.json"
    path.touch()
    store = Store("json", path)
    assert store._read_json() == []