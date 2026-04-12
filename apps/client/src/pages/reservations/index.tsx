import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Link from "next/link";
import Layout from "@/components/Layout";
import StatusBadge from "@/components/StatusBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useReservations, useCancelReservation, useCompleteReservation } from "@/hooks/useReservations";
import { isAuthenticated } from "@/lib/auth";
import type { components } from "@/api/schema";

type Reservation = components["schemas"]["ReservationResponse"];

function fmt(iso: string) {
  return new Date(iso).toLocaleString("en-US", {
    weekday: "short", month: "short", day: "numeric",
    hour: "numeric", minute: "2-digit",
  });
}
function hrs(r: Reservation) {
  return ((new Date(r.end_time).getTime() - new Date(r.start_time).getTime()) / 3_600_000).toFixed(1);
}

export default function ReservationsPage() {
  const router = useRouter();
  const { data: reservationsData, isLoading } = useReservations();
  const reservations = reservationsData?.reservations ?? [];
  const cancel = useCancelReservation();
  const complete = useCompleteReservation();

  const [tab, setTab] = useState<"upcoming" | "past">("upcoming");
  const [logFlight, setLogFlight] = useState<Reservation | null>(null);
  const [hobbs, setHobbs] = useState({ hobbs_start: "", hobbs_end: "" });
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  if (isLoading) return <LoadingSpinner fullPage />;

  const now = new Date();
  const upcoming = reservations.filter(
    (r) => r.status === "confirmed" && new Date(r.end_time) > now,
  ).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  const past = reservations.filter(
    (r) => r.status !== "confirmed" || new Date(r.end_time) <= now,
  ).sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());

  const shown = tab === "upcoming" ? upcoming : past;

  const handleCancel = async (id: number) => {
    if (!confirm("Cancel this reservation?")) return;
    await cancel.mutateAsync(id);
  };

  const handleComplete = async () => {
    if (!logFlight) return;
    setError("");
    const s = parseFloat(hobbs.hobbs_start);
    const e = parseFloat(hobbs.hobbs_end);
    if (isNaN(s) || isNaN(e) || e <= s) {
      setError("Hobbs end must be greater than hobbs start");
      return;
    }
    await complete.mutateAsync({ 
      id: logFlight.id, 
      data: { 
        flight_data: { hobbs_start: s, hobbs_end: e } 
      } 
    });
    setLogFlight(null);
    setHobbs({ hobbs_start: "", hobbs_end: "" });
  };

  return (
    <>
      <Head>
        <title>My Bookings — RampBook</title>
      </Head>
      <Layout>
        <div className="page-header">
          <h1 className="page-title">My Bookings</h1>
          <p className="page-sub">Manage your flight reservations</p>
        </div>

        <div className="page-body space-y-6">
          {/* Actions + tabs */}
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="tabs">
              <button className={tab === "upcoming" ? "tab-active" : "tab"} onClick={() => setTab("upcoming")}>
                Upcoming ({upcoming.length})
              </button>
              <button className={tab === "past" ? "tab-active" : "tab"} onClick={() => setTab("past")}>
                Past ({past.length})
              </button>
            </div>
            <Link href="/reservations/new" className="btn-primary">✈ New Booking</Link>
          </div>

          {shown.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">📅</div>
              <div className="empty-title">{tab === "upcoming" ? "No upcoming reservations" : "No past reservations"}</div>
              {tab === "upcoming" && (
                <p className="text-sm"><Link href="/reservations/new" className="text-accent hover:underline">Book a flight</Link> to get started</p>
              )}
            </div>
          ) : (
            <div className="tbl-wrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th>Aircraft</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Hrs</th>
                    <th>Instructor</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {shown.map((r) => (
                    <tr key={r.id}>
                      <td>
                        <span className="font-bold text-accent font-mono">{r.aircraft?.tail_number}</span>
                        <span className="block text-xs text-secondary">{r.aircraft?.model}</span>
                      </td>
                      <td className="whitespace-nowrap text-secondary">{fmt(r.start_time)}</td>
                      <td className="whitespace-nowrap text-secondary">{fmt(r.end_time)}</td>
                      <td className="text-secondary">{hrs(r)}</td>
                      <td className="text-secondary">{r.instructor?.full_name ?? <span className="text-muted italic">Solo</span>}</td>
                      <td><StatusBadge status={r.status} /></td>
                      <td>
                        <div className="flex items-center gap-2">
                          {r.status === "confirmed" && new Date(r.end_time) > now && (
                            <>
                              <Link href={`/reservations/${r.id}/edit`} className="btn-ghost btn-sm">Edit</Link>
                              <button
                                onClick={() => handleCancel(r.id)}
                                disabled={cancel.isPending}
                                className="btn-danger btn-sm"
                                id={`cancel-res-${r.id}`}
                              >
                                Cancel
                              </button>
                            </>
                          )}
                          {r.status === "confirmed" && new Date(r.end_time) <= now && (
                            <button
                              onClick={() => { setLogFlight(r); setHobbs({ hobbs_start: "", hobbs_end: "" }); setError(""); }}
                              className="btn-primary btn-sm"
                              id={`log-flight-${r.id}`}
                            >
                              Log Flight
                            </button>
                          )}
                          {r.status === "completed" && r.hobbs_end && (
                            <span className="text-xs text-secondary font-mono">{r.hobbs_start?.toFixed(1)} → {r.hobbs_end?.toFixed(1)}</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </Layout>

      {/* Log Flight Modal */}
      {logFlight && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-6">
          <div className="bg-surface border border-edge-strong rounded-2xl p-8 w-full max-w-md shadow-2xl animate-[fadeIn_0.2s_ease]">
            <h2 className="text-lg font-bold text-primary mb-1">Log Flight</h2>
            <p className="text-sm text-secondary mb-6">
              {logFlight.aircraft?.tail_number} · {logFlight.aircraft?.model}
            </p>

            <div className="flex flex-col gap-4">
              <div className="field">
                <label className="label" htmlFor="hobbs-start">Hobbs Start</label>
                <input id="hobbs-start" type="number" step="0.1" className="input" placeholder="e.g. 4821.3"
                  value={hobbs.hobbs_start} onChange={(e) => setHobbs((p) => ({ ...p, hobbs_start: e.target.value }))} />
              </div>
              <div className="field">
                <label className="label" htmlFor="hobbs-end">Hobbs End</label>
                <input id="hobbs-end" type="number" step="0.1" className="input" placeholder="e.g. 4823.8"
                  value={hobbs.hobbs_end} onChange={(e) => setHobbs((p) => ({ ...p, hobbs_end: e.target.value }))} />
              </div>
              {error && <p className="err">{error}</p>}
            </div>

            <div className="flex gap-3 justify-end mt-6">
              <button onClick={() => setLogFlight(null)} className="btn-ghost">Cancel</button>
              <button onClick={handleComplete} disabled={complete.isPending} className="btn-primary" id="submit-flight-log">
                {complete.isPending ? "Saving…" : "Save Flight"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
