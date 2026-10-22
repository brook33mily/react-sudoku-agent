# Propositional knowledge-base contract (V1)

## Syntax

Signed literal is `atom` or `!atom`; atom matches `[A-Za-z][A-Za-z0-9_]*`. `!` is explicit classical negation, not negation-as-failure. A fact is a signed literal. A Horn-style rule is a conjunction of zero or more signed premises implying one signed conclusion. Duplicate premises are normalized. Rules and facts are immutable after acceptance.

## API

`add_fact(literal:str) -> KBResult`; `add_rule(premises:Sequence[str], conclusion:str) -> KBResult`; `query(atom:str) -> QueryResult` where query accepts only unsigned atoms. `revision` starts at zero and increments once per newly accepted addition. Duplicate additions succeed as idempotent no-ops with `changed=False` and unchanged revision.

## Entailment and consistency

Forward-chain to the least fixed point of accepted facts/rules; a rule fires when all premises are entailed. Reject any proposed addition if the closure would contain both `p` and `!p` for any atom; rejected additions preserve all state and revision. Query result: `entailed` if `p` is in closure, `contradicted` if `!p` is in closure, otherwise `unresolved`. Since accepted KB is consistent, both outcomes cannot hold simultaneously. Queries do not mutate state. Malformed literals/rules are rejected with `INVALID_LITERAL` or `INVALID_RULE`.

## Derived black-box tests (commit 2)

Unknown proposition unresolved; asserted fact entailed; explicit negation contradicts positive query; multi-premise chain works; missing premise prevents entailment; contradictory update rejected without mutation; duplicate insertion idempotent; invalid syntax rejected; cyclic rules terminate.
