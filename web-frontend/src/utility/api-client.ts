type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";


interface ApiClientOptions {
baseUrl: string;
headers?: Record<string, string>;
}


export class ApiClient {
    private baseUrl: string;
    private headers: Record<string, string>;

    constructor(options: ApiClientOptions) {
        this.baseUrl = options.baseUrl;
        this.headers = options.headers || {};
    }

    async request<T>(endpoint: string, method: HttpMethod = "GET", body?: unknown): Promise<T> {

        let requestBody: BodyInit | undefined;
        if(body && body instanceof FormData) {
            requestBody = body;
        }
        else {
            requestBody = JSON.stringify(body);
            this.headers["Content-Type"] = "application/json";
        }
        console.log(body, requestBody)

        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method,
            headers: {
                ...this.headers,
            },
            body: requestBody,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return (await response.json()) as T;
    }


    connectWebSocket(path: string): WebSocket {
        const url = this.baseUrl.replace(/^https/, "wss") + path;
        const ws = new WebSocket(url);

        ws.onopen = () => {console.log("WebSocket connected:", url);};
        ws.onclose = () => {console.log("WebSocket disconnected:", url);};
        ws.onerror = (err) => {console.error("WebSocket error:", err);};

        return ws;
    }
}