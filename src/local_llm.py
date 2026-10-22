

"""Local Ollama policy for the Sudoku ReAct agent."""

import json
import urllib.request


SYSTEM_PROMPT = """
You are a Sudoku-solving ReAct agent.

Return exactly ONE JSON tool request per turn.
Do not include explanations or markdown.

SUDOKU RULES:
- Rows and columns use zero-based indexing (0 through 8).
- A zero represents an empty Sudoku cell.
- Every row, column, and 3x3 box must contain digits 1-9.
- Never place a digit in an occupied cell.
- Never repeat an action that was rejected.

YOUR PROCEDURE:
1. If you have not inspected the board, inspect it.
2. When legal candidate placements are provided, choose
   exactly ONE of the supplied JSON requests.
3. Copy the chosen request exactly.
4. After placing a digit, inspect the board again.
5. When the board contains no zeros, submit.

AVAILABLE TOOLS:

Inspect the board:
{"tool":"inspect","scope":"board"}

Place a digit:
Choose an exact JSON request from the candidate list.

Submit the completed puzzle:
{"tool":"submit"}

IMPORTANT:
- Do not invent coordinates or digits.
- Do not use knowledge-base tools in this demonstration.
- Do not call undo unless correcting a previous placement.
- Do not repeatedly inspect an unchanged board.
- Your goal is to SOLVE THE SUDOKU.
"""


def candidate_moves(grid):
    """Find legal placements using an observed 9x9 Sudoku grid."""
    moves = []

    for row in range(9):
        for column in range(9):
            if grid[row][column] != 0:
                continue

            used = set(grid[row])
            used.update(grid[r][column] for r in range(9))

            box_row = (row // 3) * 3
            box_col = (column // 3) * 3

            for r in range(box_row, box_row + 3):
                for c in range(box_col, box_col + 3):
                    used.add(grid[r][c])

            options = [
                digit
                for digit in range(1, 10)
                if digit not in used
            ]

            for digit in options:
                moves.append({
                    "tool": "place",
                    "row": row,
                    "column": column,
                    "digit": digit,
                })

    return moves


def extract_grid(payload):
    """Extract a 9x9 grid from a board inspection result."""
    grid = payload

    if isinstance(grid, dict):
        grid = grid.get("grid", grid.get("board"))

    if not isinstance(grid, (list, tuple)) or len(grid) != 9:
        return None

    if not all(
        isinstance(row, (list, tuple))
        and len(row) == 9
        for row in grid
    ):
        return None

    return grid


class OllamaPolicy:
    """Policy that asks a local Ollama model to select tool actions."""

    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model

    def next_request(self, observation, trace, remaining_actions):
        """Ask Ollama to select the next ReAct tool request."""

        if observation is None:
            context = (
                "You have not inspected the board yet.\n"
                'Choose {"tool":"inspect","scope":"board"}.\n'
            )

        else:
            context = (
                f"Previous tool: {observation.tool}\n"
                f"Accepted: {observation.accepted}\n"
                f"Result: {observation.reason}\n"
                f"Recent actions: "
                f"{[entry.request for entry in trace[-5:]]}\n"
            )

            if (
                observation.tool == "inspect"
                and observation.accepted
            ):
                grid = extract_grid(observation.payload)

                if grid is not None:
                    moves = candidate_moves(grid)

                    if moves:
                        context += (
                            "\nACTION SELECTION REQUIRED.\n"
                            "The board has already been inspected.\n"
                            "Do NOT inspect again.\n"
                            "Do NOT choose undo or knowledge-base tools.\n"
                            "Choose exactly ONE placement from this list:\n"
                            f"{json.dumps(moves[:20])}\n"
                            "Return the selected JSON object exactly.\n"
                            "Do not invent coordinates or digits.\n"
                        )

                    elif all(0 not in row for row in grid):
                        context += (
                            "\nThe board contains no empty cells.\n"
                            'Choose {"tool":"submit"}.\n'
                        )

                    else:
                        context += (
                            "\nNo legal placements found, "
                            "but the board is incomplete.\n"
                            "Do not submit.\n"
                        )

                else:
                    context += (
                        "\nCould not extract a 9x9 grid "
                        "from the inspection result.\n"
                    )

                

            else:
                context += (
                    "\nPrevious observation data:\n"
                    f"{json.dumps(observation.payload, default=str)}\n"
                    "Inspect the board to see its current state.\n"
                )

        prompt = (
            f"{context}\n"
            f"Remaining actions: {remaining_actions}\n"
            "Choose the next tool request. Return JSON only."
        )

        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "options": {
                "temperature": 0,
            },
        }

        data = json.dumps(payload).encode("utf-8")

        http_request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=data,
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        with urllib.request.urlopen(
            http_request,
            timeout=120,
        ) as response:
            result = json.load(response)

        content = result["message"]["content"]

        try:
            return json.loads(content)

        except (ValueError, TypeError):
            # The controller will reject invalid tool requests.
            return {
                "tool": "invalid_model_output",
            }
