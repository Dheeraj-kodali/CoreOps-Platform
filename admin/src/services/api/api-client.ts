import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { env } from '../../config/env';
import { TokenStorage } from '../../utils/token-storage';

export class ApiClient {
  private static instance: AxiosInstance;
  private static isRefreshing = false;
  private static failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: any) => void;
  }> = [];

  public static getInstance(): AxiosInstance {
    if (!ApiClient.instance) {
      ApiClient.instance = axios.create({
        baseURL: env.API_BASE_URL,
        timeout: env.REQUEST_TIMEOUT_MS,
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
      });

      ApiClient.setupInterceptors();
    }
    return ApiClient.instance;
  }

  private static setupInterceptors(): void {
    // Request Interceptor: Automatic JWT Injection & Request Tracking
    ApiClient.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = TokenStorage.getAccessToken();
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response Interceptor: Automatic Refresh Token Rotation & Retries
    ApiClient.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config;

        // If error is 401 Unauthorized and request hasn't been retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (ApiClient.isRefreshing) {
            return new Promise((resolve, reject) => {
              ApiClient.failedQueue.push({ resolve, reject });
            })
              .then((token) => {
                originalRequest.headers.Authorization = `Bearer ${token}`;
                return ApiClient.instance(originalRequest);
              })
              .catch((err) => Promise.reject(err));
          }

          originalRequest._retry = true;
          ApiClient.isRefreshing = true;

          const refreshToken = TokenStorage.getRefreshToken();
          if (!refreshToken) {
            ApiClient.handleSessionExpiration();
            return Promise.reject(error);
          }

          try {
            const response = await axios.post(`${env.API_BASE_URL}/auth/refresh`, {
              refresh_token: refreshToken,
            });

            const { access_token, refresh_token: new_refresh } = response.data;
            TokenStorage.setTokens(access_token, new_refresh || refreshToken);

            ApiClient.processQueue(null, access_token);
            ApiClient.isRefreshing = false;

            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return ApiClient.instance(originalRequest);
          } catch (refreshError) {
            ApiClient.processQueue(refreshError, null);
            ApiClient.isRefreshing = false;
            ApiClient.handleSessionExpiration();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(ApiClient.normalizeError(error));
      }
    );
  }

  private static processQueue(error: any, token: string | null = null): void {
    ApiClient.failedQueue.forEach((prom) => {
      if (error) {
        prom.reject(error);
      } else if (token) {
        prom.resolve(token);
      }
    });
    ApiClient.failedQueue = [];
  }

  private static handleSessionExpiration(): void {
    TokenStorage.clear();
    if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
      window.location.href = '/login?expired=1';
    }
  }

  private static normalizeError(error: any): { message: string; statusCode?: number; raw: any } {
    const message =
      error.response?.data?.detail || error.response?.data?.message || error.message || 'An unexpected error occurred';
    return {
      message,
      statusCode: error.response?.status,
      raw: error,
    };
  }
}

export const apiClient = ApiClient.getInstance();
