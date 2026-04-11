import { useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Link from "next/link";
import Layout from "@/components/Layout";
import StatusBadge from "@/components/StatusBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useMe } from "@/hooks/useMe";
import { useReservations } from "@/hooks/useReservations";
import { useAircraft } from "@/hooks/useAircraft";
import { isAuthenticated } from "@/lib/auth";

function fmt(iso: string) {
  return new Date(iso).toLocaleString("en-US", {
    month: "short", day: "numeric", hour: "numeric", minute: "2-digit",
  });
}

export default function DashboardPage() {
  const router = useRouter();
  const { data: me, isLoading: meLoading } = useMe();
  const { data: reservations = [] } = useReservations();
  const { data: aircraft = [] } = useAircraft();

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  if (meLoading) return <LoadingSpinner fullPage />;

  const upcoming = reservations
    .filter((r) => r.status === "confirmed" && new Date(r.start_time) > new Date())
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  const availableCount = aircraft.filter((a) => a.status === "available").length;
  const confirmedCount = reservations.filter((r) => r.status === "confirmed").length;
  const completedCount = reservations.filter((r) => r.status === "completed").length;

  return (
    <>
      <Head>
        <title>Dashboard — RampBook</title>
      </Head>
      <Layout>
        <div className="page-header">
          <h1 className="page-title">
            Good day, {me?.full_name?.split(" ")[0] ?? "Pilot"} 👋
          </h1>
          <p className="page-sub">Here&apos;s what&apos;s happening at Cedar Valley Flying Club</p>
        </div>

        <div className="page-body space-y-8">
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Aircraft Available", value: availableCount, sub: `of ${aircraft.length} total` },
              { label: "Active Bookings",    value: confirmedCount, sub: "confirmed" },
              { label: "Flights Completed",  value: completedCount, sub: "this club" },
              { label: "Next Departure",     value: upcoming[0] ? upcoming[0].aircraft?.tail_number ?? "–" : "None", sub: upcoming[0] ? fmt(upcoming[0].start_time) : "No upcoming flights" },
            ].map((s) => (
              <div key={s.label} className="stat-card">
                <div className="stat-label">{s.label}</div>
                <div className="stat-value">{s.value}</div>
                <div className="stat-sub">{s.sub}</div>
              </div>
            ))}
          </div>

          {/* Quick actions */}
          <div className="flex gap-3 flex-wrap">
            <Link href="/reservations/new" className="btn-primary">✈ Book a Flight</Link>
            <Link href="/fleet"            className="btn-ghost">View Fleet</Link>
            <Link href="/reservations"     className="btn-ghost">My Bookings</Link>
          </div>

          {/* Upcoming reservations */}
          <div>
            <div className="section-row">
              <h2 className="section-title">Upcoming Reservations</h2>
              <Link href="/reservations" className="text-xs text-accent hover:underline">See all →</Link>
            </div>

            {upcoming.length === 0 ? (
              <div className="empty">
                <div className="empty-icon">📅</div>
                <div className="empty-title">No upcoming reservations</div>
                <p className="text-sm">
                  <Link href="/reservations/new" className="text-accent hover:underline">Book a flight</Link> to get started
                </p>
              </div>
            ) : (
              <div className="tbl-wrap">
                <table className="tbl">
                  <thead>
                    <tr>
                      <th>Aircraft</th>
                      <th>Departure</th>
                      <th>Duration</th>
                      <th>Instructor</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {upcoming.map((r) => {
                      const hrs = ((new Date(r.end_time).getTime() - new Date(r.start_time).getTime()) / 3_600_000).toFixed(1);
                      return (
                        <tr key={r.id}>
                          <td>
                            <span className="font-bold text-accent font-mono">{r.aircraft?.tail_number}</span>
                            <span className="block text-xs text-secondary">{r.aircraft?.model}</span>
                          </td>
                          <td>{fmt(r.start_time)}</td>
                          <td className="text-secondary">{hrs} hrs</td>
                          <td className="text-secondary">{r.instructor?.full_name ?? <span className="text-muted italic">Solo</span>}</td>
                          <td><StatusBadge status={r.status} /></td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </Layout>
    </>
  );
}
