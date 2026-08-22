import email_validator


def validate_email(
    email, *, check_deliverability: bool = False
) -> email_validator.ValidatedEmail:
    """
    Validate an email address using email_validator.

    Deliverability checking is disabled by default, but can be
    re-enabled as needed setting the ``check_deliverability``
    argument.
    """
    return email_validator.validate_email(
        email, check_deliverability=check_deliverability
    )


def normalize_email(email: str) -> str:
    """Validate and normalize an email address"""
    return validate_email(email).normalized
