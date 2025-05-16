import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from dotenv import load_dotenv
from rich import print  # noqa: A004
from rich.pretty import Pretty

from core.logic.pipeline import DocumentPipeline
from core.schemas.classifier import DocumentType
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.logging import configure_logging

if TYPE_CHECKING:
    from core.schemas.invoice import Invoice
    from core.schemas.order import Order

app = typer.Typer()
configure_logging()
load_dotenv()


@app.command()
def parse(  # noqa: PLR0913
    path: Path,
    entity: str = typer.Option("order", help="Entity type (order or invoice)"),
    parser: str = typer.Option("llamaparse", help="Document parser"),
    model: str = typer.Option("openai", help="LLM model"),
    language: str = "en",
    show: bool = False,  # noqa: FBT001, FBT002
) -> None:
    """Parse a document and extract structured data."""
    typer.echo(f"📄 Parsing '{path}' as {entity} using {model} + {parser}")

    if parser not in PARSER_REGISTRY:
        error_msg = f"Invalid parser: {parser}. Available: {list(PARSER_REGISTRY)}"
        raise typer.BadParameter(error_msg)

    if (model, entity) not in EXTRACTOR_REGISTRY:
        error_msg = f"Invalid extractor: ({model}, {entity})"
        raise typer.BadParameter(error_msg)

    asyncio.run(_parse_internal(path, language, parser, model, entity, show))


async def _parse_internal(  # noqa: PLR0913
    path: Path,
    language: str,
    parser: str,
    model: str,
    entity: str,
    show: bool,  # noqa: FBT001
) -> None:
    print("🔍 Starting parse")
    parser_instance = PARSER_REGISTRY[parser](path, language)
    print(f"🧩 Using parser: {parser_instance.__class__.__name__}")
    extractor_instance = EXTRACTOR_REGISTRY[(model, entity)]()
    print(f"🤖 Using extractor: {extractor_instance.__class__.__name__}")

    try:
        pipeline: DocumentPipeline[Any]
        result: Order | Invoice
        pipeline = DocumentPipeline[Any](
            parser=parser_instance,
            extractor=extractor_instance,
            document_type=DocumentType[entity],
        )
        result, _doc_type = await pipeline.run()
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        raise

    if show:
        print("✅ Parsed Structured Data:")
        print(Pretty(result.model_dump()))
