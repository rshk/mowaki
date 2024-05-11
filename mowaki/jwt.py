from datetime import datetime, timedelta

import jwt


class TokenMaker:

    """Convenience object for issuing and validating JWT tokens.

    Keeps track of (and validates) secret, algorithm, issuer, and
    audience for a particular JWT token type.
    """

    def __init__(
        self,
        secret,
        issuer=None,
        audience=None,
        validity=None,
        algorithm="HS256",
    ):
        self.secret = secret
        self.issuer = issuer
        self.audience = audience
        self.validity = validity
        self.algorithm = algorithm

    def issue(self, subject, validity=None, **kwargs):
        """Issue a new JWT token

        Args:

            subject (str):
                Token subject (eg. user ID)

            validity (datetime.timedelta):
                Token validity.

            exp (datetime.datetime):
                Token expiration date. Overrides validity.
        """

        claim = {
            "sub": subject,
        }

        if self.issuer is not None:
            claim["iss"] = self.issuer

        if self.audience is not None:
            claim["aud"] = self.audience

        if validity is None:
            validity = self.validity

        if validity is not None:
            claim["exp"] = datetime.utcnow() + timedelta(seconds=self.validity)

        claim.update(kwargs)

        return jwt.encode(claim, self.secret, algorithm=self.algorithm)

    def validate(self, token):
        """Validate a JWT token, returning the contained data"""

        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            issuer=self.issuer,
            audience=self.audience,
        )


def get_unverified_header(token):
    return jwt.get_unverified_header(token)


def get_unverified_token_data(token):
    return jwt.decode(token, options={"verify_signature": False})


def get_token_audience(token):
    return get_unverified_token_data(token)["aud"]
