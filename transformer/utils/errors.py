class TransformerError(Exception):
    """Base exception for transformer errors."""

    pass


class ScrapeError(TransformerError):
    """Error during scraping."""

    pass


class TransientError(ScrapeError):
    """Retryable error (network, rate limit)."""

    pass


class ClientError(ScrapeError):
    """Non-retryable error (403, 404, invalid selector)."""

    pass


class ParsingError(ScrapeError):
    """Data extraction error."""

    pass


class ExportError(TransformerError):
    """Error during export."""

    pass
