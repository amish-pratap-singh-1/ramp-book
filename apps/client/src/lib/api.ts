import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { clearToken, getToken } from "@/lib/auth";
import { toast } from "sonner";

// Extend Axios configuration to support custom toast properties
declare module "axios" {
  export interface AxiosRequestConfig {
    showToast?: boolean;
    successMessage?: string;
    errorMessage?: string;
  }
}

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor — attach Bearer token
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handle toasts and errors
api.interceptors.response.use(
  (response) => {
    const config = response.config as InternalAxiosRequestConfig & {
      showToast?: boolean;
      successMessage?: string;
    };

    if (config.showToast) {
      toast.success(config.successMessage || "Action successful");
    }
    return response;
  },
  async (error: AxiosError<{ message?: string }>) => {
    const config = error.config as InternalAxiosRequestConfig & {
      showToast?: boolean;
      errorMessage?: string;
    };

    // Handle 401 specifically
    if (error.response?.status === 401) {
      clearToken();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      return Promise.reject(error);
    }

    // Default to showing error toasts unless explicitly disabled
    if (config?.showToast !== false) {
      let message = config?.errorMessage;

      if (!message) {
        const status = error.response?.status;
        const serverMessage = error.response?.data?.message;

        if (serverMessage) {
          message = serverMessage;
        } else {
          switch (status) {
            case 400:
              message = "Invalid request. Please check your input.";
              break;
            case 403:
              message = "You don't have permission to perform this action.";
              break;
            case 404:
              message = "The requested resource was not found.";
              break;
            case 500:
              message = "A server error occurred. Please try again later.";
              break;
            default:
              message = "Something went wrong. Please try again.";
          }
        }
      }

      toast.error(message);
    }

    return Promise.reject(error);
  },
);
