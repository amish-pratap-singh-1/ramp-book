import { api } from "@/lib/api";
import type { components } from "@/api/schema";
import type { AxiosRequestConfig } from "axios";

type LoginRequest = components["schemas"]["LoginRequest"];
type TokenResponse = components["schemas"]["TokenResponse"];

export const authApi = {
  login: async (data: LoginRequest, config?: AxiosRequestConfig): Promise<TokenResponse> => {
    const res = await api.post("/api/v1/auth/login", data, config);
    return res.data;
  },
};
