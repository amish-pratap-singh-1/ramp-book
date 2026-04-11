import { api } from "@/lib/api";

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
  me: async (): Promise<User> => {
    const res = await api.get("/api/v1/users/me");
    return res.data;
  },
  instructors: async (): Promise<User[]> => {
    const res = await api.get("/api/v1/users/instructors");
    return res.data;
  },
};
