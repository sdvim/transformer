import csv
from pathlib import Path
from typing import Any, Dict, List

from transformer.exporters.base import BaseExporter
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class CSVExporter(BaseExporter):
    """Export data to CSV format."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".csv"

    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Export data to CSV file."""
        if not data:
            logger.warning("no_data_to_export")
            return

        # Get all unique keys across all dictionaries
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(fieldnames)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        logger.info("csv_export_complete", path=str(output_path), rows=len(data))
