"""Black-box cases from specs/knowledge_base_contract.md."""
from src.knowledge_base import KnowledgeBase

def test_unknown_proposition_is_unresolved():
    assert KnowledgeBase().query('A').status == 'unresolved'

def test_fact_is_entailed_and_revision_advances():
    kb = KnowledgeBase()
    assert kb.add_fact('A').accepted
    assert kb.revision == 1 and kb.query('A').status == 'entailed'

def test_explicit_negation_contradicts_query():
    kb = KnowledgeBase()
    assert kb.add_fact('!A').accepted
    assert kb.query('A').status == 'contradicted'

def test_multiple_premises_are_required():
    kb = KnowledgeBase()
    kb.add_rule(['A','B'], 'C')
    kb.add_fact('A')
    assert kb.query('C').status == 'unresolved'
    kb.add_fact('B')
    assert kb.query('C').status == 'entailed'

def test_reject_contradictory_update_without_mutation():
    kb = KnowledgeBase()
    kb.add_fact('A')
    before = kb.revision
    result = kb.add_fact('!A')
    assert result.accepted is False
    assert kb.revision == before and kb.query('A').status == 'entailed'

def test_duplicate_fact_is_idempotent():
    kb = KnowledgeBase()
    kb.add_fact('A')
    result = kb.add_fact('A')
    assert result.accepted and result.changed is False and kb.revision == 1

def test_invalid_fact_syntax_is_rejected():
    kb = KnowledgeBase()
    result = kb.add_fact('1bad')
    assert result.accepted is False and result.reason == 'INVALID_LITERAL'
    assert kb.revision == 0

def test_cyclic_rules_terminate():
    kb = KnowledgeBase()
    kb.add_rule(['A'],'B')
    kb.add_rule(['B'],'A')
    kb.add_fact('A')
    assert kb.query('B').status == 'entailed'

def test_query_does_not_mutate_revision():
    kb = KnowledgeBase()
    kb.query('Unknown')
    assert kb.revision == 0
