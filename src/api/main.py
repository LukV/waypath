from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    """Print a greeting."""
    return {"message": "Hello World"}
