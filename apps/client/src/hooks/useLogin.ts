import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/router";
import { authApi } from "@/api/auth.api";
import { setToken } from "@/lib/auth";

export function useLogin() {
  const router = useRouter();
  return useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      setToken(data.access_token);
      router.push("/dashboard");
    },
  });
}
