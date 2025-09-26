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
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method,
            headers: {
                "Content-Type": "application/json",
                ...this.headers,
            },
            body: body ? JSON.stringify(body) : undefined,
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        return (await response.json()) as T;
    }


    connectWebSocket(path: string): WebSocket {
        const url = this.baseUrl.replace(/^http/, "ws") + path;
        const ws = new WebSocket(url);

        ws.onopen = () => {console.log("WebSocket connected:", url);};
        ws.onclose = () => {console.log("WebSocket disconnected:", url);};
        ws.onerror = (err) => {console.error("WebSocket error:", err);};

        return ws;
    }
}