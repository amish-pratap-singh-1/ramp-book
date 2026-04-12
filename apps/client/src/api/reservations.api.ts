import { api } from "@/lib/api";
import type { components } from "@/api/schema";
import type { AxiosRequestConfig } from "axios";

type ReservationListResponse = components["schemas"]["ReservationListResponse"];
type ReservationResponseWrapper = components["schemas"]["ReservationResponseWrapper"];
type ReservationCreateRequest = components["schemas"]["ReservationCreateRequest"];
type ReservationUpdateRequest = components["schemas"]["ReservationUpdateRequest"];
type FlightCompleteRequestWrapper = components["schemas"]["FlightCompleteRequestWrapper"];

export const reservationsApi = {
  list: async (config?: AxiosRequestConfig): Promise<ReservationListResponse> => {
    const res = await api.get("/api/v1/reservations/", config);
    return res.data;
  },
  get: async (id: number, config?: AxiosRequestConfig): Promise<ReservationResponseWrapper> => {
    const res = await api.get(`/api/v1/reservations/${id}`, config);
    return res.data;
  },
  create: async (data: ReservationCreateRequest, config?: AxiosRequestConfig): Promise<ReservationResponseWrapper> => {
    const res = await api.post("/api/v1/reservations/", data, config);
    return res.data;
  },
  update: async (id: number, data: ReservationUpdateRequest, config?: AxiosRequestConfig): Promise<ReservationResponseWrapper> => {
    const res = await api.patch(`/api/v1/reservations/${id}`, data, config);
    return res.data;
  },
  cancel: async (id: number, config?: AxiosRequestConfig): Promise<ReservationResponseWrapper> => {
    const res = await api.delete(`/api/v1/reservations/${id}`, config);
    return res.data;
  },
  complete: async (id: number, data: FlightCompleteRequestWrapper, config?: AxiosRequestConfig): Promise<ReservationResponseWrapper> => {
    const res = await api.post(`/api/v1/reservations/${id}/complete`, data, config);
    return res.data;
  },
};
