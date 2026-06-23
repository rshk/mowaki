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

def initiate_authentication_flow():
    pass
