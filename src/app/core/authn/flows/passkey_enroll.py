from typing import Any

from pydantic import BaseModel
from webauthn import generate_registration_options, verify_registration_response
from webauthn.helpers import options_to_json_dict
from webauthn.registration.verify_registration_response import VerifiedRegistration

from app import repo
from app.config import get_config
from app.core.authn.exceptions import FlowProcessingError
from app.core.authz.trust_level import check_trust_level
from app.core.context import get_auth_subject
from app.types.auth.auth_user_passkey import PasskeyCredentialID, PasskeyPublicKeyData
from app.types.auth.trust_level import TRUST_LEVEL_HIGH

from .processor import FlowActionResult, FlowProcessor, JSONObject


class PasskeyEnrollFlowState(BaseModel):
    options: Any


class PasskeyEnrollFlowAction(BaseModel):
    credential: Any


class PasskeyEnrollFlowChallenge(BaseModel):
    options: Any


# Shortcut aliases
StateModel = PasskeyEnrollFlowState
ActionModel = PasskeyEnrollFlowAction
ChallengeModel = PasskeyEnrollFlowChallenge


PROCESSOR = FlowProcessor(
    state_model=StateModel,
    action_model=ActionModel,
    challenge_model=ChallengeModel,
)


@PROCESSOR.state_creator
async def create_passkey_enroll_initial_state(_: JSONObject) -> StateModel:
    return await generate_challenge_state()


@PROCESSOR.action_processor
async def process(
    state: StateModel, action: ActionModel
) -> FlowActionResult[StateModel]:

    result = await verify_challenge_response(state, action)

    # Didn't raise -> valid -> store new passkey
    # TODO: do we need to validate transports?
    await register_new_passkey(result, action.credential["response"]["transports"])

    return FlowActionResult.success()


@PROCESSOR.challenge_getter
def get_email_otp_auth_challenge(state: StateModel) -> ChallengeModel:
    return ChallengeModel(options=state.options)


async def generate_challenge_state() -> PasskeyEnrollFlowState:
    config = get_config()
    subject = get_auth_subject()

    if subject.user_id is None:
        # TODO: we should just prompt the user to authenticate instead
        # Should we include that in the flow, or just create a new one?
        raise FlowProcessingError("Only authenticated users can enroll a new passkey")

    if not check_trust_level(subject, TRUST_LEVEL_HIGH, recent=True):
        # TODO: we should just prompt the user to re-authenticate instead
        # Should we include that in the flow, or just create a new one?
        raise FlowProcessingError("Only authenticated users can enroll a new passkey")

    # FIXME: use a core function to get user here?
    user = await repo.user.get(subject.user_id)

    options = generate_registration_options(
        rp_id=config.auth_relying_party_id,
        rp_name=config.auth_relying_party_name,
        user_name=user.email,
        user_id=subject.user_id.bytes,
        # attestation=AttestationConveyancePreference.DIRECT,  # ???
        # authenticator_selection=AuthenticatorSelectionCriteria(  # ???
        #     authenticator_attachment=AuthenticatorAttachment.PLATFORM,
        #     resident_key=ResidentKeyRequirement.REQUIRED,
        # ),
        # exclude_credentials=[...]  # TODO
    )

    return PasskeyEnrollFlowState(options=options_to_json_dict(options))


async def verify_challenge_response(
    state: PasskeyEnrollFlowState, action: PasskeyEnrollFlowAction
) -> VerifiedRegistration:
    config = get_config()
    verification = verify_registration_response(
        credential=action.credential,
        expected_challenge=state.options["challenge"],
        expected_origin=str(config.frontend_url),  # TODO: use a specific settinng?
        expected_rp_id=config.auth_relying_party_id,
        require_user_verification=True,
    )
    return verification


async def register_new_passkey(
    v: VerifiedRegistration, transports: list[str] | None = None
):
    subject = get_auth_subject()

    if subject.user_id is None:
        # This should never happen
        raise FlowProcessingError("Only authenticated users can enroll a new passkey")

    user = await repo.user.get(subject.user_id)

    await repo.auth.user_passkey.create(
        user_id=user.id,
        credential_id=PasskeyCredentialID(v.credential_id),
        public_key=PasskeyPublicKeyData(v.credential_public_key),
        display_name=None,
        device_type=v.credential_device_type,
        backed_up=v.credential_backed_up,
        transports=transports,
    )
