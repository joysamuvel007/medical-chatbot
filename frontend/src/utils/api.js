
const BASE_URL = '/';  

/**
 * Send a chat message to the backend pipeline.
 * 
 * @param {string} userMessage - What the user typed
 * @param {string|null} sessionId - Existing session ID, or null for new
 * @returns {Promise<object>} ChatResponse from the backend
 */
export async function sendMessage(userMessage, sessionId = null) {
  const response = await fetch(`${BASE_URL}chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_message: userMessage,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Check if the backend and Ollama are healthy.
 * @returns {Promise<object>} { status, ollama_running, available_models }
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${BASE_URL}health`);
    return response.json();
  } catch {
    return { status: 'unreachable', ollama_running: false, available_models: [] };
  }
}

/**
 * Delete a session (for "New Chat" button).
 * @param {string} sessionId
 */
export async function clearSession(sessionId) {
  await fetch(`${BASE_URL}session/${sessionId}`, { method: 'DELETE' });
}