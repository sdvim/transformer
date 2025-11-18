import csv
import json
import sqlite3
from pathlib import Path

import pytest

from transformer.exporters import (
    CSVExporter,
    ICalExporter,
    JSONExporter,
    MarkdownExporter,
    SQLiteExporter,
)


def test_csv_exporter(tmp_path, sample_data):
    """Test CSV export."""
    output = tmp_path / "test.csv"
    exporter = CSVExporter()

    assert exporter.can_handle(output)
    exporter.export(sample_data, output)

    # Verify CSV content
    with open(output) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["title"] == "Item 1"


def test_json_exporter(tmp_path, sample_data):
    """Test JSON export."""
    output = tmp_path / "test.json"
    exporter = JSONExporter()

    exporter.export(sample_data, output)

    # Verify JSON content
    with open(output) as f:
        data = json.load(f)
        assert len(data) == 2
        assert data[0]["title"] == "Item 1"


def test_sqlite_exporter(tmp_path, sample_data):
    """Test SQLite export."""
    output = tmp_path / "test.db"
    exporter = SQLiteExporter()

    exporter.export(sample_data, output)

    # Verify database content
    conn = sqlite3.connect(output)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    assert len(rows) == 2
    conn.close()


def test_markdown_exporter(tmp_path, sample_data):
    """Test Markdown export."""
    output = tmp_path / "test.md"
    exporter = MarkdownExporter()

    exporter.export(sample_data, output)

    # Verify markdown content
    content = output.read_text()
    assert "- [ ] Item 1" in content
    assert "- [ ] Item 2" in content


def test_ical_exporter(tmp_path):
    """Test iCalendar export."""
    output = tmp_path / "test.ics"
    exporter = ICalExporter()

    data = [
        {
            "title": "Meeting",
            "start": "2024-01-15T10:00:00",
            "end": "2024-01-15T11:00:00",
            "location": "Office",
        }
    ]

    exporter.export(data, output)

    # Verify file was created
    assert output.exists()
    content = output.read_bytes()
    assert b"BEGIN:VCALENDAR" in content
    assert b"Meeting" in content
