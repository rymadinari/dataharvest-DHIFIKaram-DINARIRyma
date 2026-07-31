"""
store.py -- Persistance des items valides. Trois backends : csv, sqlite, json.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path


class Store:
    BACKENDS = ("csv", "sqlite", "json")

    def __init__(self, backend: str, path: str):
        if backend not in self.BACKENDS:
            raise ValueError(f"Backend inconnu: {backend}")
        self.backend = backend
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # API publique
    # ------------------------------------------------------------------ #
    def save(self, items: list[dict]) -> int:
        """Persiste les items. Retourne le nombre d'items inseres (hors doublons)."""
        if not items:
            return 0
        if self.backend == "csv":
            return self._save_csv(items)
        if self.backend == "sqlite":
            return self._save_sqlite(items)
        return self._save_json(items)

    def count(self) -> int:
        """Retourne le nombre total d'items dans le store."""
        if self.backend == "csv":
            return len(self._read_csv())
        if self.backend == "sqlite":
            return self._count_sqlite()
        return len(self._read_json())

    def export_to(self, other_backend: str, path: str) -> int:
        """Exporte tous les items vers un autre backend. Retourne le nb exporte."""
        if other_backend not in self.BACKENDS:
            raise ValueError(f"Backend inconnu: {other_backend}")

        if self.backend == "csv":
            items = self._read_csv()
        elif self.backend == "sqlite":
            items = self._read_sqlite()
        else:
            items = self._read_json()

        target = Store(other_backend, path)
        return target.save(items)

    # ------------------------------------------------------------------ #
    # CSV
    # ------------------------------------------------------------------ #
    def _save_csv(self, items: list[dict]) -> int:
        is_new = not self.path.exists() or self.path.stat().st_size == 0
        existing_urls = {row.get("url") for row in self._read_csv()} if not is_new else set()

        fieldnames = list(items[0].keys())
        inserted = 0
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if is_new:
                writer.writeheader()
            for item in items:
                if item.get("url") in existing_urls:
                    continue
                writer.writerow(item)
                existing_urls.add(item.get("url"))
                inserted += 1
        return inserted

    def _read_csv(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    # ------------------------------------------------------------------ #
    # SQLite
    # ------------------------------------------------------------------ #
    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _ensure_table(self, conn: sqlite3.Connection, columns: list[str]) -> None:
        cols_sql = ", ".join(f'"{c}" TEXT' for c in columns if c != "url")
        conn.execute(
            f'CREATE TABLE IF NOT EXISTS items ('
            f'id INTEGER PRIMARY KEY AUTOINCREMENT, '
            f'"url" TEXT UNIQUE, '
            f'{cols_sql})'
        )

    def _save_sqlite(self, items: list[dict]) -> int:
        columns = list(items[0].keys())
        if "url" not in columns:
            columns = ["url"] + columns

        conn = self._connect()
        try:
            self._ensure_table(conn, columns)
            inserted = 0
            for item in items:
                cols = list(item.keys())
                placeholders = ", ".join("?" for _ in cols)
                col_names = ", ".join(f'"{c}"' for c in cols)
                cur = conn.execute(
                    f'INSERT OR IGNORE INTO items ({col_names}) VALUES ({placeholders})',
                    [item[c] for c in cols],
                )
                if cur.rowcount:
                    inserted += 1
            conn.commit()
            return inserted
        finally:
            conn.close()

    def _count_sqlite(self) -> int:
        if not self.path.exists():
            return 0
        conn = self._connect()
        try:
            cur = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='items'"
            )
            if cur.fetchone()[0] == 0:
                return 0
            return conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        finally:
            conn.close()

    def _read_sqlite(self) -> list[dict]:
        if not self.path.exists():
            return []
        conn = self._connect()
        try:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='items'"
            )
            if cur.fetchone()[0] == 0:
                return []
            rows = conn.execute("SELECT * FROM items").fetchall()
            return [{k: v for k, v in dict(row).items() if k != "id"} for row in rows]
        finally:
            conn.close()

    # ------------------------------------------------------------------ #
    # JSON
    # ------------------------------------------------------------------ #
    def _save_json(self, items: list[dict]) -> int:
        existing = self._read_json()
        existing_urls = {row.get("url") for row in existing}

        inserted = 0
        for item in items:
            if item.get("url") in existing_urls:
                continue
            existing.append(item)
            existing_urls.add(item.get("url"))
            inserted += 1

        with self.path.open("w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        return inserted

    def _read_json(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
