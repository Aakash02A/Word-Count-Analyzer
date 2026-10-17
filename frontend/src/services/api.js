/**
 * Word Intelligence API Client
 * Centralizes all HTTP communications between React frontend and FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

/**
 * Checks system health and liveness
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Server returned status ${response.status}: ${response.statusText}`,
      };
    }

    const data = await response.json();
    return {
      success: true,
      data,
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || 'Unable to connect to Word Intelligence backend',
    };
  }
}

/**
 * Submits raw text for core linguistic and frequency analytics
 * @param {object} params
 * @param {string} params.text
 * @param {number} [params.top_n=10]
 * @param {boolean} [params.case_sensitive=false]
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function analyzeText({ text, top_n = 10, case_sensitive = false, engine = 'python' }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        text,
        top_n: Number(top_n),
        case_sensitive: Boolean(case_sensitive),
        engine: String(engine),
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const detail = errorData?.detail || `Error ${response.status}: ${response.statusText}`;
      return {
        success: false,
        error: detail,
      };
    }

    const data = await response.json();
    return {
      success: true,
      data,
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || 'Failed to submit analysis request to backend',
    };
  }
}

export default {
  checkHealth,
  analyzeText,
};
