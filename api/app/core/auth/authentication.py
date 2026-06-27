"""
Authentication
--------------

- Request authentication to a "level"
- Initiate a flow with some challenges
- When responding to an authentication challenge, assertions might be
  granted. The flow can also be marked as completed. When assertions
  are granted, the session secret needs to be rotated.
  We can even create a brand new session in some cases, eg. when
  switching authenticated user.

"""

import uuid
from datetime import datetime, timezone
from typing import reveal_type

from app import repo
from app.repo.auth.flow import generate_challenge_id
from app.types.auth.challenges import (
    BaseChallengeResponse,
    Challenge,
    ChallengeID,
    EmailAddrChallenge,
    EmailAddrResponse,
    EmailAddrState,
    EmailOtpChallenge,
    EmailOtpResponse,
    EmailOtpState,
    PasskeyChallenge,
    TotpChallenge,
)
from app.types.auth.flow import AuthFlow, AuthFlowID


async def create_login_flow():
    flow_id = await repo.auth.flow.create(
        kind="login",
        challenges=[
            EmailAddrChallenge(
                challenge_id=generate_challenge_id(),
                created_at=datetime.now(timezone.utc),
                state=EmailAddrState(),
            )
        ],
    )
    flow = await repo.auth.flow.get(flow_id)
    return flow


def create_upgrade_flow():
    pass


def advance_flow(flow: AuthFlow, responses: list[BaseChallengeResponse]) -> AuthFlow:
    responses_by_id = {x.challenge_id: x for x in responses}
    for challenge in flow.challenges:
        response = responses_by_id.get(challenge.challenge_id)
        if response is None:
            continue  # nothing to do

        # Evaluate response to the challenge
        # Perform required side effects
        # Run queries to retrieve user state + use to generate next challenges

        if isinstance(challenge, EmailAddrChallenge):
            assert isinstance(response, EmailAddrResponse), (
                f"Mismatched response type for {challenge}: {response}"
            )
            assert challenge.kind == response.kind == "email-addr"
            # TODO: handle response

        elif isinstance(challenge, EmailOtpChallenge):
            assert isinstance(response, EmailOtpResponse), (
                f"Mismatched response type for {challenge}: {response}"
            )
            assert challenge.kind == response.kind == "email-otp"
            # TODO: handle response

        elif isinstance(challenge, PasskeyChallenge):
            pass
            # TODO: handle response

        elif isinstance(challenge, TotpChallenge):
            pass
            # TODO: handle response

        else:
            raise TypeError(f"Unsupported challenge: {challenge}")

    return flow


# Private functions --------------------------------------------------
