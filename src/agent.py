
"""Bounded ReAct agent runner.

Implements specs/react_loop_contract.md.
The policy selects requests; the controller executes them.
"""


def run_agent(policy, controller):
    """Run the policy until the controller reaches a terminal state.

    The policy receives only the previous observation, trace,
    and remaining action budget.
    """
    observation = None

    while controller.terminal_reason is None:
        remaining = controller.max_actions - controller.used_actions

        if remaining <= 0:
            # Defensive fallback if the budget was exhausted
            # without the terminal reason being assigned.
            controller.terminal_reason = "ACTION_LIMIT"
            break

        request = policy.next_request(
            observation=observation,
            trace=tuple(controller.trace),
            remaining_actions=remaining,
        )

        observation = controller.step(request)

    return controller.terminal_reason
