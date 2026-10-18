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
 * Evaluates readiness across backend dependencies including MySQL and Spark
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function checkReadiness() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/readiness`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Readiness check failed with status ${response.status}`,
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
      error: err.message || 'Failed to query readiness endpoint',
    };
  }
}

/**
 * Submits raw text for core linguistic and frequency analytics
 * @param {object} params
 * @param {string} params.text
 * @param {number} [params.top_n=10]
 * @param {boolean} [params.case_sensitive=false]
 * @param {string} [params.engine='python']
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

/**
 * Uploads a document (TXT, PDF, DOCX) for extraction and analysis
 * @param {object} params
 * @param {File} params.file
 * @param {number} [params.top_n=10]
 * @param {boolean} [params.case_sensitive=false]
 * @param {string} [params.engine='python']
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function analyzeFile({ file, top_n = 10, case_sensitive = false, engine = 'python' }) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_n', String(top_n));
    formData.append('case_sensitive', String(case_sensitive));
    formData.append('engine', String(engine));

    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/file`, {
      method: 'POST',
      body: formData,
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
      error: err.message || 'Failed to upload document to backend',
    };
  }
}

/**
 * Uploads an image (PNG, JPG, WEBP) for OCR text extraction and analysis
 * @param {object} params
 * @param {File} params.file
 * @param {number} [params.top_n=10]
 * @param {boolean} [params.case_sensitive=false]
 * @param {string} [params.engine='python']
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function analyzeImage({ file, top_n = 10, case_sensitive = false, engine = 'python' }) {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('top_n', String(top_n));
    formData.append('case_sensitive', String(case_sensitive));
    formData.append('engine', String(engine));

    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/image`, {
      method: 'POST',
      body: formData,
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
      error: err.message || 'Failed to upload and extract text from image',
    };
  }
}

/**
 * Submits a public webpage URL for SSRF-safe fetching and analysis
 * @param {object} params
 * @param {string} params.url
 * @param {number} [params.top_n=10]
 * @param {boolean} [params.case_sensitive=false]
 * @param {string} [params.engine='python']
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function analyzeUrl({ url, top_n = 10, case_sensitive = false, engine = 'python' }) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analysis/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({
        url,
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
      error: err.message || 'Failed to analyze webpage URL',
    };
  }
}

/**
 * Fetches paginated history records with optional filters
 * @param {object} [params]
 * @param {number} [params.skip=0]
 * @param {number} [params.limit=20]
 * @param {string} [params.source_type]
 * @param {string} [params.engine]
 * @param {string} [params.search]
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function fetchHistory(params = {}) {
  try {
    const query = new URLSearchParams();
    if (params.skip !== undefined) query.set('skip', String(params.skip));
    if (params.limit !== undefined) query.set('limit', String(params.limit));
    if (params.source_type && params.source_type !== 'all') query.set('source_type', params.source_type);
    if (params.engine && params.engine !== 'all') query.set('engine', params.engine);
    if (params.search && params.search.trim()) query.set('search', params.search.trim());

    const qs = query.toString();
    const url = `${API_BASE_URL}/api/v1/history${qs ? `?${qs}` : ''}`;
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      return {
        success: false,
        error: errorData?.detail || `Failed to fetch history (status ${response.status})`,
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
      error: err.message || 'Failed to fetch history records from database',
    };
  }
}

/**
 * Fetches high-level historical statistics (total runs, total words, last run)
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function fetchHistoryStats() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/stats`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Failed to fetch history statistics (status ${response.status})`,
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
      error: err.message || 'Failed to retrieve history statistics',
    };
  }
}

/**
 * Fetches complete historical analysis detail including reconstructed results payload
 * @param {number|string} id
 * @returns {Promise<{success: boolean, data?: object, error?: string}>}
 */
export async function fetchHistoryDetail(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/${id}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      return {
        success: false,
        error: errorData?.detail || `History record #${id} not found`,
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
      error: err.message || 'Failed to retrieve history record detail',
    };
  }
}

/**
 * Deletes a historical record by ID
 * @param {number|string} id
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function deleteHistoryRecord(id) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/history/${id}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      return {
        success: false,
        error: errorData?.detail || `Failed to delete record #${id}`,
      };
    }

    return {
      success: true,
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || 'Failed to delete history record',
    };
  }
}

/**
 * Exports current analysis data as an RFC 4180 compliant CSV document
 * and initiates a browser file download.
 * @param {object} analysisData Complete AnalysisResponse object
 * @returns {Promise<{success: boolean, error?: string}>}
 */
export async function exportAnalysisCsv(analysisData) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/export/csv`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(analysisData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const detail = errorData?.detail || `Error ${response.status}: ${response.statusText}`;
      return {
        success: false,
        error: detail,
      };
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const filename = `word_intelligence_analysis_${Date.now()}.csv`;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);

    return {
      success: true,
    };
  } catch (err) {
    return {
      success: false,
      error: err.message || 'Failed to export CSV report',
    };
  }
}

export default {
  checkHealth,
  checkReadiness,
  analyzeText,
  analyzeFile,
  analyzeUrl,
  fetchHistory,
  fetchHistoryStats,
  fetchHistoryDetail,
  deleteHistoryRecord,
  exportAnalysisCsv,
};
