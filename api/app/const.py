from datetime import timedelta

SESSION_TOKEN_HEADER = "X-Set-Session-Token"

# Allowed headers for CORS
CUSTOM_HEADERS = [
    SESSION_TOKEN_HEADER,
]

# Session expiration time since last use
SESSION_SOFT_VALIDITY = timedelta(days=30)

# Session expiration time since creation
SESSION_HARD_VALIDITY = timedelta(days=90)

# Flow expiration time since creation
FLOW_HARD_VALIDITY = timedelta(hours=12)
