import { api } from "@/lib/api";
import type { AxiosRequestConfig } from "axios";

export interface User {
  id: number;
  club_id: number;
  email: string;
  full_name: string;
  role: "member" | "instructor" | "admin";
  certificate?: string;
  ratings?: string;
  is_active: boolean;
}

export const usersApi = {
  me: async (config?: AxiosRequestConfig): Promise<User> => {
    const res = await api.get("/api/v1/users/me", config);
    return res.data;
  },
  instructors: async (config?: AxiosRequestConfig): Promise<User[]> => {
    const res = await api.get("/api/v1/users/instructors", config);
    return res.data;
  },
};
