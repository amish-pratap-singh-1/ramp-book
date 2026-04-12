import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reservationsApi } from "@/api/reservations.api";
import { isAuthenticated } from "@/lib/auth";
import type { components } from "@/api/schema";

type ReservationCreateRequest = components["schemas"]["ReservationCreateRequest"];
type ReservationUpdateRequest = components["schemas"]["ReservationUpdateRequest"];
type FlightCompleteRequestWrapper = components["schemas"]["FlightCompleteRequestWrapper"];

export function useReservations() {
  return useQuery({
    queryKey: ["reservations"],
    queryFn: () => reservationsApi.list(),
    enabled: isAuthenticated(),
  });
}

export function useCreateReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ReservationCreateRequest) => reservationsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reservations"] }),
  });
}

export function useUpdateReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ReservationUpdateRequest }) =>
      reservationsApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reservations"] }),
  });
}

export function useCancelReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => reservationsApi.cancel(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reservations"] }),
  });
}

export function useCompleteReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: FlightCompleteRequestWrapper }) =>
      reservationsApi.complete(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reservations"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
    },
  });
}
