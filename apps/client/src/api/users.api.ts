import { api } from "@/lib/api";
import type { components } from "@/api/schema";
import type { AxiosRequestConfig } from "axios";

type UserResponseWrapper = components["schemas"]["UserResponseWrapper"];
type UserListResponse = components["schemas"]["UserListResponse"];

export const usersApi = {
  me: async (config?: AxiosRequestConfig): Promise<UserResponseWrapper> => {
    const res = await api.get("/api/v1/users/me", config);
    return res.data;
  },
  instructors: async (config?: AxiosRequestConfig): Promise<UserListResponse> => {
    const res = await api.get("/api/v1/users/instructors", config);
    return res.data;
  },
};
