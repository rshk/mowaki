from datetime import timedelta

# Name of the HTTP header used to pass session tokens
SESSION_TOKEN_HEADER = "X-Set-Session-Token"

# Allowed headers for CORS
CUSTOM_HEADERS = [
    SESSION_TOKEN_HEADER,
]

# Session expiration time since last use
SESSION_SOFT_VALIDITY = timedelta(days=30)

# Session expiration time since creation
SESSION_HARD_VALIDITY = timedelta(days=90)

# Default max validity for authentication challenges
CHALLENGE_HARD_VALIDITY = timedelta(minutes=60)

# Maximum age for an authentication assertion to be considered
# "recent" for authorization purposes.
RECENT_ASSERTION_MAX_AGE = timedelta(minutes=5)

# Default mailer configuration
DEFAULT_MAILER = "dummy://"
DEFAULT_EMAIL_SENDER = "Default Sender <no-reply@example.com>"
