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

export default {
  checkHealth,
};
