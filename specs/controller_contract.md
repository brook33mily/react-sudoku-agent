# Controller and terminal contract (V1)

## Owned state

`Controller(board, kb, max_actions=500)` owns `used_actions`, append-only trace and `terminal_reason`. `max_actions` is a positive integer. Services remain authoritative for their own state.

## Policies

Only one typed request per step. Validate tagged schema and bounds before dispatch. Unknown tool, malformed args or policy violation returns `REJECTED_REQUEST` with a specific reason; active rejections count toward the budget and are traced. Inspect and query are permitted anytime while active. Place, undo, KB additions and submit route to services. The controller does not silently repair requests or mutate state on rejection.

## Ordered terminal checks

1. If already terminal before request, return existing terminal status without dispatch/counting.
2. If action budget already exhausted before request, set `ACTION_LIMIT` and do not dispatch.
3. Validate/dispatch exactly one request, count it, append trace and obtain observation.
4. If request was `submit` and board validation succeeded, set `SOLVED`.
5. If request was `submit` and validation failed, set `INVALID_SUBMISSION` (terminal).
6. Otherwise if `used_actions >= max_actions`, set `ACTION_LIMIT`.
7. Otherwise remain active.

A successful submission on the final allowed action is `SOLVED` (submission check precedes exhaustion). A rejected request on the final action ends as `ACTION_LIMIT`. There is no model-authored terminal state.

## Trace

Every active request produces one ordered entry with request, accepted/rejected result, observation, action number and resulting terminal status. Returned observations include remaining budget. No credentials or untrusted model prose are stored as authority.

## Derived tests (commit 2)

Invalid tool consumes budget without mutation; accepted tool dispatches exactly once; submit incomplete board terminates invalid; final-budget successful submit wins over limit; rejected final-budget action ends at limit; calls after terminal are inert; trace ordering and action numbers are correct.
