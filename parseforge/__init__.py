"""parseforge - Omni-modal document parsing engine.

A zero-dependency reference implementation of the core mechanisms behind
Tencent Youtu's Youtu-Parsing-Omni 5B (an omni-modal parsing model that turns
documents, images, charts, tables and audio-video into *structured JSON* with a
single model, topping OmniDocBench at 96.96):

* **Unified omni-modal encoding**: a shared encoder projects vision patches,
  text tokens and audio frames into one token space, so a single decoder head
  can parse any modality.

* **Layout-aware parsing**: region detection (title / paragraph / table / chart /
  formula / figure) + reading order, so the output JSON preserves document flow.

* **Structured JSON decoding**: a constrained decoder keeps every generated
  token valid against a JSON schema -- tables become rows/cells, charts become
  data series, formulas become LaTeX, instead of free-form prose.

Public API:
    from parseforge import OmniParser, Config, get_backend
"""

__version__ = "0.1.0"

from .config import Config, load_config
from .engine import OmniParser
from .backends import get_backend, list_backends

__all__ = [
    "Config",
    "load_config",
    "OmniParser",
    "get_backend",
    "list_backends",
    "__version__",
]
