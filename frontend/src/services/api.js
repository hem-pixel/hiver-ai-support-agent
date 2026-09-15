const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
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
      error.message.includes('Failed to fetch')
        ? 'Backend service is unavailable. Please ensure the FastAPI server is running on http://localhost:8000.'
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
    if (error.message.includes('Failed to fetch') || error.name === 'TypeError') {
      throw new Error(
        'Backend server is unavailable. Please start the FastAPI backend on http://localhost:8000 (uvicorn app.main:app --port 8000).'
      );
    }
    throw error;
  }
}
