import asyncio
from pathlib import Path

import typer
from rich import print  # noqa: A004
from rich.pretty import Pretty

from core.logic.pipeline import DocumentPipeline
from core.services.document_parser import DocumentParser
from core.services.structuring import OrderExtractor

app = typer.Typer()


@app.command()
def hello(name: str) -> None:
    """Say hello to NAME."""
    typer.echo(f"Hello {name}!")


@app.command()
def parse(
    path: Path,
    language: str = "en",
    *,
    show: bool = False,
) -> None:
    """Parse a document and save the structured data as JSON and optionally as .md."""
    typer.echo(f"🏄 Uploading document: {path}")
    asyncio.run(_parse_internal(path, language, show))


async def _parse_internal(
    path: Path,
    language: str,
    show: bool,  # noqa: FBT001
) -> None:
    pipeline = DocumentPipeline(
        parser=DocumentParser(language=language, path=path),
        extractor=OrderExtractor(),
    )
    order = await pipeline.run()

    if show:
        typer.echo("🔥 Parsed Structured Data:")
        print(Pretty(order.model_dump()))


if __name__ == "__main__":
    app()
