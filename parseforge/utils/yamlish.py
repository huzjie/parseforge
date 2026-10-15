"""Minimal YAML-subset parser (zero-dependency fallback).

Supports nested maps, block lists (``- item`` / ``- key: value``), inline
comments and blank lines. Intentionally tiny -- NOT a full YAML parser.
"""
import re


def _strip_comment(line):
    for i, ch in enumerate(line):
        if ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i]
    return line


def _indent_of(line):
    return len(line) - len(line.lstrip(" "))


def _parse_scalar(s):
    s = s.strip()
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if s in ("null", "~", ""):
        return None
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    if s.startswith("[") and s.endswith("]"):
        inner = s[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(x) for x in inner.split(",")]
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return s


def parse(text):
    """Parse YAML-subset text into nested dict/list structures.

    Stack entries are 5-tuples ``(indent, container, parent, key, pending)``.
    Two subtle rules (historically the "lost first list item" bug):
    1. a block list under ``key:`` replaces the placeholder dict in its *parent*;
    2. a list item only pops entries *deeper* than itself, never an equal-indent
       sibling list.
    """
    root = {}
    stack = [(-1, root, None, None, False)]

    for raw in text.splitlines():
        line = _strip_comment(raw).rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        indent = _indent_of(line)

        if stripped.startswith("- "):
            item_text = stripped[2:].strip()
            while len(stack) > 1 and stack[-1][0] > indent:
                stack.pop()
            top_indent, container, parent, key, pending = stack[-1]
            if pending and isinstance(container, dict) and not container:
                lst = []
                if isinstance(parent, dict):
                    parent[key] = lst
                elif isinstance(parent, list):
                    parent.append(lst)
                stack.pop()
                stack.append((indent, lst, parent, key, False))
                container = lst
            elif not isinstance(container, list):
                lst = []
                container = lst
                stack.append((indent, lst, None, None, False))
            if ":" in item_text and not item_text.startswith(("[", "{", '"', "'")):
                k, _, v = item_text.partition(":")
                d = {}
                container.append(d)
                if v.strip():
                    d[k.strip()] = _parse_scalar(v)
                else:
                    stack.append((indent, d, container, k.strip(), True))
            else:
                container.append(_parse_scalar(item_text))
        elif ":" in stripped:
            k, _, v = stripped.partition(":")
            k = k.strip()
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
            container = stack[-1][1]
            if v.strip():
                container[k] = _parse_scalar(v)
            else:
                d = {}
                container[k] = d
                stack.append((indent, d, container, k, True))
        else:
            if isinstance(stack[-1][1], list):
                stack[-1][1].append(_parse_scalar(stripped))

    return root
