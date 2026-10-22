# V2 test derivation and implementation boundary

Date: 2026-10-21

The tests were designed from the V1 observable contracts before implementation. The design covers successful behavior, boundary rejection, and state-preservation invariants. `tests/README.md` records interface naming choices that should be reflected in the contracts before V3.

| Contract | Public test module | Evidence |
|---|---|---|
| Board representation, inspection, placement, undo, completion | `test_board.py` | accepted/rejected operations, revisions, clue invariants, validation |
| KB signed facts, rules, closure, consistency | `test_knowledge_base.py` | entailment, contradiction, idempotence, cycles |
| Tagged tool schemas | `test_tools.py` | valid typed requests, malformed/extra/coerced values |
| Controller policies and terminal ordering | `test_controller.py` | budget, rejection, submission, terminal precedence, trace |
| ReAct loop | `test_agent.py` | observation-driven request loop and bounded termination |

Review checklist before implementation:
- [ ] Confirm the V2 interface decisions in `tests/README.md` against V1 contracts.
- [ ] Commit tests with no corresponding implementation bodies.
- [ ] Record `python3 -m pytest -q` baseline failure (missing imports are expected).
- [ ] Give coding agent these specifications and tests, bounded by module.
- [ ] Review diffs, run tests independently, and document corrections.
