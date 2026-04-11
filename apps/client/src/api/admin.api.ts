import { api } from "@/lib/api";
import type { Reservation } from "@/api/reservations.api";

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
  allReservations: async (): Promise<Reservation[]> => {
    const res = await api.get("/api/v1/admin/reservations");
    return res.data;
  },
  listMaintenance: async (): Promise<MaintenanceWindow[]> => {
    const res = await api.get("/api/v1/admin/maintenance");
    return res.data;
  },
  addMaintenance: async (data: MaintenanceCreate): Promise<MaintenanceWindow> => {
    const res = await api.post("/api/v1/admin/maintenance", data);
    return res.data;
  },
  deleteMaintenance: async (id: number): Promise<void> => {
    await api.delete(`/api/v1/admin/maintenance/${id}`);
  },
};
