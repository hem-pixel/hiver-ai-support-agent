const CONFIGURED_API_URL = import.meta.env.VITE_API_URL;
let activeBaseUrl = CONFIGURED_API_URL || 'http://localhost:8000';

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
 * Execute fetch request with automatic loopback fallback between localhost and 127.0.0.1.
 * On Windows, localhost often resolves to IPv6 [::1] while Uvicorn binds to IPv4 127.0.0.1.
 * Fallback ensures seamless connection across all environments.
 */
async function fetchWithFallback(path, options = {}) {
  // If user configured an explicit override via VITE_API_URL, use it directly
  if (CONFIGURED_API_URL) {
    return fetch(`${CONFIGURED_API_URL}${path}`, options);
  }

  try {
    const res = await fetch(`${activeBaseUrl}${path}`, options);
    return res;
  } catch (err) {
    if (isNetworkError(err)) {
      const alternateUrl =
        activeBaseUrl === 'http://localhost:8000'
          ? 'http://127.0.0.1:8000'
          : 'http://localhost:8000';

      try {
        const altRes = await fetch(`${alternateUrl}${path}`, options);
        activeBaseUrl = alternateUrl; // Cache the responsive endpoint
        return altRes;
      } catch {
        // If direct port fails, try relative path through Vite dev proxy
        try {
          const proxyRes = await fetch(path, options);
          activeBaseUrl = '';
          return proxyRes;
        } catch {
          // All strategies exhausted
        }
      }
    }
    throw err;
  }
}

/**
 * Check backend health.
 */
export async function checkHealth() {
  try {
    const response = await fetchWithFallback('/api/health');
    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      isNetworkError(error)
        ? `FastAPI backend is offline or unavailable at ${activeBaseUrl}. Ensure the backend is running from backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload (or run "npm run dev" from repository root).`
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
    const response = await fetchWithFallback('/api/analyze', {
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
        `FastAPI backend is offline or unavailable at ${activeBaseUrl}. The frontend is operating normally, but cannot connect to the backend service. Ensure the backend server is running from the backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload (or run "npm run dev" from repository root).`
      );
    }
    throw error;
  }
}
