import pytest

from app.lib.flows.base import FailureStateBlock, SuccessStateBlock
from app.lib.flows.types import FlowAction, FlowState

from .data.simple_flow import InitialState, SecondState, SimpleFlowFactory


@pytest.mark.asyncio
async def test_flow_execution():
    initial_state = InitialState()
    assert initial_state.dump() == {"kind": "initial"}

    state2 = await initial_state.execute(FlowAction({"kind": "goto-2"}))
    assert isinstance(state2, SecondState)
    assert state2.dump() == {"kind": "state-2"}

    endstate_success = await state2.execute(FlowAction({"kind": "ok"}))
    assert isinstance(endstate_success, SuccessStateBlock)
    assert endstate_success.dump() == {"kind": "success"}

    endstate_failure = await state2.execute(FlowAction({"kind": "error"}))
    assert isinstance(endstate_failure, FailureStateBlock)
    assert endstate_failure.dump() == {"kind": "failure"}


@pytest.mark.asyncio
async def test_creation_of_flow_through_factory():
    factory = SimpleFlowFactory()

    initial_state = await factory.create()
    assert isinstance(initial_state, InitialState)
    assert initial_state.dump() == {"kind": "initial"}


@pytest.mark.asyncio
async def test_loading_of_flow_states_through_factory():
    factory = SimpleFlowFactory()

    initial_state = await factory.load(FlowState({"kind": "initial"}))
    assert isinstance(initial_state, InitialState)

    state2 = await factory.load(FlowState({"kind": "state-2"}))
    assert isinstance(state2, SecondState)

    endstate_success = await factory.load(FlowState({"kind": "success"}))
    assert isinstance(endstate_success, SuccessStateBlock)

    endstate_failure = await factory.load(FlowState({"kind": "failure"}))
    assert isinstance(endstate_failure, FailureStateBlock)
