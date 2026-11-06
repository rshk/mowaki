from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import UTC, datetime

from app import repo
from app.const import AUTH_FLOW_HARD_VALIDITY
from app.core.authn.exceptions import (
    FlowAccessDenied,
    FlowAlreadyCompleted,
    FlowExpired,
)
from app.core.context import get_current_session
from app.lib.flows.processor import FlowProcessor
from app.lib.flows.registry import FlowRegistry
from app.lib.flows.repo import FlowRepo
from app.lib.sql.table_helper import UpdateHelper
from app.types.auth.auth_flow import AuthFlow, FlowID, FlowKind, FlowState


@dataclass
class LockedFlow:
    info: AuthFlow
    processor: FlowProcessor


class AuthnFlowRepo(FlowRepo[FlowID]):
    def __init__(self, registry: FlowRegistry):
        self._registry = registry

    async def create(self, kind: FlowKind) -> FlowID:
        session = get_current_session()
        factory = self._registry[kind]
        proc: FlowProcessor = await factory.create()
        state = proc.dump()

        flow_id = await repo.auth.flow.create(
            kind=kind,
            state=FlowState(state),
            expires_in=None,  # TODO: allow setting this on creation
            session_id=session.session_id,
        )

        return flow_id

    async def get(self, flow_id: FlowID) -> AuthFlow:
        flow = await repo.auth.flow.get(flow_id)
        _ensure_flow_is_processable(flow)
        return flow

    @asynccontextmanager
    async def _get_for_update(
        self, flow_id: FlowID
    ) -> AsyncGenerator[UpdateHelper[AuthFlow]]:
        session_id = get_current_session().session_id
        async with repo.auth.flow.for_update(flow_id, session_id=session_id) as upd:
            flow = await upd.get()
            _ensure_flow_is_processable(flow)
            yield upd

    @asynccontextmanager
    async def for_processing(self, flow_id: FlowID) -> AsyncGenerator[FlowProcessor]:
        async with self._get_for_update(flow_id) as upd:
            flow = await upd.get()
            factory = self._registry[flow.kind]
            proc: FlowProcessor = await factory.load(flow.state)

            yield proc

            # Save current state
            state = proc.dump()
            is_ended = proc.get_status().is_ended()
            await upd.update(state=state, is_ended=is_ended)

        # Automatically cleanup ended flows
        if is_ended:
            await repo.auth.flow.delete(flow_id)

    @asynccontextmanager
    async def lock(self, flow_id: FlowID) -> AsyncGenerator[LockedFlow]:
        """Lock a flow for processing

        EXPERIMENTAL method, might replace .for_processing()
        ...or, do we even need a strict protocol for this flow repo?
        (we might, if we want to use a custom one for testing)
        """

        async with self._get_for_update(flow_id) as upd:
            flow = await upd.get()
            factory = self._registry[flow.kind]
            proc: FlowProcessor = await factory.load(flow.state)

            yield LockedFlow(info=flow, processor=proc)

            # Save current state
            state = proc.dump()
            is_ended = proc.get_status().is_ended()
            await upd.update(state=state, is_ended=is_ended)

        # Automatically cleanup ended flows
        if is_ended:
            await repo.auth.flow.delete(flow_id)

    async def delete(self, flow_id: FlowID):
        async with self._get_for_update(flow_id) as upd:
            await upd.update(is_ended=True)  # Logical deletion
        await repo.auth.flow.delete(flow_id)

    async def cleanup(self):
        await self.cleanup_completed()
        await self.cleanup_expired()

    async def cleanup_completed(self):
        await repo.auth.flow.delete_completed()

    async def cleanup_expired(self):
        await repo.auth.flow.delete_expired(max_validity=AUTH_FLOW_HARD_VALIDITY)


def _ensure_flow_is_processable(flow: AuthFlow):

    # If the flow is tied to a session, make sure it matches the
    # current session.
    # DOES THIS AUTHZ CHECK BELONG HERE?
    if flow.session_id is not None:
        session = get_current_session()
        if flow.session_id != session.session_id:
            raise FlowAccessDenied("This flow belongs to a different session")

    # If the flow is completed, reject the request.
    # This has a slim chance of happening due to a race condition
    # between flow completion and deletion from the database.
    # NOTE: the repo should already filter out on is_ended=False, so
    # this is actually unnecessary. Just cover this case with tests and remove?
    if flow.is_ended:
        raise FlowAlreadyCompleted("This flow has already been completed")

    # If the flow has expired, it cannot be processed further.
    # We might want to give the user a convenient option to restart it!
    if is_flow_expired(flow):
        raise FlowExpired("This flow has expired")


def is_flow_expired(flow: AuthFlow) -> bool:
    return get_flow_expiration_date(flow) <= datetime.now(UTC)


def get_flow_expiration_date(flow: AuthFlow) -> datetime:
    expiration_date = flow.created_at + AUTH_FLOW_HARD_VALIDITY
    if flow.expires_at and flow.expires_at < expiration_date:
        expiration_date = flow.expires_at
    return expiration_date
