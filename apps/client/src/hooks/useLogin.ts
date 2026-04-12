import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { authApi } from "@/api/auth.api";
import { setToken } from "@/lib/auth";

export function useLogin() {
  const router = useRouter();
  return useMutation({
    mutationFn: (data: any) =>
      authApi.login(data, {
        showToast: true,
        successMessage: "Welcome back! Redirecting you now...",
      }),
    onSuccess: (data) => {
      setToken(data.access_token);
      router.replace("/dashboard");
    },
  });
}
