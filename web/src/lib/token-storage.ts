import { SESSION_ID_KEY } from "./config";

export function getToken(): string | null {
    return (
        sessionStorage.getItem(SESSION_ID_KEY) ||
        localStorage.getItem(SESSION_ID_KEY) ||
        null
    );
}

export function setSessionToken(token: string): void {
    localStorage.removeItem(SESSION_ID_KEY);
    sessionStorage.setItem(SESSION_ID_KEY, token);
}

export function setToken(token: string): void {
    sessionStorage.removeItem(SESSION_ID_KEY);
    localStorage.setItem(SESSION_ID_KEY, token);
}

export function removeToken(): void {
    sessionStorage.removeItem(SESSION_ID_KEY);
    localStorage.removeItem(SESSION_ID_KEY);
}
