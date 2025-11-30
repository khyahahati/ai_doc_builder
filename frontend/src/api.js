const DEFAULT_BASE_URL = "http://127.0.0.1:8000";

function resolveBaseUrl() {
  const envUrl = import.meta?.env?.VITE_API_BASE_URL;
  const candidate = envUrl && typeof envUrl === "string" ? envUrl.trim() : "";

  if (!candidate) {
    return DEFAULT_BASE_URL;
  }

  return candidate.endsWith("/") ? candidate.slice(0, -1) : candidate;
}

const BASE_URL = resolveBaseUrl();

function normalizePath(path) {
  if (!path) {
    return "/";
  }

  return path.startsWith("/") ? path : `/${path}`;
}

async function request(path, { method = "GET", headers: extraHeaders, body } = {}, token) {
  const url = `${BASE_URL}${normalizePath(path)}`;
  const headers = new Headers(extraHeaders || {});

  if (!headers.has("Accept")) {
    headers.set("Accept", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(url, {
    method,
    headers,
    body,
    credentials: "same-origin",
  });

  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");
  const text = await response.text();
  const payload = isJson && text ? safeJsonParse(text) : text;

  if (!response.ok) {
    const detail = typeof payload === "string" ? payload : payload?.detail || payload?.message;
    const message = detail || `Request to ${url} failed with status ${response.status}`;
    throw new Error(message);
  }

  if (!text) {
    return null;
  }

  return payload;
}

function safeJsonParse(value) {
  try {
    return JSON.parse(value);
  } catch (error) {
    console.warn("Failed to parse JSON response", error);
    return value;
  }
}

async function postForm(path, formData, token) {
  let body = formData;
  const headers = {};

  if (formData instanceof URLSearchParams) {
    headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8";
    body = formData.toString();
  } else if (formData instanceof FormData) {
    // Let the browser compute the boundary header automatically.
  } else if (formData && typeof formData === "object") {
    headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8";
    body = new URLSearchParams(formData).toString();
  }

  return request(path, { method: "POST", headers, body }, token);
}

async function sendJson(path, data, token, method = "POST") {
  const headers = { "Content-Type": "application/json" };
  const body = data == null ? null : JSON.stringify(data);

  return request(path, { method, headers, body }, token);
}

const api = {
  get(path, token) {
    return request(path, { method: "GET" }, token);
  },
  postJSON(path, data, token) {
    return sendJson(path, data, token, "POST");
  },
  putJSON(path, data, token) {
    return sendJson(path, data, token, "PUT");
  },
  patchJSON(path, data, token) {
    return sendJson(path, data, token, "PATCH");
  },
  postForm,
  delete(path, token) {
    return request(path, { method: "DELETE" }, token);
  },
  request,
  BASE_URL,
};

export default api;
export { BASE_URL };
