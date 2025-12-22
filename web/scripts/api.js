// script/api.js
const BACKEND_PORT = 8000;
const API_BASE =
  window.location.port === "5500"
    ? `http://${window.location.hostname}:${BACKEND_PORT}/api`
    : "/api";

export async function predictNews(payload) {
    try {
        const res = await fetch(`${API_BASE}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!res.ok) {
            throw new Error(`Lỗi server: ${res.status}`);
        }

        return await res.json();
    } catch (error) {
        console.error("Lỗi khi gọi API predict:", error);
        throw error; // Ném lỗi để main.js có thể bắt được và hiển thị lên UI
    }
}

export async function sendFeedback(feedback) {
    try {
        const res = await fetch(`${API_BASE}/feedback`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(feedback)
        });

        if (!res.ok) {
            throw new Error(`Lỗi feedback: ${res.status}`);
        }

        return await res.json();
    } catch (error) {
        console.error("Lỗi khi gửi feedback:", error);
        return { success: false, error: error.message };
    }
}