from pathlib import Path
from typing import Optional

import typer

from transformer.core.factory import ScraperFactory
from transformer.exporters import get_exporter
from transformer.scrapers import get_site_scraper
from transformer.utils.errors import TransformerError
from transformer.utils.logging import get_logger, setup_logging

setup_logging()
logger = get_logger(__name__)

app = typer.Typer(
    name="transform", help="Transform webpages into arbitrary file types", add_completion=False
)


@app.command()
def transform(
    url: str = typer.Argument(..., help="URL to scrape"),
    output: Path = typer.Option(..., "--output", "-o", help="Output file path"),
    selector: Optional[str] = typer.Option(
        None, "--selector", "-s", help="CSS selector for elements"
    ),
    dynamic: bool = typer.Option(
        False, "--dynamic", "-d", help="Force dynamic scraping (JavaScript)"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """
    Transform webpage data into various file formats.

    Examples:

      transform https://youtube.com/playlist?list=xyz -o playlist.csv

      transform https://goodreads.com/shelf/to-read -o books.md

      transform https://example.com -s "div.content" -o data.json
    """
    try:
        # Try site-specific scraper first
        scraper = get_site_scraper(url)
        if scraper:
            logger.info("using_site_specific_scraper", url=url)
        else:
            # Fall back to generic scraper
            scraper = ScraperFactory.get_scraper(url, force_dynamic=dynamic)
            logger.info("using_generic_scraper", url=url, dynamic=dynamic)

        # Scrape data
        typer.echo(f"Scraping {url}...")
        data = scraper.scrape(url, selector)

        if not data:
            typer.echo("No data extracted", err=True)
            raise typer.Exit(1)

        typer.echo(f"Extracted {len(data)} items")

        # Export data
        exporter = get_exporter(output)
        typer.echo(f"Exporting to {output}...")
        exporter.export(data, output)

        typer.echo(f"Success! Saved to {output}")

    except TransformerError as e:
        logger.error("transform_error", error=str(e))
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        logger.exception("unexpected_error")
        typer.echo(f"Unexpected error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information."""
    typer.echo("transformer 0.1.0")


if __name__ == "__main__":
    app()
