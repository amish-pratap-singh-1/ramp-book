import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/api/auth.api";

export function useLogin() {
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      localStorage.setItem("access_token", data.access_token);
    },
  });
}
