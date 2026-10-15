"""A tiny JSON-schema validator for the parse output.

The parse engine emits dictionaries/lists/scalars. This validator checks a
subset of JSON Schema (type / items / required / properties) so the decoder can
guarantee *structural* validity even when the underlying model is imperfect --
that is the whole point of structured extraction.
"""
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Schema:
    spec: Dict[str, Any]

    @classmethod
    def object(cls, properties, required=None):
        return cls({"type": "object", "properties": properties,
                    "required": required or list(properties.keys())})

    @classmethod
    def array(cls, items):
        return cls({"type": "array", "items": items})


def _type_name(v):
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "null"


def validate(instance, schema: Schema):
    """Return (ok, error). Checks type / properties / required / items."""
    return _validate(instance, schema.spec)


def _validate(inst, spec):
    if isinstance(spec, dict) and "type" in spec:
        expected = spec["type"]
        actual = _type_name(inst)
        if expected == "number" and actual == "number":
            pass
        elif actual != expected:
            return False, "type %s != %s" % (actual, expected)
        if expected == "object" and "properties" in spec:
            if not isinstance(inst, dict):
                return False, "not object"
            for req in spec.get("required", []):
                if req not in inst:
                    return False, "missing required %s" % req
            for k, subspec in spec["properties"].items():
                if k in inst and inst[k] is not None:
                    ok, err = _validate(inst[k], subspec)
                    if not ok:
                        return False, "%s: %s" % (k, err)
        elif expected == "array" and "items" in spec:
            if not isinstance(inst, list):
                return False, "not array"
            for item in inst:
                ok, err = _validate(item, spec["items"])
                if not ok:
                    return False, err
        return True, ""
    if isinstance(spec, dict) and "properties" in spec:
        if not isinstance(inst, dict):
            return False, "not object"
        for req in spec.get("required", []):
            if req not in inst:
                return False, "missing required %s" % req
        for k, subspec in spec["properties"].items():
            if k in inst and inst[k] is not None:
                ok, err = _validate(inst[k], subspec)
                if not ok:
                    return False, "%s: %s" % (k, err)
        return True, ""
    if isinstance(spec, dict) and "items" in spec:
        if not isinstance(inst, list):
            return False, "not array"
        for item in inst:
            ok, err = _validate(item, spec["items"])
            if not ok:
                return False, err
        return True, ""
    return True, ""
