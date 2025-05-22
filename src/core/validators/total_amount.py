from typing import Any, Protocol, TypeVar, runtime_checkable

from core.utils.config import ObjectStatus

T = TypeVar("T")


@runtime_checkable
class HasLinesAndTotal(Protocol):  # noqa: D101
    lines: list[Any]
    total_excl_vat: float


TOTAL_AMOUNT_TOLERANCE = 0.01


def validate(entity: T) -> ObjectStatus:
    """Check if the total amount of an object is correct."""
    if isinstance(entity, HasLinesAndTotal):
        try:
            line_total = sum(getattr(line, "subtotal", 0.0) for line in entity.lines)
            if abs(line_total - entity.total_excl_vat) > TOTAL_AMOUNT_TOLERANCE:
                return ObjectStatus.NEEDS_REVIEW
        except (AttributeError, TypeError):
            # Fall through if any attribute is missing or malformed
            return ObjectStatus.NEEDS_REVIEW

    # Future: add domain-specific rules based on type(entity) if needed
    return ObjectStatus.TO_ACCEPT
