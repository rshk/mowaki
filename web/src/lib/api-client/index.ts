import { API_URL } from "../config";
import { RestClient } from "./rest-client";
import * as tokenStorage from "../token-storage";

export class ApiClient {
    _client: RestClient;

    constructor(baseUrl: string) {
        this._client = new RestClient(baseUrl);

        this._client.addRequestMiddleware(request => {
            const token = tokenStorage.getToken();
            if (token) {
                request.headers.set("Authorization", `Bearer ${token}`);
            }
        });

        this._client.addResponseHandler(response => {
            const newSessionId = response.headers.get("x-set-session-token");
            if (newSessionId) {
                tokenStorage.setSessionToken(newSessionId);
            }
        });
    }

    // ---------------------------------------------------------------
    // User authentication
    // ---------------------------------------------------------------

    async getLoginFlowInfo(token?: string): Promise<null> {}

    async startLoginFlow(email: string): Promise<null> {}

    async submitLoginFlowChallengeResponse(
        token: string,
        response: object,
    ): Promise<null> {}

    async getSessionInfo(token: string) {}

    async deleteSession(token: string) {}

    // ---------------------------------------------------------------
    // Item management
    // ---------------------------------------------------------------

    async getItems(): Promise<Item[]> {
        return (await this._client.get("/items")) as Item[];
    }

    async getItem(id: string): Promise<Item> {
        return (await this._client.get(`/item/${id}`)) as Item;
    }

    async createItem(label: string): Promise<Item> {
        return (await this._client.post("/items", { label })) as Item;
    }

    async updateItem(id: string, label: string): Promise<null> {
        return (await this._client.patch(`/item/${id}`, { label })) as null;
    }

    async deleteItem(id: string): Promise<null> {
        return (await this._client.delete(`/item/${id}`)) as null;
    }
}

type LoginFlowInfo = {
    flowId: string | null;
    challenges?: LoginFlowChallenge[];
    sessionId?: string;
};

type LoginFlowChallenge =
    | { type: "email"; email: string }
    | { type: "password"; password: string };

type Item = {
    id: string;
    label: string;
};

export default new ApiClient(API_URL);
