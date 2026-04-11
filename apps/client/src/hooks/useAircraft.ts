import { useQuery } from "@tanstack/react-query";
import { aircraftApi } from "@/api/aircraft.api";
import { isAuthenticated } from "@/lib/auth";

export function useAircraft() {
  return useQuery({
    queryKey: ["aircraft"],
    queryFn: aircraftApi.list,
    enabled: isAuthenticated(),
  });
}
