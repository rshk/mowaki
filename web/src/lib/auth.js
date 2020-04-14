const TOKEN_KEY_NAME = 'api-auth-token';
const LOGIN_PAGE_URL = '/login';
const AFTER_LOGIN_PAGE = '/';
const AFTER_LOGOUT_PAGE = LOGIN_PAGE_URL;


export function doLogin(token, options) {
    const opts = {destination: AFTER_LOGIN_PAGE, ...options};
    localStorage.setItem(TOKEN_KEY_NAME, token);
    window.location.href = opts.destination;
}

export function doLogout(options) {
    const opts = {destination: AFTER_LOGOUT_PAGE, ...options};

    _clearAccessToken();

    // Prevent infinite redirection loop
    if (window.location.pathname !== opts.destination) {
        // Redirect to login page; also, ensures all the js-side state
        // is flushed by refreshing the page (as opposed to using
        // pushState).
        window.location.href = opts.destination;
    }
    else {
        window.location.reload();
    }
}

export function getToken() {
    return localStorage.getItem(TOKEN_KEY_NAME);
}


function _clearAccessToken() {
    localStorage.removeItem(TOKEN_KEY_NAME);
    localStorage.clear();
}
