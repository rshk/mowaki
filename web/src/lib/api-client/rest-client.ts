const MIME_JSON = "application/json";


type RequestMiddleware = (request: Request) => void;
type ResponseHandler = (response: Response) => void;

export class RestClient {
    baseUrl: string;
    headers: Headers;
    requestMiddleware: RequestMiddleware[];
    responseHandlers: ResponseHandler[];

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.headers = new Headers();
        this.requestMiddleware = [];
        this.responseHandlers = [];
    }

    _url(path: string): URL {
        return new URL(path, this.baseUrl);
    }

    addRequestMiddleware(fn: RequestMiddleware) {
        this.requestMiddleware.push(fn);
    }

    addResponseHandler(fn: ResponseHandler) {
        this.responseHandlers.push(fn);
    }

    async _fetchJson(
        path: string,
        method: string,
        data?: object,
    ): Promise<object> {
        let url = this._url(path);
        let options: RequestInit = {
            method,
            headers: {
                "Accept": MIME_JSON,
            },
        };

        if (
            method !== "GET" &&
            method !== "HEAD" &&
            method !== "OPTIONS" &&
            typeof data !== "undefined"
        ) {
            options.headers["Content-Type"] = MIME_JSON;
            options.body = JSON.stringify(data);
        }

        let request = new Request(url, options);
        this.requestMiddleware.forEach(fn => fn(request));

        let response = await fetch(request);

        if (response.ok) {
            this.responseHandlers.forEach(handler => handler(response));
            return response.json();
        }

        if (response.status == 403) {
            throw new AuthorizationError(response);
        }

        throw new HttpError(response);
    }

    async get(path: string): Promise<object> {
        return this._fetchJson(path, "GET")
    }

    async post(path: string, data: object): Promise<object> {
        return this._fetchJson(path, "POST", data);
    }

    async put(path: string, data: object): Promise<object> {
        return this._fetchJson(path, "PUT", data);
    }

    async patch(path: string, data: object): Promise<object> {
        return this._fetchJson(path, "PATCH", data);
    }

    async delete_(path: string): Promise<object> {
        return this._fetchJson(path, "DELETE");
    }
}


export class HttpError extends Error {
    response: Response;

    constructor(response: Response) {
        super();
        this.response = response;
    }
}


export class AuthorizationError extends HttpError {}
