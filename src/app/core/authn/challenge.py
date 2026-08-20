from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app import repo
from app.types.auth.challenges import ChallengeID, ChallengeState, ChallengeStateParams


async def create_challenge(params: ChallengeStateParams) -> ChallengeID:
    return await repo.auth.challenge.create_challenge(params)


@asynccontextmanager
async def lock_challenge_for_processing(
    challenge_id: ChallengeID,
) -> AsyncGenerator[ChallengeState]:
    """Lock a challenge for processing, delete it at the end"""

    async with repo.auth.challenge.lock_challenge_for_processing(
        challenge_id
    ) as challenge:
        yield challenge
