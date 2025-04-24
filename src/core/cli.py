import typer

app = typer.Typer()


@app.command()
def hello(name: str = "Growing pAI") -> str:
    """Print a greeting with the provided name."""
    greeting = f"Hello {name}"
    typer.echo(greeting)
    return greeting
