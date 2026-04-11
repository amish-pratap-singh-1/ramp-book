import { useQuery } from "@tanstack/react-query";
import { usersApi } from "@/api/users.api";
import { isAuthenticated } from "@/lib/auth";

export function useInstructors() {
  return useQuery({
    queryKey: ["instructors"],
    queryFn: usersApi.instructors,
    enabled: isAuthenticated(),
    staleTime: 120_000,
  });
}
