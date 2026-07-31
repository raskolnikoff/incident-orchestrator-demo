"""
_schema_lite.py — Minimal, stdlib-only JSON Schema (draft 2020-12 subset)
validator.

Supports exactly the schema features used under schemas/ in this
repository: type, required, properties, items, enum, minItems, minimum,
pattern, not, and additionalProperties. This is
not a general-purpose validator; it exists so the test suite and
scripts/validate_examples.py can check example JSON payloads against
schemas/*.json without a third-party `jsonschema` dependency.
"""
from __future__ import annotations

import re

_TYPE_MAP = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def _check_type(value, type_spec) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    for t in types:
        py_type = _TYPE_MAP.get(t)
        if py_type is None:
            continue
        if t == "integer" and isinstance(value, bool):
            continue  # bool is a subclass of int in Python; exclude it
        if isinstance(value, py_type):
            return True
    return False


def validate(instance, schema, path: str = "$") -> list[str]:
    """Return a list of human-readable validation error strings (empty if
    the instance conforms to the supported schema subset)."""
    errors: list[str] = []

    if "type" in schema and not _check_type(instance, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(instance).__name__}")
        return errors  # further checks are unreliable once the type is wrong

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

    if "not" in schema:
        sub_errors = validate(instance, schema["not"], path)
        if not sub_errors:
            errors.append(f"{path}: value {instance!r} matches a disallowed 'not' schema")

    if "pattern" in schema and isinstance(instance, str):
        if not re.match(schema["pattern"], instance):
            errors.append(f"{path}: value {instance!r} does not match pattern {schema['pattern']!r}")

    if "minimum" in schema and isinstance(instance, (int, float)):
        if instance < schema["minimum"]:
            errors.append(f"{path}: value {instance} is below minimum {schema['minimum']}")

    if isinstance(instance, dict):
        for req_key in schema.get("required", []):
            if req_key not in instance:
                errors.append(f"{path}: missing required property '{req_key}'")
        props = schema.get("properties", {})
        for key, val in instance.items():
            if key in props:
                errors.extend(validate(val, props[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: unexpected property '{key}'")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: expected at least {schema['minItems']} items, got {len(instance)}")
        if "items" in schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, schema["items"], f"{path}[{i}]"))

    return errors
