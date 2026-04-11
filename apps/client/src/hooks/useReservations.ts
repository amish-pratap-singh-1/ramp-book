import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { reservationsApi, type ReservationCreate, type ReservationUpdate, type FlightComplete } from "@/api/reservations.api";
import { isAuthenticated } from "@/lib/auth";

export function useReservations() {
  return useQuery({
    queryKey: ["reservations"],
    queryFn: reservationsApi.list,
    enabled: isAuthenticated(),
  });
}

export function useCreateReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ReservationCreate) => reservationsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reservations"] }),
  });
}

export function useUpdateReservation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ReservationUpdate }) =>
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
    mutationFn: ({ id, data }: { id: number; data: FlightComplete }) =>
      reservationsApi.complete(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reservations"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
    },
  });
}
