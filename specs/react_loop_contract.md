# ReAct loop and local policy contract (V1)

`Policy.next_request(observation, trace, remaining_actions) -> TypedToolRequest` emits exactly one valid tool request. The runner forwards each request to the controller and supplies the authoritative observation back to the policy. The runner stops immediately on terminal status, never bypasses controller validation, and never interprets model text as success.

## Local deterministic development policy

A local `LocalPolicy` is a **test double / deterministic agent**, not an LLM. It may use visible board observations and deterministic Sudoku constraint reasoning to choose inspect/place/undo/submit requests. It may not read board internals or write state directly. For predictable test fixtures it should terminate within the configured budget. To exercise the KB boundary, a fixture/test scenario should add/query facts or rules through typed tools; do not claim KB reasoning if never invoked.

## Genuine offline LLM integration (final compliance option)

A local model adapter must call a locally installed LLM and constrain its response to one schema-valid tool request (e.g., structured JSON validated by the controller). The model may see only developer prompts, tool-call history and observations. If no local model is available, document the limitation; the deterministic policy alone does not establish compliance with the assignment's model-selection requirement.

## Failure cases

Malformed policy output is passed to controller for bounded rejection rather than directly executed. Policy failure or repeated invalid output must not create an infinite loop; controller action budget remains authoritative. No external credentials required.
