import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/api/users.api";
import { isAuthenticated } from "@/lib/auth";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: usersApi.me,
    enabled: isAuthenticated(),
    staleTime: 60_000,
  });
}
