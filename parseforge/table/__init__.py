"""Table recognition: detect grid structure and emit structured cells."""
from .structure import TableStructure
from .cells import cell_text, cells_to_rows
from .span import detect_spans

__all__ = ["TableStructure", "cell_text", "cells_to_rows", "detect_spans"]
