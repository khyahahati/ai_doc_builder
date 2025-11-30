const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request(path, { method = "GET", body = null, headers = {} } = {}) {
  const opts = { method, headers: { ...headers } };

  if (body && typeof body === "object" && !(body instanceof URLSearchParams)) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  } else if (body instanceof URLSearchParams) {
    opts.headers["Content-Type"] = "application/x-www-form-urlencoded";
    opts.body = body.toString();
  } else if (body) {
    opts.body = body;
  }

  const res = await fetch(`${API_BASE_URL}${path}`, opts);
  const payload = await res.json().catch(() => null);
  if (!res.ok) {
    const message = (payload && payload.detail) || payload || `Request failed: ${res.status}`;
    const err = new Error(typeof message === "string" ? message : JSON.stringify(message));
    err.status = res.status;
    throw err;
  }
  return payload;
}

// Accept optional token for authenticated requests. Keep backward-compatible signatures.
export async function postJSON(path, data, token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return request(path, { method: "POST", body: data, headers });
}

export async function postForm(path, formParams, token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return request(path, { method: "POST", body: formParams, headers });
}

export async function get(path, token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  return request(path, { method: "GET", headers });
}

// Fetch a binary (file) response and return a blob. Throws on non-OK.
export async function download(path, token = null) {
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(`${API_BASE_URL}${path}`, { method: "GET", headers });
  if (!res.ok) {
    const payload = await res.json().catch(() => null);
    const message = (payload && payload.detail) || payload || `Request failed: ${res.status}`;
    const err = new Error(typeof message === "string" ? message : JSON.stringify(message));
    err.status = res.status;
    throw err;
  }
  const blob = await res.blob();
  return blob;
}

export default { postJSON, postForm, get, download };
