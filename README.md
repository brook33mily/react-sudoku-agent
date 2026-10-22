# ReAct Sudoku Agent — Version 1: Specifications

CS 4300 Artificial Intelligence · U0-HW-08

## Status

**Milestone 1: architecture and public behavior contracts only.** No working solver or test suite is claimed in this commit. The implementation and black-box tests belong in later, separately reviewable commits.

## Design

A local, deterministic `LocalPolicy` selects one typed tool request at a time. It is an offline ReAct-style substitute, **not a language model**. Because the assignment explicitly says a language model selects tool calls, this substitution may require instructor approval or a later genuine local LLM adapter (e.g., a locally installed model). Keep the controller and tool contracts independent of the model so a local LLM can be substituted without changing authoritative state.

See `specs/architecture.md` and the contracts in `specs/`.

## Planned setup

Python 3.11+; `pytest` for tests. No credentials or network required for the deterministic development adapter. Later implementation will expose `python -m src.main` and `python -m pytest -q`.

## Development sequence

1. Commit these architecture/specification documents first.
2. Derive black-box tests from each contract and commit them **before** implementation.
3. Give the contracts and tests to a coding agent; implement named modules and review diffs.
4. Run tests independently, record failures and revisions in `docs/development_log.md`.
5. Add a true local LLM adapter if required by the instructor; document model setup and demonstrate typed-tool selection.

## Safety

Do not commit `.env`, credentials, model service tokens, or authenticated URLs.
