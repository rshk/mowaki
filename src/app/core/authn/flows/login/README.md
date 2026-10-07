# Login flow

Configurable, unified login flow.


## Supported authentication methods

- Email OTP: used for account creation, and for logging in when a webauthn passkey is not available
- Webauthn: preferred authentication method, when available
- OAuth or SSO: login using a 3rd party provider (Note: this could be a separate flow entirely)
- Time-based OTP: can be used for additional security when a passkey is not available
- Recovery codes: last resort if no passkey or TOTP is available
- Password (?): password authentication can be easily supported with this flow
- Captcha: A captcha (like reCAPTCHA or the Cloudflare one) can be used to decide whether to prompt for extra authentication methods

Also part of the flow:

- Account creation: if user validates Email OTP for an address not
  currently associated to an account, they can be prompted to create
  an account
- Webauthn enrollment: if a new account was created, we can prompt the
  user to generate a passkey to secure their account (should we do
  this for existing accounts with no MFA as well?)
- TOTP enrollment: for new accounts, offer "Authenticator app" as 2fa
- Recovery codes generation: if a new account was created and MFA was
  added, we can let the user download recovery codes at this point.


## Flow state

- We need to store things like OTP, webauthn params, etc.

### Decision required

Do we need to explicitly store some "current step" value, or can we
just infer it based on which flow attributes are set?

- Actions could be valid at various points; they depend on specific
  state attributes being set
- Are there scenarios where we **do not** want the user to be able to
  perform a given action, even if the correct state is set?

(Probably need to draw the full flow first, to make an informed
decision on this).


## Flow actions

- Use the `action` key as discriminator
- Various "steps" have different actions that are allowed


## Flow summary

- Step: `initial`
  - Action: `set-email(email)`
    - Generate OTP and send it to the selected address
    - Next step: `validate-otp`
  - Action: `init-webauthn`
    - Needs to indicate which passkey we want to use for authentication
    - **TODO** Check the webauthn flow for exact next steps required
- Step: `validate-otp`
  - Action: `otp-response(otp)`
    - Validate provided OTP -> if invalid, return error (invalidate flow after X attempts)
    - If user exists for the provided `email`
      - **Create a new session**
      - Add session assertion
      - If MFA is enabled -> 2fa step using one of:
        - Webauthn (passkey)
        - TOTP
        - Recovery code
        - Initiate account recovery procedure
    - If user does not exist
      - Next step: `confirm-create-user`
- Step: `second-factor`
- Step: `confirm-create-user`
  - Action: `confirm`
    - Create a new user
    - **Create a new session**
    - Add session assertion
    - Next step: `enroll-2fa-prompt`
  - Action: `cancel`
    - Abort the whole flow
- Step: `enroll-2fa-prompt`
  - Ask user to enroll a 2fa method; depending on response go to one of the `enroll-...` methods
  - If a 2fa method was enrolled, generate recovery codes and allow the user to download them
  - **RECOVERY CODE STORAGE** how to? Just store an array of hashes? Length/charset of the codes?
    - Cloudflare: 9 dec digits
    - Pypy: 16 hex digits
- Step: `enroll-webauthn`
- Step: `enroll-totp`
- Step: `generate-recovery-codes`
- Step: `validate-totp`
  - Request and verify a time-based OTP form an authenticator app
- Step: `captcha` ??? -> we could require this for user creation


### Simplified flow v1: email OTP only

- INITIAL: ask for email address
  - Action: set-email
    - Send OTP
    - Next step: VALIDATE-OTP
- VALIDATE-OTP:
  - Action: set-otp
    - If OTP is invalid -> abort flow
    - If user exists -> new session with assertion
    - If user doesn't exist -> ask whether to create one


## Step: `INITIAL`

Challenge:

``` json
{
    "kind": "login_init",
    "email_address": {"enabled": true},
    "webauthn": {"enabled": true},  // ...
    // oauth and sso options here
}
```

- email address
- webauthn (if enabled)
- [not implemented yet] various oauth providers (if enabled)
- [not implemented yet] SSO (if enabled)

Actions:

- `{"action": "set_email_address", "email": "..."}`
  - [not implemented yet] if SSO enabled -> initiate SSO flow
  - General case:
    - Send OTP
    - Next step: `VERIFY_OTP`
- `{"action": "webauthn_init"}`
  - Next step: WEBAUTHN_REQUEST


## Step: `EMAIL_PROVIDED`


## Step: `VERIFY_OTP`

State:

`{"email": "...", "otp": "..."}`

Challenge:

`{"kind": "verify_otp"}`


## Step: `WEBAUTHN_REQUEST`
