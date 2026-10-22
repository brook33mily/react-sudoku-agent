
"""End-to-end Sudoku ReAct demo using local Ollama."""

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

from src.agent import run_agent
from src.board import Board
from src.controller import Controller
from src.knowledge_base import KnowledgeBase
from src.local_llm import OllamaPolicy


SOLVED = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def json_safe(value):
    """Convert dataclasses and tuples to JSON-compatible values."""
    if is_dataclass(value):
        return json_safe(asdict(value))
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    return value


def main():
    puzzle = [row.copy() for row in SOLVED]

    # One missing digit: row 0, column 2 should contain 4.
    puzzle[0][2] = 0

    board = Board(puzzle)
    kb = KnowledgeBase()
    controller = Controller(board, kb, max_actions=12)
    policy = OllamaPolicy(model="qwen2.5:0.5b")

    print("Starting Ollama Sudoku ReAct demo...")
    print("Missing cell: row 0, column 2")
    print("Action budget: 12")

    result = run_agent(policy, controller)

    print("\nExecution trace:")
    for entry in controller.trace:
        print(
            f"Action {entry.action_number}: "
            f"{entry.request} -> "
            f"{entry.observation.reason}"
        )

    print(f"\nTerminal reason: {result}")
    print(f"Actions used: {controller.used_actions}")
    print(f"Board complete: {board.validate_complete()}")

    output = {
        "model": policy.model,
        "initial_puzzle": puzzle,
        "terminal_reason": result,
        "actions_used": controller.used_actions,
        "board_complete": board.validate_complete(),
        "trace": json_safe(controller.trace),
    }

    evidence_dir = Path("docs/test-results")
    evidence_dir.mkdir(parents=True, exist_ok=True)

    path = evidence_dir / "v4-ollama-demo.json"
    path.write_text(json.dumps(output, indent=2))

    print(f"Evidence saved to: {path}")


if __name__ == "__main__":
    main()
