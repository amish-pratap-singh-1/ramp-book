import { useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Link from "next/link";
import Layout from "@/components/Layout";
import StatusBadge from "@/components/StatusBadge";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useAircraft } from "@/hooks/useAircraft";
import { isAuthenticated } from "@/lib/auth";
import type { Aircraft } from "@/api/aircraft.api";

export default function FleetPage() {
  const router = useRouter();
  const { data: aircraft = [], isLoading } = useAircraft();

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  if (isLoading) return <LoadingSpinner fullPage />;

  return (
    <>
      <Head>
        <title>Fleet — RampBook</title>
        <meta name="description" content="Browse available aircraft at Cedar Valley Flying Club" />
      </Head>
      <Layout>
        <div className="page-header">
          <h1 className="page-title">Aircraft Fleet</h1>
          <p className="page-sub">{aircraft.length} aircraft registered · Cedar Valley Flying Club</p>
        </div>

        <div className="page-body">
          {aircraft.length === 0 ? (
            <div className="empty">
              <div className="empty-icon">✈</div>
              <div className="empty-title">No aircraft in the fleet</div>
              <p>Contact your club admin to add aircraft.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
              {aircraft.map((ac: Aircraft) => (
                <AircraftCard key={ac.id} ac={ac} />
              ))}
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}

function AircraftCard({ ac }: { ac: Aircraft }) {
  const router = useRouter();
  const available = ac.status === "available";

  return (
    <div className="bg-card border border-edge rounded-2xl p-6 flex flex-col gap-5 transition-all duration-200 hover:-translate-y-1 hover:border-accent/20 hover:shadow-2xl">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="text-2xl font-extrabold text-accent tracking-widest font-mono">{ac.tail_number}</div>
          <div className="text-sm font-medium text-primary mt-0.5">{ac.model}</div>
        </div>
        <StatusBadge status={ac.status} />
      </div>

      {/* Meta */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Year",          value: ac.year },
          { label: "Hobbs Hours",   value: `${ac.total_hobbs_hours.toFixed(1)} hrs` },
          { label: "Hourly Rate",   value: `$${ac.hourly_rate_usd}/hr` },
          { label: "Notes",         value: ac.notes ?? "—" },
        ].map(({ label, value }) => (
          <div key={label}>
            <div className="text-[10px] font-bold text-muted uppercase tracking-widest">{label}</div>
            <div className="text-sm text-primary mt-0.5 truncate">{value}</div>
          </div>
        ))}
      </div>

      {/* Action */}
      <div className="pt-4 border-t border-edge mt-auto">
        <button
          disabled={!available}
          onClick={() => router.push(`/reservations/new?aircraft=${ac.id}`)}
          className={available ? "btn-primary w-full justify-center" : "btn-ghost w-full justify-center opacity-50 cursor-not-allowed"}
          id={`book-ac-${ac.id}`}
        >
          {available ? "Book This Aircraft →" : `Unavailable (${ac.status})`}
        </button>
      </div>
    </div>
  );
}
