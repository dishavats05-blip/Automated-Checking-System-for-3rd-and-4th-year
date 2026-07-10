// Talks to Track4/intern_i_backend_engine. In dev, Vite proxies /api ->
// http://localhost:8001 (see vite.config.js). Every write (the PATCH
// override) fires immediately on user action so the mark updates without
// a page reload — see ScoreEditor.jsx.

const BASE = "/api";

async function request(path, options = {}) {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status}: ${body}`);
  }
  return response.json();
}

export async function uploadScript(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/upload", { method: "POST", body: formData, headers: {} });
}

export function getTaskStatus(taskId) {
  return request(`/tasks/${taskId}`);
}

export function getReviewQueue() {
  return request("/review-queue");
}

export function overrideScore(scriptId, questionId, { reviewerId, correctedScore, reason }) {
  return request(`/scripts/${scriptId}/questions/${questionId}/score`, {
    method: "PATCH",
    body: JSON.stringify({
      reviewer_id: reviewerId,
      corrected_score: correctedScore,
      reason,
    }),
  });
}
