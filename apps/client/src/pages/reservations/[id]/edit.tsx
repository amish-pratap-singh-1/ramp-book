import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import LoadingSpinner from "@/components/LoadingSpinner";
import QueryBoundary from "@/components/QueryBoundary";
import { useReservations, useUpdateReservation } from "@/hooks/useReservations";
import { useInstructors } from "@/hooks/useInstructors";
import { isAuthenticated } from "@/lib/auth";
import { aircraftApi } from "@/api/aircraft.api";
import AircraftCalendar, { CalendarEvent } from "@/components/AircraftCalendar";
import type { components } from "@/api/schema";
import { useQuery } from "@tanstack/react-query";
import { View, SlotInfo } from "react-big-calendar";
import { formatDateForInput, formatDateForAPI } from "@/lib/date-utils";

export default function EditReservationPage() {
  const router = useRouter();
  const { id } = router.query;
  const { data: reservationsData, isLoading } = useReservations();
  const reservations = reservationsData?.reservations ?? [];
  const { data: instructorsData } = useInstructors();
  const instructors = instructorsData?.users ?? [];
  const update = useUpdateReservation();

  const reservation = reservations.find((r) => r.id === parseInt(id as string));

  const { register, handleSubmit, reset, formState: { errors }, watch, setValue } = useForm<{
    instructor_id: string;
    start_time: string;
    end_time: string;
    notes: string;
  }>();

  const [currentDate, setCurrentDate] = useState<Date>(new Date());
  const [currentView, setCurrentView] = useState<View>("week");

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  useEffect(() => {
    if (reservation) {
      reset({
        instructor_id: reservation.instructor_id?.toString() ?? "",
        start_time: formatDateForInput(reservation.start_time),
        end_time: formatDateForInput(reservation.end_time),
        notes: reservation.notes ?? "",
      });
      setCurrentDate(new Date(reservation.start_time));
    }
  }, [reservation, reset]);

  const { data: scheduleData, isLoading: scheduleLoading } = useQuery({
    queryKey: ["aircraft_schedule", reservation?.aircraft_id],
    queryFn: () => aircraftApi.getSchedule(reservation!.aircraft_id),
    enabled: !!reservation,
  });
  const schedule = scheduleData?.schedules ?? [];

  const events: CalendarEvent[] = schedule
    .filter(s => s.type !== "reservation" || s.id !== reservation?.id)
    .map(s => ({
      id: `${s.type}-${s.id}`,
      title: s.type === "maintenance" ? "Maintenance" : "Reserved",
      start: new Date(s.start_time),
      end: new Date(s.end_time),
      type: s.type as any,
    }));

  // Add the current reservation as a 'draft' or distinct event
  const startTime = watch("start_time");
  const endTime = watch("end_time");

  if (startTime && endTime) {
    events.push({
      id: "current",
      title: "Active Selection",
      start: new Date(startTime),
      end: new Date(endTime),
      isDraft: true,
    });
  }

  const handleSelectSlot = (slotInfo: SlotInfo) => {
    setValue("start_time", formatDateForInput(slotInfo.start));
    setValue("end_time", formatDateForInput(slotInfo.end));
  };

  // Removed manual isLoading check, handled by QueryBoundary below

  const onSubmit = (values: { instructor_id: string; start_time: string; end_time: string; notes: string }) => {
    const payload: components["schemas"]["ReservationUpdateRequest"] = {
      reservation: {
        instructor_id: values.instructor_id ? parseInt(values.instructor_id) : undefined,
        start_time: formatDateForAPI(values.start_time)!,
        end_time: formatDateForAPI(values.end_time)!,
        notes: values.notes || undefined,
      }
    };
    if (!reservation) return;
    update.mutate({ id: reservation.id, data: payload }, {
      onSuccess: () => {
        router.push("/reservations");
      }
    });
  };

  return (
    <>
      <Head>
        <title>Edit Booking — RampBook</title>
      </Head>
      <Layout>
        <QueryBoundary 
          isLoading={isLoading} 
          data={reservation} 
          loadingComponent={<LoadingSpinner fullPage />}
        >
          <div className="page-header">
            <h1 className="page-title">Edit Booking</h1>
            <p className="page-sub">
              {reservation?.aircraft?.tail_number} · {reservation?.aircraft?.model}
            </p>
          </div>

          <div className="page-body">
            <div className="flex flex-col xl:flex-row gap-8">
              <div className="flex-1 bg-surface border border-edge rounded-2xl p-5 shadow-xl">
                <div className="mb-4">
                  <h2 className="text-lg font-bold">Reschedule on Calendar</h2>
                  <p className="text-sm text-secondary">Drag to select a new time slot for this aircraft</p>
                </div>
                <AircraftCalendar
                  events={events}
                  date={currentDate}
                  onDateChange={setCurrentDate}
                  view={currentView}
                  onViewChange={setCurrentView}
                  onSelectSlot={handleSelectSlot}
                  isLoading={scheduleLoading}
                />
              </div>

              <div className="w-full xl:w-96 flex-shrink-0">
                <div className="card sticky top-24 shadow-2xl border-accent/20">
                  <h2 className="section-title mb-6">Booking Details</h2>
                  <form onSubmit={handleSubmit(onSubmit)} id="edit-reservation-form" className="flex flex-col gap-5">

                    <div className="grid grid-cols-2 gap-4">
                      <div className="field">
                        <label className="label" htmlFor="edit-start">Departure *</label>
                        <input
                          id="edit-start"
                          type="datetime-local"
                          {...register("start_time", { required: "Required" })}
                          className="input"
                        />
                        {errors.start_time && <p className="err">{errors.start_time.message}</p>}
                      </div>
                      <div className="field">
                        <label className="label" htmlFor="edit-end">Return *</label>
                        <input
                          id="edit-end"
                          type="datetime-local"
                          {...register("end_time", { required: "Required" })}
                          className="input"
                        />
                        {errors.end_time && <p className="err">{errors.end_time.message}</p>}
                      </div>
                    </div>

                    <div className="field">
                      <label className="label" htmlFor="edit-instructor">Instructor <span className="text-muted font-normal normal-case">(optional)</span></label>
                      <select id="edit-instructor" {...register("instructor_id")} className="select-input">
                        <option value="">— No instructor (solo) —</option>
                        {instructors.map((i) => (
                          <option key={i.id} value={i.id}>
                            {i.full_name} · {i.ratings ?? "CFI"}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="field">
                      <label className="label" htmlFor="edit-notes">Notes</label>
                      <textarea id="edit-notes" {...register("notes")} rows={3} className="input resize-none" />
                    </div>


                    <div className="flex flex-col gap-3 pt-4 border-t border-edge">
                      <button type="submit" disabled={update.isPending} className="btn-primary w-full justify-center" id="save-edit">
                        {update.isPending ? "Saving…" : "Save Changes"}
                      </button>
                      <button type="button" onClick={() => router.back()} className="btn-ghost w-full justify-center">Cancel</button>
                    </div>
                  </form>
                </div>
              </div>
            </div>

          </div>
        </QueryBoundary>
      </Layout>

    </>
  );
}
