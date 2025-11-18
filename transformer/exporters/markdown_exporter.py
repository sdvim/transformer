from pathlib import Path
from typing import Any, Dict, List

from transformer.exporters.base import BaseExporter
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class MarkdownExporter(BaseExporter):
    """Export data to Markdown format."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".md", ".markdown")

    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Export data to Markdown file."""
        lines = []

        for item in data:
            # Create checkbox list item
            title = item.get("title", item.get("text", "Item"))
            lines.append(f"- [ ] {title}")

            # Add additional details as nested list
            for key, value in item.items():
                if key not in ("title", "text") and value:
                    lines.append(f"  - {key}: {value}")

            lines.append("")  # Blank line between items

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("markdown_export_complete", path=str(output_path), items=len(data))
