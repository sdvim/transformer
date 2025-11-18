from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List


class BaseExporter(ABC):
    """Abstract base class for all exporters."""

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """Returns True if this exporter can handle the given file extension."""
        pass

    @abstractmethod
    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """
        Export data to file.

        Args:
            data: List of dictionaries to export
            output_path: Destination file path

        Raises:
            ExportError: If export fails
        """
        pass
