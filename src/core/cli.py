import asyncio
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich import print  # noqa: A004
from rich.pretty import Pretty

from core.logic.pipeline import DocumentPipeline
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.logging import configure_logging

app = typer.Typer()
configure_logging()

# Load environment variables
load_dotenv()


@app.command()
def parse(
    path: Path,
    language: str = "en",
    parser: str = "llamaparse",
    model: str = "openai",
    *,
    show: bool = False,
) -> None:
    """Parse a document and extract structured data."""
    typer.echo(f"\U0001f3c4 Uploading document: {path}")

    if parser not in PARSER_REGISTRY:
        raise typer.BadParameter(  # noqa: TRY003
            f"Invalid parser: {parser}. Available: {list(PARSER_REGISTRY.keys())}"  # noqa: EM102
        )
    if model not in EXTRACTOR_REGISTRY:
        raise typer.BadParameter(  # noqa: TRY003
            f"Invalid model: {model}. Available: {list(EXTRACTOR_REGISTRY.keys())}"  # noqa: EM102
        )

    asyncio.run(_parse_internal(path, language, parser, model, show))


async def _parse_internal(
    path: Path,
    language: str,
    parser: str,
    model: str,
    show: bool,  # noqa: FBT001
) -> None:
    parser_instance = PARSER_REGISTRY[parser](path, language)
    extractor_instance = EXTRACTOR_REGISTRY[model]()

    pipeline = DocumentPipeline(
        parser=parser_instance,
        extractor=extractor_instance,
    )
    order = await pipeline.run()

    if show:
        typer.echo("\U0001f525 Parsed Structured Data:")
        print(Pretty(order.model_dump()))


if __name__ == "__main__":
    app()
