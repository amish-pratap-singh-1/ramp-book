import { api } from "@/lib/api";
import type { AxiosRequestConfig } from "axios";

export interface Aircraft {
  id: number;
  club_id: number;
  tail_number: string;
  model: string;
  year: number;
  hourly_rate_usd: number;
  total_hobbs_hours: number;
  status: "available" | "maintenance" | "retired";
  notes?: string;
}

export interface AircraftScheduleItem {
  id: number;
  start_time: string;
  end_time: string;
  type: "reservation" | "maintenance";
}

export interface AircraftCreate {
  tail_number: string;
  model: string;
  year: number;
  hourly_rate_usd: number;
  total_hobbs_hours?: number;
  notes?: string;
}

export const aircraftApi = {
  list: async (config?: AxiosRequestConfig): Promise<Aircraft[]> => {
    const res = await api.get("/api/v1/aircraft/", config);
    return res.data;
  },
  get: async (id: number, config?: AxiosRequestConfig): Promise<Aircraft> => {
    const res = await api.get(`/api/v1/aircraft/${id}`, config);
    return res.data;
  },
  getSchedule: async (id: number, config?: AxiosRequestConfig): Promise<AircraftScheduleItem[]> => {
    const res = await api.get(`/api/v1/aircraft/${id}/schedule`, config);
    return res.data;
  },
  create: async (data: AircraftCreate, config?: AxiosRequestConfig): Promise<Aircraft> => {
    const res = await api.post("/api/v1/aircraft/", data, config);
    return res.data;
  },
};
