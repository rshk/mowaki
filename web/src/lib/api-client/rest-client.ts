const MIME_JSON = "application/json";

export class RestClient {
    baseUrl: string;
    headers: Headers;
    getExtraHeaders: null | (() => Headers);

    constructor(baseUrl: string) {
        this.baseUrl = baseUrl;
        this.headers = new Headers();
    }

    _url(path: string): URL {
        return new URL(path, this.baseUrl);
    }

    _headers(headers?: { [key: string]: string }): Headers {
        let newHeaders = new Headers(this.headers);

        if (this.getExtraHeaders !== null) {
            this.getExtraHeaders().forEach(([key, val]) => {
                newHeaders.set(key, val);
            });
        }

        if (typeof headers !== "undefined") {
            Object.entries(headers).forEach(([key, val]) => {
                newHeaders.set(key, val);
            });
        }

        return newHeaders;
    }

    setExtraHeadersGetter(fn: () => Headers) {
        this.getExtraHeaders = fn;
    }

    async get(path: string): Promise<object> {
        let url = this._url(path);
        let options = {
            method: "GET",
            headers: this._headers({ Accept: MIME_JSON }),
        };
        return await fetch(url, options).then((x) => x.json());
    }

    async post(path: string, data: object): Promise<object> {
        let url = this._url(path);
        let body = JSON.stringify(data);
        let options = {
            method: "POST",
            headers: this._headers({
                Accept: MIME_JSON,
                "Content-Type": MIME_JSON,
            }),
            body,
        };
        return await fetch(url, options).then((x) => x.json());
    }

    async put(path: string, data: object): Promise<object> {
        let url = this._url(path);
        let body = JSON.stringify(data);
        let options = {
            method: "PUT",
            headers: this._headers({
                Accept: MIME_JSON,
                "Content-Type": MIME_JSON,
            }),
            body,
        };
        return await fetch(url, options).then((x) => x.json());
    }

    async patch(path: string, data: object): Promise<object> {
        let url = this._url(path);
        let body = JSON.stringify(data);
        let options = {
            method: "PATCH",
            headers: this._headers({
                Accept: MIME_JSON,
                "Content-Type": MIME_JSON,
            }),
            body,
        };
        return await fetch(url, options).then((x) => x.json());
    }

    async delete(path: string): Promise<object> {
        let url = this._url(path);
        let options = {
            method: "DELETE",
            headers: this._headers({ Accept: MIME_JSON }),
        };
        return await fetch(url, options).then((x) => x.json());
    }
}
