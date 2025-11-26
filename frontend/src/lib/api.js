const rawBaseUrl = import.meta.env.VITE_API_BASE_URL ?? '';
const normalizedBaseUrl = rawBaseUrl.endsWith('/')
  ? rawBaseUrl.slice(0, -1)
  : rawBaseUrl;

export const buildApiUrl = (path) => {
  if (!path) {
    return normalizedBaseUrl;
  }
  if (normalizedBaseUrl) {
    return `${normalizedBaseUrl}${path}`;
  }
  return path;
};

export const getApiBaseUrl = () => normalizedBaseUrl;

