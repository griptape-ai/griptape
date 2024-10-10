from __future__ import annotations

import logging
from typing import Optional, cast

from attrs import define, field
from statemachine import State
from statemachine import StateMachine as _StateMachine
from statemachine.factory import StateMachineMetaclass

from griptape.common import observable
from griptape.configs import Defaults
from griptape.structures import Structure
from griptape.tasks import BaseTask

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class StateMachine(Structure):
    state_machine: _StateMachine = field(init=False)
    events: dict[str, list[StateMachine.Transition]] = field(kw_only=True)

    @property
    def input_task(self) -> Optional[BaseTask]:
        return self.find_task(self.state_machine.current_state.value)

    @property
    def output_task(self) -> Optional[BaseTask]:
        return self.find_task(self.state_machine.current_state.value)

    @define(eq=False)
    class StateMachineListener:
        state_machine: StateMachine = field()

        def on_enter_state(self, state: State) -> None:
            task = self.state_machine.find_task(state.value)
            logger.debug({"state_id": state.value, "task_id": task.id, "event": "on_enter_state"})

            task.execute()

    @define(kw_only=True)
    class Transition:
        source: str = field()
        destination: str = field()

    @define
    class InnerStateMachine(_StateMachine):
        def __attrs_pre_init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)

        @classmethod
        def from_definition(cls, definition: dict, **extra_kwargs) -> StateMachine.InnerStateMachine:
            """Creates a StateMachine class from a dictionary definition, using the StateMachineMetaclass metaclass.

            It maps the definition to the StateMachineMetaclass parameters and then creates the class.

            Example usage with a traffic light machine:

            >>> machine = BaseMachine.from_definition(
            ...     "TrafficLightMachine",
            ...     {
            ...         "states": {
            ...             "green": {"initial": True},
            ...             "yellow": {},
            ...             "red": {},
            ...         },
            ...         "events": {
            ...             "transitions": [
            ...                 {"from": "green", "to": "yellow"},
            ...                 {"from": "yellow", "to": "red"},
            ...                 {"from": "red", "to": "green"},
            ...             ]
            ...         },
            ...     }
            ... )

            Args:
                definition (dict): The definition of the state machine.
                **extra_kwargs: Extra keyword arguments to pass to the metaclass.

            Returns:
                StateMachine.InnerStateMachine: The created state machine class.

            """
            states_instances = {
                state_id: State(**state_kwargs, value=state_id)
                for state_id, state_kwargs in definition["states"].items()
            }

            events = {}
            for event_name, transitions in definition["events"].items():
                for transition_data in transitions:
                    source = states_instances[transition_data["from"]]
                    target = states_instances[transition_data["to"]]

                    transition = source.to(
                        target,
                        event=event_name,
                        cond=transition_data.get("cond"),
                        unless=transition_data.get("unless"),
                        on=transition_data.get("on"),
                        internal=transition_data.get("internal"),
                    )

                    if event_name in events:
                        events[event_name] |= transition
                    else:
                        events[event_name] = transition

            attrs_mapper = {**extra_kwargs, **states_instances, **events}

            return cast(
                StateMachine.InnerStateMachine,
                StateMachineMetaclass(cls.__name__, (cls,), attrs_mapper)(**extra_kwargs),
            )

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        definition = {
            "states": {},
            "events": self.events,
        }
        for task in self.tasks:
            definition["states"][task.id] = task.meta

        for transitions in self.events.values():
            for transition in transitions:
                from_task = self.find_task(transition.source)
                to_task = self.find_task(transition.destination)

                from_task.add_child(to_task)

        self.state_machine = StateMachine.InnerStateMachine.from_definition(definition)
        self.state_machine.add_listener(StateMachine.StateMachineListener(self))

    def add_task(self, task: BaseTask) -> BaseTask:
        task.preprocess(self)
        self._tasks.append(task)

        return task

    @observable
    def try_run(self, *args) -> StateMachine:
        self.state_machine.send(*args)

        return self
