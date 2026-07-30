export const env = {
  API_BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  REQUEST_TIMEOUT_MS: 15000, // 15 seconds
  MAX_RETRIES: 2,
};
