import { api } from "@/lib/api";
import type { components } from "@/api/schema";

type LoginRequest = components["schemas"]["LoginRequest"];
type TokenResponse = components["schemas"]["TokenResponse"];

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await api.post("/api/v1/auth/login", data);
    return res.data;
  },
};
