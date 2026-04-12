import { api } from "@/lib/api";
import type { Reservation } from "@/api/reservations.api";
import type { User } from "@/api/users.api";
import type { AxiosRequestConfig } from "axios";

export interface MaintenanceWindow {
  id: number;
  club_id: number;
  aircraft_id: number;
  start_time: string;
  end_time: string;
  reason?: string;
}

export interface MaintenanceCreate {
  aircraft_id: number;
  start_time: string;
  end_time: string;
  reason?: string;
}

export const adminApi = {
  allReservations: async (config?: AxiosRequestConfig): Promise<Reservation[]> => {
    const res = await api.get("/api/v1/admin/reservations", config);
    return res.data;
  },
  listMaintenance: async (config?: AxiosRequestConfig): Promise<MaintenanceWindow[]> => {
    const res = await api.get("/api/v1/admin/maintenance", config);
    return res.data;
  },
  addMaintenance: async (data: MaintenanceCreate, config?: AxiosRequestConfig): Promise<MaintenanceWindow> => {
    const res = await api.post("/api/v1/admin/maintenance", data, config);
    return res.data;
  },
  deleteMaintenance: async (id: number, config?: AxiosRequestConfig): Promise<void> => {
    await api.delete(`/api/v1/admin/maintenance/${id}`, config);
  },
  listUsers: async (config?: AxiosRequestConfig): Promise<User[]> => {
    const res = await api.get("/api/v1/admin/users", config);
    return res.data;
  },
  addUser: async (data: any, config?: AxiosRequestConfig): Promise<User> => {
    const res = await api.post("/api/v1/admin/users", data, config);
    return res.data;
  },
};
