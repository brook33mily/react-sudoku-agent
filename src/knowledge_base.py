
"""Propositional knowledge-base service.

Implements specs/knowledge_base_contract.md.

Supports signed literals, Horn-style rules, forward chaining,
consistency checks, and three-valued query results.
"""

import re
from dataclasses import dataclass
from typing import Sequence


ATOM_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9_]*\Z")
LITERAL_PATTERN = re.compile(r"!?[A-Za-z][A-Za-z0-9_]*\Z")


@dataclass(frozen=True)
class KBResult:
    accepted: bool
    reason: str
    changed: bool
    revision: int


@dataclass(frozen=True)
class QueryResult:
    status: str
    revision: int


class KnowledgeBase:
    def __init__(self):
        self._facts = set()
        self._rules = set()
        self.revision = 0

    @staticmethod
    def _valid_literal(literal):
        return (
            isinstance(literal, str)
            and LITERAL_PATTERN.fullmatch(literal) is not None
        )

    @staticmethod
    def _valid_atom(atom):
        return (
            isinstance(atom, str)
            and ATOM_PATTERN.fullmatch(atom) is not None
        )

    @staticmethod
    def _opposite(literal):
        if literal.startswith("!"):
            return literal[1:]
        return "!" + literal

    @classmethod
    def _closure(cls, facts, rules):
        """Compute the least fixed point of all accepted rules."""
        known = set(facts)

        changed = True
        while changed:
            changed = False

            for premises, conclusion in rules:
                if set(premises).issubset(known):
                    if conclusion not in known:
                        known.add(conclusion)
                        changed = True

        return known

    @classmethod
    def _consistent(cls, facts, rules):
        known = cls._closure(facts, rules)

        return all(
            cls._opposite(literal) not in known
            for literal in known
        )

    def add_fact(self, literal: str) -> KBResult:
        if not self._valid_literal(literal):
            return KBResult(
                False, "INVALID_LITERAL", False, self.revision
            )

        if literal in self._facts:
            return KBResult(True, "OK", False, self.revision)

        proposed_facts = self._facts | {literal}

        if not self._consistent(proposed_facts, self._rules):
            return KBResult(
                False, "INCONSISTENT", False, self.revision
            )

        self._facts.add(literal)
        self.revision += 1

        return KBResult(True, "OK", True, self.revision)

    def add_rule(
        self,
        premises: Sequence[str],
        conclusion: str
    ) -> KBResult:

        if (
            not isinstance(premises, (list, tuple))
            or not self._valid_literal(conclusion)
            or any(not self._valid_literal(p) for p in premises)
        ):
            return KBResult(
                False, "INVALID_RULE", False, self.revision
            )

        # Duplicate premises do not change logical meaning.
        normalized = tuple(sorted(set(premises)))
        rule = (normalized, conclusion)

        if rule in self._rules:
            return KBResult(True, "OK", False, self.revision)

        proposed_rules = self._rules | {rule}

        if not self._consistent(self._facts, proposed_rules):
            return KBResult(
                False, "INCONSISTENT", False, self.revision
            )

        self._rules.add(rule)
        self.revision += 1

        return KBResult(True, "OK", True, self.revision)

    def query(self, atom: str) -> QueryResult:
        if not self._valid_atom(atom):
            return QueryResult("INVALID_LITERAL", self.revision)

        known = self._closure(self._facts, self._rules)

        if atom in known:
            status = "entailed"
        elif "!" + atom in known:
            status = "contradicted"
        else:
            status = "unresolved"

        return QueryResult(status, self.revision)
