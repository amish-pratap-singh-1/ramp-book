import { api } from "@/lib/api";
import type { components } from "@/api/schema";
import type { AxiosRequestConfig } from "axios";

type AircraftListResponse = components["schemas"]["AircraftListResponse"];
type AircraftResponseWrapper = components["schemas"]["AircraftResponseWrapper"];
type AircraftCreateRequest = components["schemas"]["AircraftCreateRequest"];
type AircraftScheduleListResponse = components["schemas"]["AircraftScheduleListResponse"];

export const aircraftApi = {
  list: async (config?: AxiosRequestConfig): Promise<AircraftListResponse> => {
    const res = await api.get("/api/v1/aircraft/", config);
    return res.data;
  },
  get: async (id: number, config?: AxiosRequestConfig): Promise<AircraftResponseWrapper> => {
    const res = await api.get(`/api/v1/aircraft/${id}`, config);
    return res.data;
  },
  getSchedule: async (id: number, config?: AxiosRequestConfig): Promise<AircraftScheduleListResponse> => {
    const res = await api.get(`/api/v1/aircraft/${id}/schedule`, config);
    return res.data;
  },
  create: async (data: AircraftCreateRequest, config?: AxiosRequestConfig): Promise<AircraftResponseWrapper> => {
    const res = await api.post("/api/v1/aircraft/", data, config);
    return res.data;
  },
};
