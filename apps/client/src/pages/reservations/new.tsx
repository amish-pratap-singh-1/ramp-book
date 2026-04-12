import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useForm } from "react-hook-form";
import { useQuery } from "@tanstack/react-query";
import { Calendar, dateFnsLocalizer, SlotInfo, View } from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { enUS } from "date-fns/locale";

import Layout from "@/components/Layout";
import LoadingSpinner from "@/components/LoadingSpinner";
import QueryBoundary from "@/components/QueryBoundary";
import { useCreateReservation } from "@/hooks/useReservations";
import { useAircraft } from "@/hooks/useAircraft";
import { useInstructors } from "@/hooks/useInstructors";
import { isAuthenticated } from "@/lib/auth";
import { aircraftApi } from "@/api/aircraft.api";
import type { components } from "@/api/schema";

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales: { "en-US": enUS },
});

export default function NewReservationPage() {
  const router = useRouter();
  const preselect = router.query.aircraft as string | undefined;

  const { data: aircraftData, isLoading: acLoading } = useAircraft();
  const aircraft = aircraftData?.aircraft ?? [];
  const { data: instructorsData } = useInstructors();
  const instructors = instructorsData?.users ?? [];
  const create = useCreateReservation();

  const [selectedAircraft, setSelectedAircraft] = useState<string>("");
  const [draftSlot, setDraftSlot] = useState<{ start: Date; end: Date } | null>(null);
  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [currentView, setCurrentView] = useState<View>("week");

  const { register, handleSubmit } = useForm<{
    instructor_id: string;
    notes: string;
  }>();

  // Set preselect once after hydration
  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
    if (preselect && !selectedAircraft && aircraft.length > 0) {
      setSelectedAircraft(preselect);
    }
  }, [router, preselect, aircraft, selectedAircraft]);

  const { data: schedule = [], isLoading: scheduleLoading } = useQuery({
    queryKey: ["aircraft_schedule", selectedAircraft],
    queryFn: () => aircraftApi.getSchedule(parseInt(selectedAircraft)),
    select: (data) => data.schedules,
    enabled: !!selectedAircraft,
  });

  // Removed manual acLoading check, handled by QueryBoundary below

  const onSubmit = (values: { instructor_id: string; notes: string }) => {
    if (!draftSlot || !selectedAircraft) return;
    const payload: components["schemas"]["ReservationCreateRequest"] = {
      reservation: {
        aircraft_id: parseInt(selectedAircraft),
        instructor_id: values.instructor_id ? parseInt(values.instructor_id) : undefined,
        start_time: draftSlot.start.toISOString(),
        end_time: draftSlot.end.toISOString(),
        notes: values.notes || undefined,
      }
    };
    create.mutate(payload, {
      onSuccess: () => {
        router.push("/reservations");
      }
    });
  };

  const available = aircraft.filter((a) => a.status === "available");

  const events = schedule.map((s) => ({
    id: `${s.type}-${s.id}`,
    title: s.type === "maintenance" ? "Maintenance" : "Reserved",
    start: new Date(s.start_time),
    end: new Date(s.end_time),
    isDraft: false,
    type: s.type,
  }));

  if (draftSlot) {
    events.push({
      id: "draft",
      title: "New Booking",
      start: draftSlot.start,
      end: draftSlot.end,
      isDraft: true,
    } as any);
  }

  const handleSelectSlot = (slotInfo: SlotInfo) => {
    const overlap = schedule.some((s) => {
      const sStart = new Date(s.start_time);
      const sEnd = new Date(s.end_time);
      return slotInfo.start < sEnd && slotInfo.end > sStart;
    });
    if (overlap) {
      alert("Selected time overlaps with an existing booking or maintenance window.");
      return;
    }
    setDraftSlot({ start: slotInfo.start, end: slotInfo.end });
  };

  const eventPropGetter = (event: any) => {
    if (event.isDraft) return { className: "rbc-slot-selection" };
    
    // Industry standard status colors natively handled through style properties
    if (event.type === "maintenance") {
      return { 
        className: "rbc-event",
        style: { backgroundColor: "#ef4444", borderColor: "#b91c1c", color: "#ffffff" } 
      };
    }
    if (event.type === "reservation") {
      return { 
        className: "rbc-event",
        style: { backgroundColor: "#38bdf8", borderColor: "#0284c7", color: "#ffffff" } 
      };
    }
    
    return { className: "rbc-event" };
  };

  return (
    <>
      <Head>
        <title>New Booking — RampBook</title>
      </Head>
      <Layout>
        <QueryBoundary 
          isLoading={acLoading} 
          data={aircraftData} 
          loadingComponent={<LoadingSpinner fullPage />}
        >
          <div className="page-header">
            <h1 className="page-title">New Booking</h1>
            <p className="page-sub">Select an aircraft and drag across the calendar to reserve</p>
          </div>

          <div className="page-body">
            <div className="flex flex-col xl:flex-row gap-8">
              <div className="flex-1 min-w-0 bg-surface border border-edge rounded-2xl p-5 flex flex-col gap-4 shadow-xl">
                <div className="field">
                  <label className="label">1. Select Aircraft</label>
                  <select
                    value={selectedAircraft}
                    onChange={(e) => {
                      setSelectedAircraft(e.target.value);
                      setDraftSlot(null);
                      setCurrentDate(new Date()); // Reset the calendar when aircraft changes
                      setCurrentView("week");
                    }}
                    className="select-input max-w-sm"
                  >
                    <option value="">— Choose an aircraft —</option>
                    {available.map((a) => (
                      <option key={a.id} value={String(a.id)}>
                        {a.tail_number} · {a.model} (${a.hourly_rate_usd}/hr)
                      </option>
                    ))}
                  </select>
                </div>

                {selectedAircraft ? (
                  <div className="h-[750px] mt-4 relative">
                    {scheduleLoading && (
                      <div className="absolute inset-0 bg-surface/50 z-10 flex items-center justify-center">
                        <LoadingSpinner />
                      </div>
                    )}
                    <Calendar
                      localizer={localizer}
                      events={events}
                      startAccessor="start"
                      endAccessor="end"
                      date={currentDate}
                      onNavigate={(date) => setCurrentDate(date)}
                      view={currentView}
                      onView={(view) => setCurrentView(view)}
                      views={["week", "day"]}
                      selectable
                      onSelectSlot={handleSelectSlot}
                      eventPropGetter={eventPropGetter}
                      step={30}
                      timeslots={2}
                      min={new Date(0, 0, 0, 6, 0, 0)} // Starts at 6 AM
                      max={new Date(0, 0, 0, 22, 0, 0)} // Ends at 10 PM
                    />
                  </div>
                ) : (
                  <div className="h-[400px] border border-edge border-dashed rounded-xl flex items-center justify-center text-muted mt-4">
                    Select an aircraft to view availability
                  </div>
                )}
              </div>

              <div className="w-full xl:w-96 flex-shrink-0">
                <div className="card sticky top-24 shadow-2xl border-accent/20">
                  <h2 className="section-title mb-6">2. Confirm Details</h2>

                  {!draftSlot ? (
                    <div className="text-secondary text-sm flex items-start gap-4 p-4 bg-base rounded-xl border border-edge">
                      <div className="w-10 h-10 rounded-full bg-surface border border-edge flex items-center justify-center text-xl flex-shrink-0 mt-1">
                        👆
                      </div>
                      <div>
                        <div className="font-bold text-primary mb-1">Pick a time slot</div>
                        Drag your cursor across empty spaces on the calendar grid to block off your preferred departure and return times.
                      </div>
                    </div>
                  ) : (
                    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5">
                      <div className="bg-base p-4 rounded-xl border border-edge">
                        <div className="text-[10px] font-bold text-muted uppercase tracking-widest mb-2">Selected Window</div>
                        <div className="text-primary font-bold text-lg mb-1">{format(draftSlot.start, "MMM do, yyyy")}</div>
                        <div className="text-secondary text-sm">
                          {format(draftSlot.start, "h:mm a")} <span className="mx-2 text-muted">→</span> {format(draftSlot.end, "h:mm a")}
                        </div>
                      </div>

                      <div className="field">
                        <label className="label">Flight Instructor <span className="text-muted font-normal normal-case">(optional)</span></label>
                        <select {...register("instructor_id")} className="select-input">
                          <option value="">— No instructor (solo) —</option>
                          {instructors.map((i) => (
                            <option key={i.id} value={String(i.id)}>
                              {i.full_name} · {i.ratings ?? "CFI"}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="field">
                        <label className="label">Flight Notes <span className="text-muted font-normal normal-case">(optional)</span></label>
                        <textarea
                          {...register("notes")}
                          className="input resize-none"
                          rows={3}
                          placeholder="e.g. IFR practice, cross-country to KDAL…"
                        />
                      </div>


                      <div className="mt-2 pt-4 border-t border-edge flex flex-col gap-3">
                        <button type="submit" disabled={create.isPending} className="btn-primary w-full justify-center">
                          {create.isPending ? "Validating & Booking…" : "Confirm Booking →"}
                        </button>
                        <button type="button" onClick={() => setDraftSlot(null)} className="btn-ghost w-full justify-center text-secondary">
                          Discard & Reselect Time
                        </button>
                      </div>
                    </form>
                  )}
                </div>
              </div>
            </div>
          </div>
        </QueryBoundary>
      </Layout>

    </>
  );
}
