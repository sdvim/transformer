from pathlib import Path

import pytest
from typer.testing import CliRunner

from transformer.cli import app

runner = CliRunner()


def test_cli_help():
    """Test CLI help command."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Transform webpages" in result.output


def test_cli_version():
    """Test version command."""
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
