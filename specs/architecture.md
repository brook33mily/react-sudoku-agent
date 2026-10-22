# Architecture and ownership (V1)

## Modules and boundaries

| Module | Owned state | Public responsibility | May depend on |
|---|---|---|---|
| `board.py` | 9×9 cells, immutable clue mask, placement undo stack, board revision | Inspect, place, undo, validate | Standard library |
| `knowledge_base.py` | Set of facts and Horn rules, KB revision | Add fact/rule, check consistency, query | Standard library |
| `tools.py` | None | Discriminated typed request/observation schemas | Standard library |
| `controller.py` | Action counter, terminal status, ordered trace | Validate and route one request, enforce policies | Board, KB, tools |
| `agent.py` | Policy-local decision context only | Choose a request from observation and history | Tools |
| `model_adapter.py` | Local policy configuration | Adapter implementing `next_request` | Agent, tools |
| `main.py` | None beyond runtime wiring | Construct services, run loop, print result | All above |

## Authority

Only the board service writes board state; only KB service writes KB state; only controller writes action count, trace and terminal reason. A policy cannot mutate services directly or declare victory. Board validation, not model text, determines accepted completion.

## Request path

1. Policy receives previous observation, trace, and remaining budget.
2. Policy emits **one** typed tool request.
3. Controller checks terminal state, budget, schema and operation policy.
4. Controller dispatches to board or KB; service returns an observation.
5. Controller counts the request and appends an immutable trace entry.
6. Controller checks terminal conditions in documented order and returns observation/status.
7. Repeat until terminal.

## Dependency rules

Services never import the controller or policy. Policy never imports concrete board/KB implementations. The controller does not infer logical truth from agent explanations. All interactions cross typed tool boundaries.

## Open design risk

The assignment calls for a *language model* selecting tools. A deterministic local policy is useful for offline tests but does not literally satisfy that clause. Prefer a local LLM with constrained JSON/schema decoding for final submission, or obtain instructor approval for a deterministic policy. Never describe the deterministic policy as an LLM.
