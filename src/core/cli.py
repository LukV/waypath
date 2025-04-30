import asyncio
import os
from pathlib import Path

import typer
from llama_cloud_services import LlamaParse  # type: ignore[import-untyped]
from pydantic_ai import Agent
from rich import print  # noqa: A004
from rich.pretty import Pretty

from api.schemas.order import Order

LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")


app = typer.Typer()


@app.command()
def parse(
    path: Path,
    language: str = "en",
    *,
    output_path: Path | None = None,
    show: bool = False,
) -> None:
    """Parse a document and save the structured data as JSON and optionally as .md."""
    typer.echo(f"🏄 Uploading PDF: {path}")
    asyncio.run(_parse_internal(path, language, output_path, show))


async def _parse_internal(
    path: Path,
    language: str,
    output_path: Path | None,
    show: bool,  # noqa: FBT001
) -> None:
    markdown = await markdown_with_llama_parse(str(path), language)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        typer.echo(f"Saved Markdown to: {output_path}")

    structured_data = await markdown_to_structured_json(markdown)

    if show:
        typer.echo("🔥 Parsed Structured Data:")
        print(Pretty(structured_data.model_dump()))


async def markdown_with_llama_parse(pdf_path: str, lang: str) -> str:
    """Convert PDF to Markdown and return raw concatenated markdown text."""
    parser = LlamaParse(
        api_key=LLAMA_CLOUD_API_KEY,
        num_workers=4,
        verbose=True,
        language=lang,
    )

    result = await parser.aparse(pdf_path)

    markdown_documents = result.get_markdown_documents(split_by_page=True)

    # Extract raw Markdown text per page and join
    return "\n\n".join(doc.text for doc in markdown_documents)


async def markdown_to_structured_json(markdown: str) -> Order:
    """Convert Markdown to structured JSON."""
    agent = Agent(
        "openai:gpt-4o",
        system_prompt="Parse the following order confirmation into structured fields.",
        output_type=Order,
    )

    result = await agent.run(markdown)
    return result.output


if __name__ == "__main__":
    app()
