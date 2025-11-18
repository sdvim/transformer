import sqlite3
from pathlib import Path
from typing import Any, Dict, List

from transformer.exporters.base import BaseExporter
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class SQLiteExporter(BaseExporter):
    """Export data to SQLite database."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".db", ".sqlite", ".sqlite3")

    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Export data to SQLite database."""
        if not data:
            return

        conn = sqlite3.connect(output_path)
        cursor = conn.cursor()

        # Create table from first item's keys
        columns = list(data[0].keys())
        column_defs = ", ".join([f'"{col}" TEXT' for col in columns])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS items ({column_defs})")

        # Insert data
        placeholders = ", ".join(["?" for _ in columns])
        for item in data:
            values = [str(item.get(col, "")) for col in columns]
            cursor.execute(f"INSERT INTO items VALUES ({placeholders})", values)

        conn.commit()
        conn.close()

        logger.info("sqlite_export_complete", path=str(output_path), rows=len(data))
