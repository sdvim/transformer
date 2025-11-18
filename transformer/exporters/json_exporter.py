import json
from pathlib import Path
from typing import Any, Dict, List

from transformer.exporters.base import BaseExporter
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class JSONExporter(BaseExporter):
    """Export data to JSON format."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".json"

    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Export data to JSON file."""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info("json_export_complete", path=str(output_path), items=len(data))
