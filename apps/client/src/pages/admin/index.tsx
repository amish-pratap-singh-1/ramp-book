import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import StatusBadge from "@/components/StatusBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import QueryBoundary from "@/components/QueryBoundary";
import ConfirmModal from "@/components/ConfirmModal";
import { adminApi } from "@/api/admin.api";
import { useAircraft } from "@/hooks/useAircraft";
import { isAuthenticated, getUserRole } from "@/lib/auth";
import AircraftCalendar, { CalendarEvent, CalendarResource } from "@/components/AircraftCalendar";
import AircraftMaintenanceCard from "@/components/AircraftMaintenanceCard";
import { View } from "react-big-calendar";
import type { components } from "@/api/schema";
import { formatDateForInput, formatDateForAPI, formatDisplay } from "@/lib/date-utils";

export default function AdminPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [tab, setTab] = useState<"reservations" | "maintenance" | "users">("reservations");
  const [showMaintForm, setShowMaintForm] = useState(false);
  const [showUserForm, setShowUserForm] = useState(false);
  const [maintToDelete, setMaintToDelete] = useState<number | null>(null);
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [currentView, setCurrentView] = useState<View>("day");
  const [selectedAircraftMaint, setSelectedAircraftMaint] = useState<string>("");
  const [draftMaintSlot, setDraftMaintSlot] = useState<{ start: Date; end: Date } | null>(null);
  const [selectedMaintEventId, setSelectedMaintEventId] = useState<number | null>(null);

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
    queryKey: ["admin_maintenance", selectedAircraftMaint],
    queryFn: () => adminApi.listMaintenance(selectedAircraftMaint ? parseInt(selectedAircraftMaint) : undefined),
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

  // Handle default maintenance aircraft selection
  useEffect(() => {
    if (tab === "maintenance" && !selectedAircraftMaint && aircraft.length > 0) {
      setSelectedAircraftMaint(aircraft[0].id.toString());
    }
  }, [tab, aircraft, selectedAircraftMaint]);

  const createMaint = useMutation({
    mutationFn: (data: components["schemas"]["MaintenanceWindowCreateRequest"]) => adminApi.addMaintenance(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin_maintenance"] });
      qc.invalidateQueries({ queryKey: ["admin_all_reservations"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
      setDraftMaintSlot(null);
      reset();
    },
  });

  const deleteMaint = useMutation({
    mutationFn: (id: number) => adminApi.deleteMaintenance(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin_maintenance"] });
      qc.invalidateQueries({ queryKey: ["aircraft"] });
      setMaintToDelete(null);
      setSelectedMaintEventId(null);
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

  // Combined loading state handled by QueryBoundary below
  const adminLoading = resLoading || maintLoading || usersLoading;
  const adminData = reservationsData && maintenanceData && usersData;

  const { data: allResData } = useQuery({
    queryKey: ["admin_all_reservations"],
    queryFn: () => adminApi.allReservations(),
    enabled: tab === "maintenance",
  });
  const allReservations = (allResData?.reservations ?? []).filter(r => 
    (!selectedAircraftMaint || r.aircraft_id === parseInt(selectedAircraftMaint)) && r.status === "confirmed"
  );

  const calendarEvents: CalendarEvent[] = [
    ...allReservations.map(r => ({
      id: `res-${r.id}`,
      title: `${r.member?.full_name ?? "Member"}`,
      start: new Date(r.start_time),
      end: new Date(r.end_time),
      type: "reservation" as const,
      resourceId: r.aircraft_id,
    })),
    ...maintenance.map(m => ({
      id: `maint-${m.id}`,
      title: m.reason || "Maintenance",
      start: new Date(m.start_time),
      end: new Date(m.end_time),
      type: "maintenance" as const,
      resourceId: m.aircraft_id,
    })),
  ];

  if (draftMaintSlot) {
    calendarEvents.push({
      id: "draft-maint",
      title: "New Window",
      start: draftMaintSlot.start,
      end: draftMaintSlot.end,
      isDraft: true,
      type: "maintenance"
    });
  }

  const calendarResources: CalendarResource[] = aircraft
    .filter(a => !selectedAircraftMaint || a.id === parseInt(selectedAircraftMaint))
    .map(a => ({
      id: a.id,
      title: a.tail_number,
    }));

  const handleSelectSlot = (slotInfo: any) => {
    setDraftMaintSlot({ start: slotInfo.start, end: slotInfo.end });
    setSelectedMaintEventId(null);
    reset({
      aircraft_id: selectedAircraftMaint || slotInfo.resourceId?.toString() || "",
      start_time: formatDateForInput(slotInfo.start),
      end_time: formatDateForInput(slotInfo.end),
      reason: "",
    });
  };

  const handleSelectEvent = (event: CalendarEvent) => {
    if (event.type === "maintenance" && typeof event.id === "string" && event.id.startsWith("maint-")) {
      const id = parseInt(event.id.replace("maint-", ""));
      const m = maintenance.find(item => item.id === id);
      if (m) {
        setSelectedMaintEventId(id);
        setDraftMaintSlot(null);
        reset({
          aircraft_id: m.aircraft_id.toString(),
          start_time: formatDateForInput(m.start_time),
          end_time: formatDateForInput(m.end_time),
          reason: m.reason || "",
        });
      }
    }
  };

  const onSubmit = (data: { aircraft_id: string; start_time: string; end_time: string; reason: string }) => {
    createMaint.mutate({
      maintenance_window: {
        aircraft_id: parseInt(data.aircraft_id),
        start_time: formatDateForAPI(data.start_time)!,
        end_time: formatDateForAPI(data.end_time)!,
        reason: data.reason || undefined,
      }
    });
  };

  const selectedMaintenance = selectedMaintEventId ? maintenance.find(m => m.id === selectedMaintEventId) : null;

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
        <QueryBoundary 
          isLoading={adminLoading} 
          data={adminData} 
          loadingComponent={<LoadingSpinner fullPage />}
        >
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
                          <td>{formatDisplay(r.start_time, "MMM d, h:mm a")}</td>
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
                <div className="flex flex-col xl:flex-row gap-8">
                  {/* Left Column: Selector & Details */}
                  <div className="w-full xl:w-96 flex-shrink-0 order-2 xl:order-1">
                    <div className="card sticky top-24 shadow-2xl border-edge-strong bg-surface/50 backdrop-blur-md">
                      <div className="field mb-6">
                        <label className="label">1. Select Aircraft</label>
                        <select
                          value={selectedAircraftMaint}
                          onChange={(e) => {
                            setSelectedAircraftMaint(e.target.value);
                            setDraftMaintSlot(null);
                            setSelectedMaintEventId(null);
                          }}
                          className="select-input !bg-base/50"
                        >
                          {aircraft.map(a => <option key={a.id} value={a.id.toString()}>{a.tail_number} · {a.model}</option>)}
                        </select>
                      </div>

                      {selectedAircraftMaint ? (
                        <div className="space-y-6">
                          <div className="h-px bg-edge-strong"></div>
                          
                          {!draftMaintSlot && !selectedMaintEventId ? (
                            <div className="bg-base/40 p-5 rounded-2xl border border-edge border-dashed text-center">
                              <div className="text-2xl mb-2">☝️</div>
                              <div className="text-sm font-bold text-primary mb-1">Manage Schedule</div>
                              <p className="text-xs text-secondary leading-relaxed">
                                Select a red window to manage existing maintenance, or drag across empty space to schedule a new one.
                              </p>
                            </div>
                          ) : (
                            <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                              <h3 className="text-sm font-bold text-primary flex items-center gap-2">
                                <span className="text-accent">{selectedMaintEventId ? "✏️" : "➕"}</span>
                                {selectedMaintEventId ? "Maintenance Details" : "New Maintenance Window"}
                              </h3>

                              <div className="grid grid-cols-1 gap-4">
                                <div className="field">
                                  <label className="label">Start</label>
                                  <input 
                                    type="datetime-local" 
                                    {...register("start_time", { required: true })} 
                                    className="input !bg-base/30 !py-2" 
                                  />
                                </div>
                                <div className="field">
                                  <label className="label">End</label>
                                  <input 
                                    type="datetime-local" 
                                    {...register("end_time", { required: true })} 
                                    className="input !bg-base/30 !py-2" 
                                  />
                                </div>
                                <div className="field">
                                  <label className="label">Reason / Work Order</label>
                                  <input 
                                    type="text" 
                                    {...register("reason")} 
                                    placeholder="e.g. 100-hour inspection" 
                                    className="input !bg-base/30 !py-2" 
                                  />
                                </div>
                              </div>

                              <div className="flex flex-col gap-3 pt-4 border-t border-edge-strong">
                                {!selectedMaintEventId ? (
                                  <button type="submit" disabled={createMaint.isPending} className="btn-primary w-full justify-center">
                                    {createMaint.isPending ? "Configuring..." : "Commit Maintenance →"}
                                  </button>
                                ) : (
                                  <button 
                                    type="button" 
                                    onClick={() => setMaintToDelete(selectedMaintEventId)}
                                    className="btn-danger w-full justify-center"
                                  >
                                    Remove Maintenance Window
                                  </button>
                                )}
                                <button 
                                  type="button" 
                                  onClick={() => {
                                    setDraftMaintSlot(null);
                                    setSelectedMaintEventId(null);
                                    reset({ aircraft_id: selectedAircraftMaint, start_time: "", end_time: "", reason: "" });
                                  }} 
                                  className="btn-ghost w-full justify-center text-xs"
                                >
                                  Clear Selection
                                </button>
                              </div>
                            </form>
                          )}
                        </div>
                      ) : (
                        <div className="p-4 bg-accent/5 border border-accent/10 rounded-2xl text-xs text-secondary leading-relaxed">
                          Select an aircraft to enable interactive scheduling and window management.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right Column: Calendar */}
                  <div className="flex-1 min-w-0 order-1 xl:order-2">
                    <div className="bg-surface/30 backdrop-blur-md border border-edge-strong rounded-3xl p-5 shadow-xl">
                      <div className="mb-4 flex items-center justify-between">
                        <div>
                          <h2 className="text-lg font-bold text-primary">
                            {selectedAircraftMaint ? aircraft.find(a => a.id === parseInt(selectedAircraftMaint))?.tail_number : "Fleet Schedule"}
                          </h2>
                          <p className="text-xs text-secondary">
                            {selectedAircraftMaint ? "Interactive maintenance & flight timeline" : "Global availability overview"}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-accent/10 border border-accent/20">
                            <div className="w-2 h-2 rounded-full bg-accent"></div>
                            <span className="text-[10px] font-bold text-accent uppercase tracking-tighter">Reservations</span>
                          </div>
                          <div className="flex items-center gap-1.5 px-2 py-1 rounded-lg bg-danger/10 border border-danger/20">
                            <div className="w-2 h-2 rounded-full bg-danger"></div>
                            <span className="text-[10px] font-bold text-danger uppercase tracking-tighter">Maintenance</span>
                          </div>
                        </div>
                      </div>

                      <AircraftCalendar
                        events={calendarEvents}
                        resources={selectedAircraftMaint ? undefined : calendarResources}
                        date={currentDate}
                        onDateChange={setCurrentDate}
                        view={currentView}
                        onViewChange={setCurrentView}
                        onSelectSlot={handleSelectSlot}
                        onSelectEvent={handleSelectEvent}
                        isLoading={maintLoading}
                        height={selectedAircraftMaint ? 800 : 600}
                      />
                    </div>
                  </div>
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
        </QueryBoundary>
      </Layout>

      <ConfirmModal
        isOpen={!!maintToDelete}
        onClose={() => setMaintToDelete(null)}
        onConfirm={() => maintToDelete && deleteMaint.mutate(maintToDelete)}
        title="Remove Maintenance"
        message="Are you sure you want to remove this maintenance window? This will make the aircraft available for bookings again."
        confirmLabel="Remove Window"
        isLoading={deleteMaint.isPending}
      />
    </>
  );
}
