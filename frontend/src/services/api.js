/**
 * API Service for Hiver AI Support Agent
 *
 * Provides fault-tolerant, low-latency communication with the FastAPI backend.
 * Features:
 * - Default API URL: http://localhost:8000 (per assignment requirements)
 * - Environment variable override: VITE_API_URL
 * - Resilient loopback fallback (http://localhost:8000 <-> http://127.0.0.1:8000 <-> /api proxy)
 *   to handle Windows IPv6/IPv4 loopback resolution differences smoothly.
 * - Proactive background warm-up on page load.
 * - Timeout-guarded requests to prevent UI hanging.
 */

const DEFAULT_API_URL = 'http://localhost:8000';
const CONFIGURED_API_URL = import.meta.env.VITE_API_URL;

// Track active responsive base URL (defaults to configured URL or http://localhost:8000)
let activeBaseUrl = CONFIGURED_API_URL || DEFAULT_API_URL;
let hasProbed = false;

/**
 * Return list of candidate base URLs to try in priority order.
 */
function getCandidateBaseUrls() {
  if (CONFIGURED_API_URL) {
    return [CONFIGURED_API_URL, 'http://127.0.0.1:8000', DEFAULT_API_URL, ''];
  }
  if (activeBaseUrl === 'http://127.0.0.1:8000') {
    return ['http://127.0.0.1:8000', DEFAULT_API_URL, ''];
  }
  return [DEFAULT_API_URL, 'http://127.0.0.1:8000', ''];
}

/**
 * Helper to identify network or connection failures (backend offline / unreachable).
 */
function isNetworkError(error) {
  if (!error) return false;
  if (error.name === 'TypeError' || error.name === 'AbortError') return true;
  const msg = (error.message || '').toLowerCase();
  return (
    msg.includes('failed to fetch') ||
    msg.includes('networkerror') ||
    msg.includes('load failed') ||
    msg.includes('connection refused') ||
    msg.includes('network request failed') ||
    msg.includes('fetch failed') ||
    msg.includes('aborted') ||
    msg.includes('timed out') ||
    msg.includes('timeout')
  );
}

/**
 * Single fetch attempt with a strict timeout using AbortController.
 */
async function fetchWithTimeout(url, options = {}, timeoutMs = 4000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    return res;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Proactively probe available endpoints in the background to select the fastest
 * responsive endpoint (e.g. resolving Windows IPv6 localhost vs IPv4 127.0.0.1 delays).
 */
export async function warmUpApiConnection() {
  if (hasProbed) return activeBaseUrl;
  const candidates = getCandidateBaseUrls();

  for (const base of candidates) {
    try {
      const url = `${base}/api/health`;
      const res = await fetchWithTimeout(url, { method: 'GET' }, 1000);
      if (res && res.ok) {
        activeBaseUrl = base;
        hasProbed = true;
        return activeBaseUrl;
      }
    } catch {
      // Continue to next candidate
    }
  }
  return activeBaseUrl;
}

// Start warm-up immediately on module load in browser
if (typeof window !== 'undefined') {
  setTimeout(() => {
    warmUpApiConnection().catch(() => {});
  }, 50);
}

/**
 * Execute fetch request with automatic candidate fallback across localhost, 127.0.0.1, and proxy.
 */
async function fetchWithFallback(path, options = {}, timeoutMs = 12000) {
  // If user configured an explicit override via VITE_API_URL, try it first
  const candidates = getCandidateBaseUrls();
  let lastError = null;

  for (let i = 0; i < candidates.length; i++) {
    const base = candidates[i];
    const url = `${base}${path}`;
    // Use a snappy timeout for early probe hops to prevent Windows IPv6 SYN hanging
    const hopTimeout = i < candidates.length - 1 ? 2000 : timeoutMs;

    try {
      const res = await fetchWithTimeout(url, options, hopTimeout);
      // Successfully reached server! Cache this working endpoint
      activeBaseUrl = base;
      hasProbed = true;
      return res;
    } catch (err) {
      lastError = err;
      if (!isNetworkError(err)) {
        // Application/HTTP level error (not network drop)
        throw err;
      }
    }
  }

  throw lastError || new Error('Failed to connect to backend service.');
}

/**
 * Check backend health.
 */
export async function checkHealth() {
  const displayUrl = CONFIGURED_API_URL || (activeBaseUrl || DEFAULT_API_URL);
  try {
    const response = await fetchWithFallback('/api/health', { method: 'GET' }, 4000);
    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    throw new Error(
      isNetworkError(error)
        ? `FastAPI backend is offline or unavailable at ${displayUrl}. Ensure the backend is running from backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload (or run "npm run dev" from repository root).`
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

  const displayUrl = CONFIGURED_API_URL || (activeBaseUrl || DEFAULT_API_URL);

  try {
    const response = await fetchWithFallback('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: trimmed }),
    }, 15000);

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
        `FastAPI backend is offline or unavailable at ${displayUrl}. The frontend is operating normally, but cannot connect to the backend service. Ensure the backend server is running from the backend/ directory with: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload (or run "npm run dev" from repository root).`
      );
    }
    throw error;
  }
}

