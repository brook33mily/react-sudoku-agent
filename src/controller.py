
"""Bounded controller for the Sudoku ReAct agent.

Implements specs/controller_contract.md.
Validates requests, dispatches tools, records observations,
and enforces terminal conditions and action budgets.
"""

from dataclasses import dataclass
from typing import Any

from .tools import parse_request


@dataclass(frozen=True)
class Observation:
    tool: str
    accepted: bool
    reason: str
    remaining_actions: int
    terminal: bool
    terminal_reason: str | None
    payload: Any = None


@dataclass(frozen=True)
class TraceEntry:
    action_number: int
    request: Any
    result: Any
    observation: Observation
    terminal_reason: str | None


class Controller:
    def __init__(self, board, kb, max_actions=500):
        if type(max_actions) is not int or max_actions <= 0:
            raise ValueError("max_actions must be a positive integer")

        self.board = board
        self.kb = kb
        self.max_actions = max_actions
        self.used_actions = 0
        self.trace = []
        self.terminal_reason = None

    def _observation(self, tool, accepted, reason, payload=None):
        return Observation(
            tool=tool,
            accepted=accepted,
            reason=reason,
            remaining_actions=max(
                0, self.max_actions - self.used_actions
            ),
            terminal=self.terminal_reason is not None,
            terminal_reason=self.terminal_reason,
            payload=payload,
        )

    def _dispatch(self, request):
        tool = request.tool
        args = request.arguments

        if tool == "inspect":
            scope = args["scope"]

            if scope == "board":
                payload = self.board.inspect_board()
            elif scope == "cell":
                payload = self.board.inspect_cell(
                    args["row"], args["column"]
                )
            elif scope == "row":
                payload = self.board.inspect_row(args["index"])
            elif scope == "column":
                payload = self.board.inspect_column(args["index"])
            elif scope == "box":
                payload = self.board.inspect_box(args["index"])
            else:
                raise ValueError("Invalid inspection scope")

            return True, "OK", payload

        if tool == "place":
            result = self.board.place(
                args["row"], args["column"], args["digit"]
            )
            return result.accepted, result.reason, result

        if tool == "undo":
            result = self.board.undo()
            return result.accepted, result.reason, result

        if tool == "add_fact":
            result = self.kb.add_fact(args["atom"])
            return result.accepted, result.reason, result

        if tool == "add_rule":
            result = self.kb.add_rule(
                args["premises"], args["conclusion"]
            )
            return result.accepted, result.reason, result

        if tool == "query":
            result = self.kb.query(args["atom"])
            return True, "OK", result

        if tool == "submit":
            if self.board.validate_complete():
                return True, "OK", {"solved": True}

            return False, "INVALID_SUBMISSION", {"solved": False}

        raise ValueError("Unknown tool")

    def step(self, request):
        """Execute at most one request and return its observation."""

        # Once terminal, the controller cannot be changed.
        if self.terminal_reason is not None:
            return self._observation(
                "none", False, "ALREADY_TERMINAL"
            )

        # Never execute a request after the budget is exhausted.
        if self.used_actions >= self.max_actions:
            self.terminal_reason = "ACTION_LIMIT"
            return self._observation(
                "none", False, "ACTION_LIMIT"
            )

        tool_name = (
            request.get("tool", "unknown")
            if isinstance(request, dict)
            else "unknown"
        )

        try:
            parsed = parse_request(request)
            accepted, reason, payload = self._dispatch(parsed)

        except (ValueError, TypeError, KeyError) as error:
            accepted = False
            reason = "REJECTED_REQUEST"
            payload = {"error": str(error)}

        # Every active request consumes exactly one action.
        self.used_actions += 1

        # Successful submission takes priority over the action limit.
        if reason == "OK" and tool_name == "submit" and accepted:
            self.terminal_reason = "SOLVED"

        elif tool_name == "submit" and reason == "INVALID_SUBMISSION":
            self.terminal_reason = "INVALID_SUBMISSION"

        elif self.used_actions >= self.max_actions:
            self.terminal_reason = "ACTION_LIMIT"

        observation = self._observation(
            tool_name, accepted, reason, payload
        )

        self.trace.append(
            TraceEntry(
                action_number=self.used_actions,
                request=request.copy()
                if isinstance(request, dict) else request,
                result=payload,
                observation=observation,
                terminal_reason=self.terminal_reason,
            )
        )

        return observation
