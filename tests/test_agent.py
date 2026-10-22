"""Black-box ReAct runner cases from specs/react_loop_contract.md.

V2 interface decision: run_agent(policy, controller) returns terminal reason.
"""
from src.board import Board
from src.knowledge_base import KnowledgeBase
from src.controller import Controller
from src.agent import run_agent
from .conftest import SOLVED

class FixedPolicy:
    def __init__(self, request):
        self.request = request
        self.calls = 0
    def next_request(self, observation, trace, remaining_actions):
        self.calls += 1
        return self.request

def test_runner_stops_after_solved_submission():
    c = Controller(Board(SOLVED), KnowledgeBase(), max_actions=3)
    policy = FixedPolicy({'tool':'submit'})
    assert run_agent(policy, c) == 'SOLVED'
    assert policy.calls == 1 and c.used_actions == 1

def test_invalid_policy_output_cannot_run_forever(puzzle):
    c = Controller(Board(puzzle), KnowledgeBase(), max_actions=2)
    policy = FixedPolicy({'tool':'bogus'})
    assert run_agent(policy, c) == 'ACTION_LIMIT'
    assert policy.calls == 2 and c.used_actions == 2
