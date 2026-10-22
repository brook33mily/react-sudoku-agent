
"""Local Ollama policy for the Sudoku ReAct agent."""

import json
import urllib.request


SYSTEM_PROMPT = """
You are a Sudoku ReAct agent.

Choose exactly ONE tool request per turn.
Return only a JSON object, without markdown.

Available tools:
- {"tool":"inspect","scope":"board"}
- {"tool":"inspect","scope":"cell","row":0,"column":0}
- {"tool":"place","row":0,"column":0,"digit":1}
- {"tool":"undo"}
- {"tool":"add_fact","atom":"A"}
- {"tool":"add_rule","premises":["A"],"conclusion":"B"}
- {"tool":"query","atom":"A"}
- {"tool":"submit"}

Sudoku rules:
Each row, column, and 3x3 box must contain digits 1-9 once.
Zero represents an empty cell.

Inspect the board before making placements.
Never change given clues.
Only submit when the board is completely solved.
"""


class OllamaPolicy:
    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model

    def next_request(self, observation, trace, remaining_actions):
        if observation is None:
            context = "No observations yet. Inspect the board."
        else:
            context = (
                f"Previous observation: {observation!r}\n"
                f"Recent trace: {trace[-5:]!r}\n"
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
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0},
        }

        data = json.dumps(payload).encode("utf-8")

        http_request = urllib.request.Request(
            "http://127.0.0.1:11434/api/chat",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(http_request, timeout=120) as response:
            result = json.load(response)

        content = result["message"]["content"]

        try:
            return json.loads(content)
        except (ValueError, TypeError):
            # Let the controller reject malformed output.
            return {"tool": "invalid_model_output"}
