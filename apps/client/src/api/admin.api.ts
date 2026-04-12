import { api } from "@/lib/api";
import type { components } from "@/api/schema";
import type { AxiosRequestConfig } from "axios";

type ReservationListResponse = components["schemas"]["ReservationListResponse"];
type MaintenanceWindowListResponse = components["schemas"]["MaintenanceWindowListResponse"];
type MaintenanceWindowResponseWrapper = components["schemas"]["MaintenanceWindowResponseWrapper"];
type MaintenanceWindowCreateRequest = components["schemas"]["MaintenanceWindowCreateRequest"];
type UserListResponse = components["schemas"]["UserListResponse"];
type UserResponseWrapper = components["schemas"]["UserResponseWrapper"];
type UserCreateRequest = components["schemas"]["UserCreateRequest"];

export const adminApi = {
  allReservations: async (config?: AxiosRequestConfig): Promise<ReservationListResponse> => {
    const res = await api.get("/api/v1/admin/reservations", config);
    return res.data;
  },
  listMaintenance: async (config?: AxiosRequestConfig): Promise<MaintenanceWindowListResponse> => {
    const res = await api.get("/api/v1/admin/maintenance", config);
    return res.data;
  },
  addMaintenance: async (data: MaintenanceWindowCreateRequest, config?: AxiosRequestConfig): Promise<MaintenanceWindowResponseWrapper> => {
    const res = await api.post("/api/v1/admin/maintenance", data, config);
    return res.data;
  },
  deleteMaintenance: async (id: number, config?: AxiosRequestConfig): Promise<void> => {
    await api.delete(`/api/v1/admin/maintenance/${id}`, config);
  },
  listUsers: async (config?: AxiosRequestConfig): Promise<UserListResponse> => {
    const res = await api.get("/api/v1/admin/users", config);
    return res.data;
  },
  addUser: async (data: UserCreateRequest, config?: AxiosRequestConfig): Promise<UserResponseWrapper> => {
    const res = await api.post("/api/v1/admin/users", data, config);
    return res.data;
  },
};
