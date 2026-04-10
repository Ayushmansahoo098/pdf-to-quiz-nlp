const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export async function generateQuiz(file, questionsPerType) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("questions_per_type", String(questionsPerType));

  try {
    const response = await fetch(`${API_BASE}/api/generate-quiz`, {
      method: "POST",
      body: formData,
    });

    const contentType = response.headers.get("content-type") || "";
    let payload = {};

    if (contentType.includes("application/json")) {
      try {
        payload = await response.json();
      } catch {
        payload = {};
      }
    } else {
      const rawText = await response.text();
      payload = rawText ? { detail: rawText.trim() } : {};
    }

    if (!response.ok) {
      const statusLabel = `${response.status} ${response.statusText}`.trim();
      throw new Error(
        payload.detail
          ? payload.detail
          : `Failed to generate quiz from the uploaded PDF (${statusLabel}).`,
      );
    }

    return payload;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error(`Could not reach the backend at ${API_BASE}. Is it running on port 8000?`);
    }
    throw error;
  }
}
