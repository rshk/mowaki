def normalize_email_address(email: str) -> str:
    """Normalize an email address.

    Will convert it to lower case, to allow for case-insensitive
    matching.
    """
    if not isinstance(email, str):
        raise TypeError('Expected a string')
    return email.lower()
