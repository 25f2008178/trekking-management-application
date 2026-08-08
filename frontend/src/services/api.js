/**
 * API service helper for interacting with Flask backend.
 * Handles JSON request formatting and credential inclusion for session cookies.
 */

async function request(url, options = {}) {
  const defaultHeaders = {
    'Accept': 'application/json',
  };

  if (options.body && typeof options.body === 'object' && !(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
    options.body = JSON.stringify(options.body);
  }

  options.headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  options.credentials = 'include';

  const response = await fetch(url, options);

  let data;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorMsg = (data && data.error) || (data && data.response && data.response.errors && data.response.errors[0]) || (typeof data === 'string' ? data : 'An error occurred');
    const err = new Error(errorMsg);
    err.status = response.status;
    err.data = data;
    throw err;
  }

  return data;
}

export const api = {
  get: (url, params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        query.append(key, val);
      }
    });
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return request(`${url}${queryString}`, { method: 'GET' });
  },

  post: (url, body) => request(url, { method: 'POST', body }),

  put: (url, body) => request(url, { method: 'PUT', body }),

  delete: (url) => request(url, { method: 'DELETE' }),
};
