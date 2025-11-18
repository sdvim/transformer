from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from icalendar import Calendar, Event

from transformer.exporters.base import BaseExporter
from transformer.utils.logging import get_logger

logger = get_logger(__name__)


class ICalExporter(BaseExporter):
    """Export data to iCalendar format."""

    def can_handle(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in (".ics", ".ical")

    def export(self, data: List[Dict[str, Any]], output_path: Path) -> None:
        """Export data to iCalendar file."""
        cal = Calendar()
        cal.add("prodid", "-//Transformer//transformer//EN")
        cal.add("version", "2.0")

        for item in data:
            event = Event()

            # Required fields
            event.add("summary", item.get("title", item.get("text", "Event")))

            # Optional fields
            if "start" in item:
                event.add("dtstart", self._parse_date(item["start"]))
            if "end" in item:
                event.add("dtend", self._parse_date(item["end"]))
            if "location" in item:
                event.add("location", item["location"])
            if "description" in item:
                event.add("description", item["description"])

            cal.add_component(event)

        with open(output_path, "wb") as f:
            f.write(cal.to_ical())

        logger.info("ical_export_complete", path=str(output_path), events=len(data))

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime object."""
        # Add more sophisticated date parsing as needed
        try:
            return datetime.fromisoformat(date_str)
        except:
            return datetime.now()
