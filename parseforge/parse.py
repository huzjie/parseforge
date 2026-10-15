"""Core data types: Document, ParseResult, and block schemas."""
from dataclasses import dataclass, field
from typing import List, Optional

import json


@dataclass
class Document:
    """A parse input: text and/or image and/or audio, plus optional layout hints."""
    doc_id: str = "doc-0"
    text: str = ""
    image: Optional[list] = None
    audio_frames: Optional[list] = None
    candidates: List[dict] = field(default_factory=list)


@dataclass
class ParseResult:
    """A parse output: ordered blocks + schema validity flag."""
    doc_id: str = ""
    blocks: List[dict] = field(default_factory=list)
    schema_valid: bool = True

    def as_dict(self):
        return {"doc_id": self.doc_id, "blocks": self.blocks,
                "schema_valid": self.schema_valid}

    def to_json(self):
        return json.dumps(self.as_dict(), ensure_ascii=False, indent=2)


def result_schema():
    """The JSON schema every ParseResult must satisfy."""
    from .decode.json_schema import Schema
    return Schema.object({
        "doc_id": {"type": "string"},
        "blocks": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "bbox": {"type": "array"},
                "content": {},
            },
        }},
        "schema_valid": {"type": "boolean"},
    }, required=["doc_id", "blocks", "schema_valid"])


BLOCK_TYPES = ["title", "text", "table", "chart", "formula", "figure"]
