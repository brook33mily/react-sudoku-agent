
"""Typed tool request validation for the Sudoku ReAct agent.

Implements specs/tool_schemas.md.
Rejects unknown tools, missing fields, extra fields,
invalid coordinates, and malformed logical expressions.
"""

import re
from dataclasses import dataclass
from typing import Any


ATOM = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
LITERAL = re.compile(r"!?[A-Za-z][A-Za-z0-9_]*\Z")


@dataclass(frozen=True)
class ToolRequest:
    tool: str
    arguments: dict[str, Any]


def _index(value):
    return type(value) is int and 0 <= value <= 8


def _digit(value):
    return type(value) is int and 1 <= value <= 9


def _atom(value):
    return type(value) is str and ATOM.fullmatch(value) is not None


def _literal(value):
    return type(value) is str and LITERAL.fullmatch(value) is not None


def _fields(request, required):
    if set(request) != set(required):
        raise ValueError("Missing or unexpected request fields")


def parse_request(request) -> ToolRequest:
    """Validate one request without executing it."""

    if not isinstance(request, dict):
        raise ValueError("Tool request must be a dictionary")

    tool = request.get("tool")

    if type(tool) is not str:
        raise ValueError("Missing or invalid tool name")

    if tool == "inspect":
        scope = request.get("scope")

        if scope == "board":
            _fields(request, {"tool", "scope"})

        elif scope == "cell":
            _fields(request, {"tool", "scope", "row", "column"})

            if not _index(request["row"]) or not _index(request["column"]):
                raise ValueError("Invalid cell coordinates")

        elif scope in {"row", "column", "box"}:
            _fields(request, {"tool", "scope", "index"})

            if not _index(request["index"]):
                raise ValueError("Invalid inspection index")

        else:
            raise ValueError("Unknown inspection scope")

    elif tool == "place":
        _fields(request, {"tool", "row", "column", "digit"})

        if not _index(request["row"]) or not _index(request["column"]):
            raise ValueError("Invalid placement coordinates")

        if not _digit(request["digit"]):
            raise ValueError("Invalid placement digit")

    elif tool == "undo":
        _fields(request, {"tool"})

    elif tool == "add_fact":
        _fields(request, {"tool", "atom"})

        if not _literal(request["atom"]):
            raise ValueError("Invalid fact literal")

    elif tool == "add_rule":
        _fields(request, {"tool", "premises", "conclusion"})

        premises = request["premises"]

        if (
            type(premises) is not list
            or not all(_literal(item) for item in premises)
            or not _literal(request["conclusion"])
        ):
            raise ValueError("Invalid logical rule")

    elif tool == "query":
        _fields(request, {"tool", "atom"})

        if not _atom(request["atom"]):
            raise ValueError("Query must contain an unsigned atom")

    elif tool == "submit":
        _fields(request, {"tool"})

    else:
        raise ValueError("Unknown tool")

    return ToolRequest(
        tool=tool,
        arguments={key: value for key, value in request.items() if key != "tool"}
    )
