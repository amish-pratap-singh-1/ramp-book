import { api } from "@/lib/api";

export interface ReservationMember {
  id: number;
  full_name: string;
  email: string;
}

export interface ReservationAircraft {
  id: number;
  tail_number: string;
  model: string;
  hourly_rate_usd: number;
}

export interface Reservation {
  id: number;
  club_id: number;
  aircraft_id: number;
  member_id: number;
  instructor_id?: number;
  start_time: string;
  end_time: string;
  status: "confirmed" | "cancelled" | "completed";
  hobbs_start?: number;
  hobbs_end?: number;
  notes?: string;
  aircraft?: ReservationAircraft;
  member?: ReservationMember;
  instructor?: ReservationMember;
}

export interface ReservationCreate {
  aircraft_id: number;
  instructor_id?: number;
  start_time: string;
  end_time: string;
  notes?: string;
}

export interface ReservationUpdate {
  instructor_id?: number;
  start_time?: string;
  end_time?: string;
  notes?: string;
}

export interface FlightComplete {
  hobbs_start: number;
  hobbs_end: number;
}

export const reservationsApi = {
  list: async (): Promise<Reservation[]> => {
    const res = await api.get("/api/v1/reservations/");
    return res.data;
  },
  get: async (id: number): Promise<Reservation> => {
    const res = await api.get(`/api/v1/reservations/${id}`);
    return res.data;
  },
  create: async (data: ReservationCreate): Promise<Reservation> => {
    const res = await api.post("/api/v1/reservations/", data);
    return res.data;
  },
  update: async (id: number, data: ReservationUpdate): Promise<Reservation> => {
    const res = await api.patch(`/api/v1/reservations/${id}`, data);
    return res.data;
  },
  cancel: async (id: number): Promise<Reservation> => {
    const res = await api.delete(`/api/v1/reservations/${id}`);
    return res.data;
  },
  complete: async (id: number, data: FlightComplete): Promise<Reservation> => {
    const res = await api.post(`/api/v1/reservations/${id}/complete`, data);
    return res.data;
  },
};
