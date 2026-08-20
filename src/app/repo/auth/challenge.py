import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app.lib.sql.table_helper import TableHelper
from app.repo._schema.auth_challenge import ChallengeTable
from app.resources import get_database
from app.types.auth.challenges import ChallengeID, ChallengeState, ChallengeStateParams

_crud = TableHelper[ChallengeState](
    ChallengeTable,
    model=ChallengeState,
    get_engine=get_database,
)


async def create_challenge(params: ChallengeStateParams) -> ChallengeID:
    challenge_id = ChallengeID(uuid.uuid4())
    created_at = datetime.now(UTC)
    await _crud.insert(
        challenge_id=challenge_id,
        created_at=created_at,
        expires_at=None,
        params=params,
    )
    return challenge_id


@asynccontextmanager
async def lock_challenge_for_processing(
    challenge_id: ChallengeID,
) -> AsyncGenerator[ChallengeState]:
    """Lock a challenge for processing, delete it at the end"""

    async with _crud.for_update(challenge_id) as updh:
        challenge = updh.result.one()
        yield challenge

        # Challenges are one-time only!
        await _crud.delete(challenge_id)
