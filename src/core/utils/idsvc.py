import ulid


def generate_id(prefix: str) -> str:
    """Generate a unique ID with the given prefix."""
    if len(prefix) != 1 or not prefix.isalpha() or not prefix.isupper():
        raise ValueError("Prefix must be a single uppercase letter.")  # noqa: TRY003
    return f"{prefix}{ulid.new()}"
