# Login flow challenges

## Email OTP (One Time password)

State:

- email
- otp


## Webauthn (Passkey)

- We need to know which user is trying to authenticate

State:

(the challenge)

Challenge:

init options for webauthn

Response:


## CAPTCHA

## RECAPTCHA

See [RECAPTCHA](https://developers.google.com/recaptcha).

## Cloudflare Turnstile

See [Cloudflare Turnstile](https://developers.cloudflare.com/turnstile/).


## TOTP (Time-based One Time Password)

- We need to know which user is trying to authenticate


## OAuth

Should we use a separate flow for OAuth?


## SSO

Should we use a separate flow for SSO?


## Prompt

Prompt are used to ask the user to confirm or choose an action.

We can probably standardize them to facilitate reuse.

Examples:

- Ask the user whether they want to create a new account, after email
  OTP authentication (or OAuth).
