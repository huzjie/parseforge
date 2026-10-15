"""Synthetic document synthesis helpers (re-export of the oracle)."""
from .oracle import (
    TYPES,
    oracle_region_type,
    oracle_text,
    oracle_cell,
    oracle_series_point,
    synthesize_document,
)

__all__ = [
    "TYPES",
    "oracle_region_type",
    "oracle_text",
    "oracle_cell",
    "oracle_series_point",
    "synthesize_document",
]
