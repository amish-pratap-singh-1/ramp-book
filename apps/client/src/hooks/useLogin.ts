import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { authApi } from "@/api/auth.api";
import { setToken } from "@/lib/auth";
import type { components } from "@/api/schema";

type LoginRequest = components["schemas"]["LoginRequest"];

export function useLogin() {
  const router = useRouter();
  return useMutation({
    mutationFn: (data: LoginRequest) =>
      authApi.login(data, {
        showToast: true,
        successMessage: "Welcome back! Redirecting you now...",
      }),
    onSuccess: (data) => {
      setToken(data.user.access_token);
      router.replace("/dashboard");
    },
  });
}
