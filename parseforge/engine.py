"""End-to-end omni-modal parser: backend + schema validation."""
from .config import load_config
from .parse import result_schema
from .decode.json_schema import validate
from .backends import get_backend


class OmniParser:
    """High-level parse entry point.

    Usage::

        from parseforge import OmniParser, Config
        from parseforge.oracle import synthesize_document

        parser = OmniParser(Config())
        doc = synthesize_document("doc-0", n_regions=8)
        result = parser.parse(doc)
        print(result.to_json())
    """

    def __init__(self, cfg=None):
        self.cfg = cfg if cfg is not None else load_config(None)
        self.backend = get_backend(self.cfg.model.name, self.cfg)

    def parse(self, document):
        result = self.backend.parse(document)
        ok, err = validate(result.as_dict(), result_schema())
        result.schema_valid = ok
        return result

    def train_step(self):
        """One training step for the trainable backend (mock)."""
        return self.backend.train_step()

    @property
    def skill(self):
        return getattr(self.backend, "skill", None)

    @property
    def backend_name(self):
        return self.backend.name
