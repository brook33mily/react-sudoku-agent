# V2 black-box tests (before implementation)

These tests were derived from the V1 public contracts, without consulting function bodies. They intentionally fail to import until V3 implementation exists. Keep this commit separate from implementation.

## V2 interface choices to review

V1 defines Board, Controller, and Policy names but not exact module names or result-field naming. V2 chooses:
- `src.board.Board`, `src.knowledge_base.KnowledgeBase`, `src.controller.Controller`;
- `src.tools.parse_request(mapping)` raises `ValueError` on invalid requests;
- board/KB results expose `.accepted`, `.reason`, `.changed` where relevant;
- KB queries expose `.status`;
- controller uses `.step(mapping)` and returns an observation object with `.accepted`, `.reason`, `.remaining_actions`, `.terminal`, `.terminal_reason`;
- trace entries expose `.action_number`;
- `src.agent.run_agent(policy, controller)` returns terminal reason.

These are **new V2 interface decisions**, not assertions that V1 already specified them. Before implementation, record/approve them in the corresponding specifications. `Controller.board` in tests is a read-only service reference for assertions; application code must not use it to bypass the controller.

## Run

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

Expected V2 baseline: test collection errors for missing modules. This is intentional, not evidence that the tests pass. After V3, run all tests and investigate every failure.

Note: This suite is a starting baseline, not complete coverage. Extend with KB rule-induced contradictions, signed premises, malformed constructor types, undo after rejection, terminal precedence, and local-model adapter cases.
