/*********************************************************************

   Authorization token storage facilities.

   - Persistent tokens are stored in localStorage, so they're
     persisted between browser sessions.

   - Session tokens are stored in sessionStorage, so they're deleted
     when the browser tab is closed.

*********************************************************************/

import { SESSION_ID_KEY } from "./config";

type TokenString = string;

/**
   Retrieve token from storage
 */
export function getToken(): TokenString | null {
    return (
        sessionStorage.getItem(SESSION_ID_KEY) ||
        localStorage.getItem(SESSION_ID_KEY) ||
        null
    );
}

type SetTokenOptions = {
    persistent: boolean;
};

export function setToken(
    token: TokenString,
    { persistent = false }: SetTokenOptions,
): void {
    if (persistent) {
        setPersistentToken(token);
    } else {
        setSessionToken(token);
    }
}

export function setSessionToken(token: TokenString): void {
    localStorage.removeItem(SESSION_ID_KEY);
    sessionStorage.setItem(SESSION_ID_KEY, token);
}

export function setPersistentToken(token: TokenString): void {
    sessionStorage.removeItem(SESSION_ID_KEY);
    localStorage.setItem(SESSION_ID_KEY, token);
}

export function updateToken(token: TokenString): void {
    if (localStorage.getItem(SESSION_ID_KEY)) {
        setPersistentToken(token);
    } else {
        setSessionToken(token);
    }
}

export function removeToken(): void {
    sessionStorage.removeItem(SESSION_ID_KEY);
    localStorage.removeItem(SESSION_ID_KEY);
}

/**
   Move token to localStorage
 */
export function makePersistent(): void {
    setPersistentToken(getToken());
}

/**
   Move token to sessionStorage
 */
export function makeTemporary(): void {
    setSessionToken(getToken());
}
