import asyncio
import os
from pathlib import Path

import typer
from llama_cloud_services import LlamaParse  # type: ignore[import-untyped]

LLAMA_CLOUD_API_KEY = os.getenv(
    "LLAMA_CLOUD_API_KEY", "llx-C0Pc1DDOlukdeKpdT6rLrJRHMGmpsgdoyMv5n5JDNu0IeDDa"
)

app = typer.Typer()


@app.command()
def parse(
    path: Path,
    language: str = "en",
    *,
    output_path: Path | None = None,
    show: bool = False,
) -> dict[str, object]:
    """Parse a document and save the structured data as JSON and optionally as .md."""
    typer.echo(f"Uploading PDF: {path}")

    markdown = asyncio.run(pdf_to_markdown(str(path), language))

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        typer.echo(f"Saved Markdown to: {output_path}")

    structured_data = asyncio.run(markdown_to_structured_json(markdown))

    if show:
        typer.echo("Parsed Structured Data:")
        typer.echo(structured_data)

    return structured_data


async def pdf_to_markdown(pdf_path: str, lang: str) -> str:
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


async def markdown_to_structured_json(markdown: str) -> dict[str, object]:
    """Convert Markdown to structured JSON (dummy for now)."""
    return {
        "title": "Simulated Document",
        "markdown": markdown,
        "sections": [
            {"heading": "Introduction", "content": "This is a simulated introduction."},
            {"heading": "Body", "content": "This is the simulated body content."},
        ],
    }


if __name__ == "__main__":
    app()
