import { api } from "@/lib/api";

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
  list: async (): Promise<Aircraft[]> => {
    const res = await api.get("/api/v1/aircraft/");
    return res.data;
  },
  get: async (id: number): Promise<Aircraft> => {
    const res = await api.get(`/api/v1/aircraft/${id}`);
    return res.data;
  },
  getSchedule: async (id: number): Promise<AircraftScheduleItem[]> => {
    const res = await api.get(`/api/v1/aircraft/${id}/schedule`);
    return res.data;
  },
  create: async (data: AircraftCreate): Promise<Aircraft> => {
    const res = await api.post("/api/v1/aircraft/", data);
    return res.data;
  },
};
