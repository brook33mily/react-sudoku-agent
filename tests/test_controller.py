"""Black-box cases from specs/controller_contract.md.

V2 interface decision: Controller.step accepts a request mapping and returns
an observation with attributes accepted, reason, remaining_actions, terminal,
terminal_reason. Controller.trace is an ordered sequence.
"""
from src.board import Board
from src.knowledge_base import KnowledgeBase
from src.controller import Controller
from .conftest import SOLVED

def make_controller(puzzle, budget=5):
    return Controller(Board(puzzle), KnowledgeBase(), max_actions=budget)

def test_invalid_tool_consumes_budget_without_mutation(puzzle):
    c = make_controller(puzzle)
    before = c.board.inspect_board()
    result = c.step({'tool':'not_a_tool'})
    assert not result.accepted and result.reason == 'REJECTED_REQUEST'
    assert result.remaining_actions == 4
    assert c.board.inspect_board() == before
    assert len(c.trace) == 1

def test_accepted_placement_is_dispatched_once(puzzle):
    c = make_controller(puzzle)
    result = c.step({'tool':'place','row':0,'column':2,'digit':4})
    assert result.accepted and c.board.revision == 1
    assert c.used_actions == 1

def test_incomplete_submission_is_terminal(puzzle):
    c = make_controller(puzzle)
    result = c.step({'tool':'submit'})
    assert result.terminal and result.terminal_reason == 'INVALID_SUBMISSION'

def test_successful_submission_on_final_action_wins():
    c = Controller(Board(SOLVED), KnowledgeBase(), max_actions=1)
    result = c.step({'tool':'submit'})
    assert result.terminal and result.terminal_reason == 'SOLVED'

def test_rejected_final_action_ends_at_limit(puzzle):
    c = make_controller(puzzle, budget=1)
    result = c.step({'tool':'bad'})
    assert result.terminal and result.terminal_reason == 'ACTION_LIMIT'

def test_requests_after_terminal_are_inert(puzzle):
    c = make_controller(puzzle, budget=1)
    c.step({'tool':'inspect','scope':'board'})
    before = (c.used_actions, len(c.trace), c.board.revision)
    c.step({'tool':'place','row':0,'column':2,'digit':4})
    assert (c.used_actions, len(c.trace), c.board.revision) == before

def test_trace_is_ordered_and_numbered(puzzle):
    c = make_controller(puzzle)
    c.step({'tool':'inspect','scope':'board'})
    c.step({'tool':'query','atom':'A'})
    assert [entry.action_number for entry in c.trace] == [1,2]
    assert c.used_actions == 2
