from app.exceptions import AppException


class SessionError(AppException):
    pass


class SessionExpired(SessionError):
    """Session was found, but it expired"""


class SessionNotFound(SessionError):
    """Session was not found"""


class SessionInvalid(SessionError):
    """Session was found but it's invalid for some reason"""


# class ChallengeExpired(AppException):
#     """Challenge is past expiration date"""


# class ChallengeResponseInvalid(AppException):
#     """Invalid response to a challenge"""


# class ChallengeResponseMismatched(ChallengeResponseInvalid):
#     """Challenge response doesn't match the challenge type"""


class FlowExpired(AppException):
    pass


class ConflictingAssertion(AppException):
    """A conflicting assertion was found in the session"""
