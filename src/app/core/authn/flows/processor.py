"""
Experimental "flow processor" v2 (instance-based)
"""

import abc
from abc import abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Protocol, cast

from pydantic import BaseModel

from app.types.auth.auth_flow import FlowAction, FlowChallenge, FlowState
from app.types.base import JSONObject


@dataclass(slots=True)
class FlowActionResult[S]:
    result: bool | None
    state: S | None

    @classmethod
    def success(cls):
        return cls(result=True, state=None)

    @classmethod
    def failure(cls):
        return cls(result=False, state=None)

    @classmethod
    def new_state(cls, state: S):
        return cls(result=None, state=state)

    def is_completed(self):
        return self.result is not None

    def is_success(self):
        return self.result is True

    def is_failure(self):
        return self.result is False

    def map[T](self, conv: Callable[[S], T]) -> FlowActionResult[T]:
        if self.state is None:
            return FlowActionResult(result=self.result, state=None)
        return FlowActionResult(result=self.result, state=conv(self.state))


class FlowProcessorProtocol(Protocol):
    @abstractmethod
    async def create(self, params: JSONObject | None = None) -> FlowState:
        """Initialize new flow state"""

    @abstractmethod
    async def process[S: FlowState](
        self, state: S, action: FlowAction
    ) -> FlowActionResult[S]:
        """Process action, returning eitgher"""

    @abstractmethod
    def get_challenge(self, state: FlowState) -> FlowChallenge:
        """Get user-facing challenge for this state"""


class ModelBasedFlowProcessor[S: BaseModel, A: BaseModel, C: BaseModel](
    FlowProcessorProtocol, abc.ABC
):
    __slots__ = []

    state_model: type[S]
    action_model: type[A]
    challenge_model: type[C]

    # FlowProcessor iterface -----------------------------------------

    async def create(self, params: JSONObject | None = None) -> FlowState:
        if params is None:
            params = {}
        _data = (await self.create_state(params)).model_dump()
        return FlowState(_data)

    async def process[StateJson: FlowState](
        self, state: StateJson, action: FlowAction
    ) -> FlowActionResult[StateJson]:
        """Process action, returning eitgher"""
        _state = self.state_model.model_validate(state)
        _action = self.action_model.model_validate(action)
        result = await self.process_action(_state, _action)
        return result.map(lambda s: cast(StateJson, s.model_dump()))

    def get_challenge(self, state: FlowState) -> FlowChallenge:
        """Get user-facing challenge for this state"""
        _state = self.state_model.model_validate(state)
        _data = self.get_challenge_from_state(_state).model_dump()
        return FlowChallenge(_data)

    # Interface methods ----------------------------------------------

    async def create_state(self, params: JSONObject) -> S:
        return self.state_model.model_validate(params)

    @abstractmethod
    async def process_action(self, state: S, action: A) -> FlowActionResult[S]:
        pass

    @abstractmethod
    def get_challenge_from_state(self, state: S) -> C:
        pass


type StateCreator[S] = Callable[[JSONObject], Awaitable[S]]
type ActionProcessor[S, A] = Callable[[S, A], Awaitable[FlowActionResult[S]]]
type ChallengeGetter[S, C] = Callable[[S], C]


class FlowProcessor[S: BaseModel, A: BaseModel, C: BaseModel](
    ModelBasedFlowProcessor[S, A, C]
):
    __slots__ = ()

    _state_creator: StateCreator[S] | None
    _action_processor: ActionProcessor[S, A] | None
    _challenge_getter: ChallengeGetter[S, C] | None

    def __init__(
        self,
        *,
        state_model: type[S] | None = None,
        action_model: type[A] | None = None,
        challenge_model: type[C] | None = None,
    ):
        if state_model is not None:
            self.state_model = state_model
        if action_model is not None:
            self.action_model = action_model
        if challenge_model is not None:
            self.challenge_model = challenge_model

        self._state_creator = None
        self._action_processor = None
        self._challenge_getter = None

    # Implementation of ModelBasedFlowprocessor ----------------------

    async def create_state(self, params: JSONObject) -> S:
        if self._state_creator is not None:
            return await self._state_creator(params)
        return self.state_model.model_validate(params)

    async def process_action(self, state: S, action: A) -> FlowActionResult[S]:
        if self._action_processor is not None:
            return await self._action_processor(state, action)
        raise ValueError("Missing action processor")

    def get_challenge_from_state(self, state: S) -> C:
        if self._challenge_getter is not None:
            return self._challenge_getter(state)
        raise ValueError("Missing challenge getter")

    # Decorators -----------------------------------------------------

    def state_creator(self, fn: StateCreator[S]) -> StateCreator[S]:
        self._state_creator = fn
        return fn

    def action_processor(self, fn: ActionProcessor[S, A]) -> ActionProcessor[S, A]:
        self._action_processor = fn
        return fn

    def challenge_getter(self, fn: ChallengeGetter[S, C]) -> ChallengeGetter[S, C]:
        self._challenge_getter = fn
        return fn
