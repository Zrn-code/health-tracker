// API Configuration
const API_CONFIG = {
  // Use environment variable or fallback to relative path for production
  BASE_URL:
    import.meta.env.VITE_API_BASE_URL ||
    "https://health-tracker-340210095480.asia-east1.run.app",
  TIMEOUT: 10000, // 10 seconds timeout
  RETRY_ATTEMPTS: 3,
};

// Helper function to build full API URL
export const buildApiUrl = (endpoint) => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint.slice(1) : endpoint;

  // In development, use the full URL to the deployed backend
  if (import.meta.env.DEV) {
    return `${API_CONFIG.BASE_URL}/api/${cleanEndpoint}`;
  }

  // In production, use relative path if BASE_URL is not set
  if (!API_CONFIG.BASE_URL || API_CONFIG.BASE_URL === "/api") {
    return `/api/${cleanEndpoint}`;
  }

  return `${API_CONFIG.BASE_URL}/api/${cleanEndpoint}`;
};

// Enhanced fetch with error handling and retry logic
export const apiRequest = async (endpoint, options = {}) => {
  const url = buildApiUrl(endpoint);

  // Set default headers
  const defaultHeaders = {
    Accept: "application/json",
  };

  // Add Content-Type for requests with body
  if (options.body && typeof options.body === "string") {
    defaultHeaders["Content-Type"] = "application/json";
  }

  const defaultOptions = {
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
    timeout: API_CONFIG.TIMEOUT,
    mode: "cors", // Explicitly set CORS mode
    credentials: "omit", // Don't send credentials for cross-origin requests
  };

  const config = { ...defaultOptions, ...options };

  let lastError;

  for (let attempt = 1; attempt <= API_CONFIG.RETRY_ATTEMPTS; attempt++) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), config.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      lastError = error;

      // Don't retry on client errors (4xx) or abort
      if (
        error.name === "AbortError" ||
        (error.status >= 400 && error.status < 500)
      ) {
        throw error;
      }

      // Only retry on network errors or 5xx errors
      if (attempt < API_CONFIG.RETRY_ATTEMPTS) {
        // Exponential backoff: wait 1s, 2s, 4s
        await new Promise((resolve) =>
          setTimeout(resolve, 1000 * Math.pow(2, attempt - 1))
        );
        continue;
      }
    }
  }

  throw lastError;
};

export default API_CONFIG;
