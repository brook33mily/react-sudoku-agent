# Typed tool interface contract (V1)

Coordinates are **zero-based integers 0..8** throughout the API. Digits are integers 1..9. Requests are tagged unions keyed by `tool`; unknown fields and coercions (including booleans as integers) are rejected.

| Tool | Required typed arguments | Response payload |
|---|---|---|
| `inspect` | `scope`: `board`/`cell`/`row`/`column`/`box`; `index` for row/column/box, or `row`,`column` for cell | selected values and board revision |
| `place` | `row:int`, `column:int`, `digit:int` | accepted/reason, revision |
| `undo` | no arguments | accepted/reason, revision |
| `add_fact` | `atom:str` | accepted/reason, KB revision |
| `add_rule` | `premises:list[str]`, `conclusion:str` | accepted/reason, KB revision |
| `query` | `atom:str` | `entailed`/`contradicted`/`unresolved`, KB revision |
| `submit` | no arguments | accepted/reason and terminal outcome |

Every controller observation includes `tool`, `accepted`, `reason`, `remaining_actions`, `terminal`, `terminal_reason`, and operation-specific payload. Rejections never mutate board or KB. The controller logs rejected requests. All requests, including rejected requests, consume one action when the controller is active; calls after terminal status are not executed or counted.

An atom matches `[A-Za-z][A-Za-z0-9_]*` and is case-sensitive. A fact is a positive atom; explicit negation is represented by `not_<atom>` only at the API syntax level? **No**: to avoid ambiguity, use signed literals `atom` and `!atom`, where `atom` matches the regex above. Queries use an unsigned atom and return contradiction when `!atom` is entailed. Rule premises and conclusions may be signed literals. The `!` prefix is the only negation syntax.
