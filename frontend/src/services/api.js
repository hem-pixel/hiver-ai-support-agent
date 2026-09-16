const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
/**
 * Helper to identify network or connection failures (backend offline / unreachable).
 */
function isNetworkError(error) {
  if (!error) return false;
  if (error.name === 'TypeError') return true;
  const msg = (error.message || '').toLowerCase();
  return (
    msg.includes('failed to fetch') ||
    msg.includes('networkerror') ||
    msg.includes('load failed') ||
    msg.includes('connection refused') ||
    msg.includes('network request failed') ||
    msg.includes('fetch failed')
  );
}

/**
 * Check backend health.
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      isNetworkError(error)
        ? `FastAPI backend is offline or unavailable at ${API_BASE_URL}. Ensure the backend is running from backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`
        : error.message
    );
  }
}

/**
 * Analyze customer support message via backend pipeline.
 *
 * @param {string} message - Customer inquiry text
 * @returns {Promise<Object>} Analyzed response
 */
export async function analyzeMessage(message) {
  const trimmed = (message || '').trim();
  if (!trimmed) {
    throw new Error('Please enter a customer message before analyzing.');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: trimmed }),
    });

    if (!response.ok) {
      let errorDetail = `Request failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson.details && Array.isArray(errJson.details)) {
          errorDetail = errJson.details.map(d => d.message).join('; ');
        } else if (errJson.detail) {
          errorDetail = errJson.detail;
        } else if (errJson.error) {
          errorDetail = errJson.error;
        }
      } catch {
        // Fallback to status text if response is not JSON
      }
      throw new Error(errorDetail);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (isNetworkError(error)) {
      throw new Error(
        `FastAPI backend is offline or unavailable at ${API_BASE_URL}. The frontend is operating normally, but cannot connect to the backend service. Ensure the backend server is running from the backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload (or run "npm run dev" from repository root).`
      );
    }
    throw error;
  }
}
