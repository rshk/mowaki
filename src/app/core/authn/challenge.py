from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from app.const import CHALLENGE_HARD_VALIDITY
from app.core.authn.exceptions import (
    ChallengeExpired,
    ChallengeResponseMismatched,
)
from app.core.context import get_current_session
from app.exceptions import ItsABug
from app.repo.auth import challenge as _repo
from app.types.auth.challenges import (
    ChallengeID,
    ChallengeResponse,
    ChallengeState,
    ChallengeStateParams,
    EmailOTPChallengeResponse,
    EmailOTPChallengeStateParams,
)


async def create_challenge(params: ChallengeStateParams) -> ChallengeID:
    return await _repo.create_challenge(params)


@asynccontextmanager
async def lock_challenge_for_processing(
    challenge_id: ChallengeID,
) -> AsyncGenerator[ChallengeState]:
    """Lock a challenge for processing, delete it at the end"""

    async with _repo.lock_challenge_for_processing(challenge_id) as challenge:
        if is_challenge_expired(challenge):
            raise ChallengeExpired(f"Challenge {challenge_id} expired")
        yield challenge


def is_challenge_expired(challenge: ChallengeState):
    """Check whether a challenge expired"""

    now = datetime.now(UTC)

    if (challenge.expires_at is not None) and challenge.expires_at <= now:
        return True

    age = challenge.created_at - now
    return age > CHALLENGE_HARD_VALIDITY


async def process_challenge_response(response: ChallengeResponse):
    """
    Process response to a challenge.

    - The original challenge will be deleted afterwards
    - Checks that the challenge hasn't expired
    - On success, appropriate assertions will be added to the session
    - On failure, an exception is raised

    Raises:
        - ChallengeExpired
        - ChallengeResponseInvalid
        - ChallengeResponseMismatched
    """

    session = get_current_session()

    async with lock_challenge_for_processing(response.challenge_id) as challenge:
        if response.kind != challenge.params.kind:
            # User might have tampered with the request.
            # Should we log this as a security warning?
            # (Or just info, as the risk of exploitability is very low)
            raise ChallengeResponseMismatched(
                f"Wrong response type for challenge {response.challenge_id}: "
                f"expected {challenge.params.kind}, received {response.kind}."
            )

        return

        match challenge.params.kind:
            case "email-otp":
                # TODO: rearrange code so we don't have circular imports

                assert isinstance(response, EmailOTPChallengeResponse)
                assert isinstance(challenge.params, EmailOTPChallengeStateParams)

                # await process_email_otp_challenge_response(challenge.params, response)

            case "passkey-auth":
                raise NotImplementedError
            case "passkey-enroll":
                raise NotImplementedError
            case _:
                # This is a bug, as we should cover all valid types here!
                raise ItsABug(f"Unsupported challenge type: {challenge.params.kind}")
