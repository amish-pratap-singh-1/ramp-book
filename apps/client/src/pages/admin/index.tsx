import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import StatusBadge from "@/components/StatusBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { adminApi } from "@/api/admin.api";
import { useAircraft } from "@/hooks/useAircraft";
import { isAuthenticated, getUserRole } from "@/lib/auth";
import type { components } from "@/api/schema";

function fmt(iso: string) {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}
function toLocal(iso: string) {
  return new Date(iso).toISOString();
}

export default function AdminPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"reservations" | "maintenance" | "users">("reservations");
  const [showMaintForm, setShowMaintForm] = useState(false);
  const [showUserForm, setShowUserForm] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else if (getUserRole() !== "admin") {
      router.replace("/dashboard");
    }
  }, [router]);

  const { data: reservationsData, isLoading: resLoading } = useQuery({
    queryKey: ["admin_reservations"],
    queryFn: () => adminApi.allReservations(),
    enabled: isAuthenticated() && getUserRole() === "admin",
  });
  const reservations = reservationsData?.reservations ?? [];

  const { data: maintenanceData, isLoading: maintLoading } = useQuery({
    queryKey: ["admin_maintenance"],
    queryFn: () => adminApi.listMaintenance(),
    enabled: isAuthenticated() && getUserRole() === "admin",
  });
  const maintenance = maintenanceData?.maintenance_windows ?? [];

  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ["admin_users"],
    queryFn: () => adminApi.listUsers(),
    enabled: isAuthenticated() && getUserRole() === "admin",
  });
  const users = usersData?.users ?? [];

  const { data: aircraftData } = useAircraft();
  const aircraft = aircraftData?.aircraft ?? [];

  const createMaint = useMutation({
    mutationFn: (data: components["schemas"]["MaintenanceWindowCreateRequest"]) => adminApi.addMaintenance(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin_maintenance"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
      setShowMaintForm(false);
      reset();
    },
  });

  const deleteMaint = useMutation({
    mutationFn: (id: number) => adminApi.deleteMaintenance(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin_maintenance"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
    },
  });

  const createUser = useMutation({
    mutationFn: (data: components["schemas"]["UserCreateRequest"]) => adminApi.addUser(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin_users"] });
      setShowUserForm(false);
      userForm.reset();
    },
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<{
    aircraft_id: string;
    start_time: string;
    end_time: string;
    reason: string;
  }>();

  type UserFormData = {
    email: string;
    password: string;
    full_name: string;
    role: "member" | "instructor" | "admin";
  };

  const userForm = useForm<UserFormData>({
    defaultValues: { role: "member" }
  });

  if (resLoading || maintLoading || usersLoading) return <LoadingSpinner fullPage />;

  const onSubmit = (data: { aircraft_id: string; start_time: string; end_time: string; reason: string }) => {
    createMaint.mutate({
      maintenance_window: {
        aircraft_id: parseInt(data.aircraft_id),
        start_time: toLocal(data.start_time),
        end_time: toLocal(data.end_time),
        reason: data.reason || undefined,
      }
    });
  };

  const sortedRes = [...reservations].sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  const sortedMaint = [...maintenance].sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  const sortedUsers = [...users].sort((a, b) => a.full_name.localeCompare(b.full_name));

  const onUserSubmit = (data: UserFormData) => {
    createUser.mutate({ user: data });
  };

  return (
    <>
      <Head>
        <title>Admin Panel — RampBook</title>
      </Head>
      <Layout>
        <div className="page-header">
          <h1 className="page-title">Admin Panel</h1>
          <p className="page-sub">Club management and oversight</p>
        </div>

        <div className="page-body space-y-6">
          <div className="tabs">
            <button className={tab === "reservations" ? "tab-active" : "tab"} onClick={() => setTab("reservations")}>
              All Club Bookings
            </button>
            <button className={tab === "maintenance" ? "tab-active" : "tab"} onClick={() => setTab("maintenance")}>
              Maintenance
            </button>
            <button className={tab === "users" ? "tab-active" : "tab"} onClick={() => setTab("users")}>
              Users
            </button>
          </div>

          {tab === "reservations" && (
            <div className="tbl-wrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Aircraft</th>
                    <th>Member</th>
                    <th>Instructor</th>
                    <th>Departure</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sortedRes.length === 0 ? (
                    <tr><td colSpan={5} className="text-center py-8 text-muted">No reservations found.</td></tr>
                  ) : (
                    sortedRes.map((r) => (
                      <tr key={r.id}>
                        <td><span className="font-bold text-accent font-mono">{r.aircraft?.tail_number}</span></td>
                        <td>{r.member?.full_name}</td>
                        <td className="text-secondary">{r.instructor?.full_name ?? "—"}</td>
                        <td>{fmt(r.start_time)}</td>
                        <td><StatusBadge status={r.status} /></td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          )}

          {tab === "maintenance" && (
            <div className="space-y-6">
              <div className="flex justify-end">
                <button onClick={() => setShowMaintForm(!showMaintForm)} className="btn-primary">
                  {showMaintForm ? "Close Form" : "➕ Add Maintenance Window"}
                </button>
              </div>

              {showMaintForm && (
                <div className="card max-w-lg mb-6 shadow-xl border-accent/20">
                  <h2 className="section-title mb-4">New Maintenance Window</h2>
                  <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
                    <div className="field">
                      <label className="label">Aircraft</label>
                      <select {...register("aircraft_id", { required: "Required" })} className="select-input">
                        <option value="">— Select Aircraft —</option>
                        {aircraft.map(a => <option key={a.id} value={a.id}>{a.tail_number}</option>)}
                      </select>
                      {errors.aircraft_id && <p className="err">{errors.aircraft_id.message}</p>}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="field">
                        <label className="label">Start</label>
                        <input type="datetime-local" {...register("start_time", { required: "Required" })} className="input" />
                      </div>
                      <div className="field">
                        <label className="label">End</label>
                        <input type="datetime-local" {...register("end_time", { required: "Required" })} className="input" />
                      </div>
                    </div>
                    <div className="field">
                      <label className="label">Reason</label>
                      <input type="text" {...register("reason")} placeholder="e.g. 100-hour inspection" className="input" />
                    </div>
                    <div className="flex justify-end gap-3 mt-2">
                      <button type="submit" disabled={createMaint.isPending} className="btn-primary">
                        {createMaint.isPending ? "Saving…" : "Save"}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="tbl-wrap">
                <table className="tbl">
                  <thead>
                    <tr>
                      <th>Aircraft (ID)</th>
                      <th>Start</th>
                      <th>End</th>
                      <th>Reason</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedMaint.length === 0 ? (
                      <tr><td colSpan={5} className="text-center py-8 text-muted">No scheduled maintenance.</td></tr>
                    ) : (
                      sortedMaint.map(m => {
                        const ac = aircraft.find(a => a.id === m.aircraft_id);
                        return (
                          <tr key={m.id}>
                            <td><span className="font-bold text-warn font-mono">{ac?.tail_number ?? m.aircraft_id}</span></td>
                            <td>{fmt(m.start_time)}</td>
                            <td>{fmt(m.end_time)}</td>
                            <td>{m.reason || "—"}</td>
                            <td>
                              <button
                                onClick={() => { if(confirm("Remove?")) deleteMaint.mutate(m.id); }}
                                className="btn-danger btn-sm"
                                disabled={deleteMaint.isPending}
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {tab === "users" && (
            <div className="space-y-6">
              <div className="flex justify-end">
                <button onClick={() => setShowUserForm(!showUserForm)} className="btn-primary">
                  {showUserForm ? "Close Form" : "➕ Add User"}
                </button>
              </div>

              {showUserForm && (
                <div className="card max-w-lg mb-6 shadow-xl border-accent/20">
                  <h2 className="section-title mb-4">Provision New Account</h2>
                  {createUser.isError && (
                    <div className="mb-4 text-sm text-danger bg-danger/10 p-3 rounded">{String((createUser.error as any)?.response?.data?.detail || "Error")}</div>
                  )}
                  <form onSubmit={userForm.handleSubmit(onUserSubmit)} className="flex flex-col gap-4">
                    <div className="field">
                      <label className="label">Full Name</label>
                      <input type="text" {...userForm.register("full_name", { required: "Required" })} className="input" />
                    </div>
                    <div className="field">
                      <label className="label">Email</label>
                      <input type="email" {...userForm.register("email", { required: "Required" })} className="input" />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="field">
                        <label className="label">Password (Temporary)</label>
                        <input type="password" {...userForm.register("password", { required: "Required" })} className="input" />
                      </div>
                      <div className="field">
                        <label className="label">Role</label>
                        <select {...userForm.register("role")} className="select-input">
                          <option value="member">Member</option>
                          <option value="instructor">Instructor</option>
                          <option value="admin">Admin</option>
                        </select>
                      </div>
                    </div>
                    <div className="flex justify-end gap-3 mt-2">
                      <button type="submit" disabled={createUser.isPending} className="btn-primary">
                        {createUser.isPending ? "Saving…" : "Create User"}
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="tbl-wrap">
                <table className="tbl">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedUsers.length === 0 ? (
                      <tr><td colSpan={4} className="text-center py-8 text-muted">No users found.</td></tr>
                    ) : (
                      sortedUsers.map(u => (
                        <tr key={u.id}>
                          <td className="font-bold">{u.full_name}</td>
                          <td className="text-secondary">{u.email}</td>
                          <td><StatusBadge status={u.role as any} /></td>
                          <td>
                            <span className={`badge ${u.is_active ? 'bg-ok/10 text-ok' : 'bg-danger/10 text-danger'}`}>
                              {u.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}
