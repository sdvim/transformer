from pathlib import Path
from typing import Any, Dict, List

from transformer.exporters.base import BaseExporter
from transformer.exporters.csv_exporter import CSVExporter
from transformer.exporters.ical_exporter import ICalExporter
from transformer.exporters.json_exporter import JSONExporter
from transformer.exporters.markdown_exporter import MarkdownExporter
from transformer.exporters.sqlite_exporter import SQLiteExporter
from transformer.utils.errors import ExportError

EXPORTERS: List[BaseExporter] = [
    CSVExporter(),
    JSONExporter(),
    SQLiteExporter(),
    ICalExporter(),
    MarkdownExporter(),
]


def get_exporter(output_path: Path) -> BaseExporter:
    """Get appropriate exporter for file path."""
    for exporter in EXPORTERS:
        if exporter.can_handle(output_path):
            return exporter
    raise ExportError(f"No exporter found for {output_path.suffix}")
