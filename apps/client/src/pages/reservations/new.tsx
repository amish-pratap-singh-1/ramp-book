import { useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import LoadingSpinner from "@/components/LoadingSpinner";
import { useCreateReservation } from "@/hooks/useReservations";
import { useAircraft } from "@/hooks/useAircraft";
import { useInstructors } from "@/hooks/useInstructors";
import { isAuthenticated } from "@/lib/auth";
import type { ReservationCreate } from "@/api/reservations.api";

function toLocal(iso: string) {
  // Convert yyyy-MM-ddTHH:mm (local) to UTC ISO string
  return new Date(iso).toISOString();
}

export default function NewReservationPage() {
  const router = useRouter();
  const preselect = router.query.aircraft as string | undefined;

  const { data: aircraft = [], isLoading: acLoading } = useAircraft();
  const { data: instructors = [] } = useInstructors();
  const create = useCreateReservation();

  const { register, handleSubmit, formState: { errors } } = useForm<{
    aircraft_id: string;
    instructor_id: string;
    start_time: string;
    end_time: string;
    notes: string;
  }>({
    defaultValues: { aircraft_id: preselect ?? "" },
  });

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  if (acLoading) return <LoadingSpinner fullPage />;

  const apiError = (create.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail;

  const onSubmit = async (values: {
    aircraft_id: string;
    instructor_id: string;
    start_time: string;
    end_time: string;
    notes: string;
  }) => {
    const payload: ReservationCreate = {
      aircraft_id: parseInt(values.aircraft_id),
      instructor_id: values.instructor_id ? parseInt(values.instructor_id) : undefined,
      start_time: toLocal(values.start_time),
      end_time: toLocal(values.end_time),
      notes: values.notes || undefined,
    };
    await create.mutateAsync(payload);
    router.push("/reservations");
  };

  const available = aircraft.filter((a) => a.status === "available");

  return (
    <>
      <Head>
        <title>New Booking — RampBook</title>
      </Head>
      <Layout>
        <div className="page-header">
          <h1 className="page-title">New Booking</h1>
          <p className="page-sub">Reserve an aircraft for your next flight</p>
        </div>

        <div className="page-body">
          <div className="max-w-lg">
            <form onSubmit={handleSubmit(onSubmit)} id="new-reservation-form" className="flex flex-col gap-5">

              {/* Aircraft */}
              <div className="field">
                <label className="label" htmlFor="aircraft_id">Aircraft *</label>
                <select
                  id="aircraft_id"
                  {...register("aircraft_id", { required: "Select an aircraft" })}
                  className="select-input"
                >
                  <option value="">— Select aircraft —</option>
                  {available.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.tail_number} · {a.model} (${a.hourly_rate_usd}/hr)
                    </option>
                  ))}
                </select>
                {errors.aircraft_id && <p className="err">{errors.aircraft_id.message}</p>}
              </div>

              {/* Date/time range */}
              <div className="grid grid-cols-2 gap-4">
                <div className="field">
                  <label className="label" htmlFor="start_time">Departure *</label>
                  <input
                    id="start_time"
                    type="datetime-local"
                    {...register("start_time", { required: "Required" })}
                    className="input"
                  />
                  {errors.start_time && <p className="err">{errors.start_time.message}</p>}
                </div>
                <div className="field">
                  <label className="label" htmlFor="end_time">Return *</label>
                  <input
                    id="end_time"
                    type="datetime-local"
                    {...register("end_time", { required: "Required" })}
                    className="input"
                  />
                  {errors.end_time && <p className="err">{errors.end_time.message}</p>}
                </div>
              </div>

              {/* Instructor */}
              <div className="field">
                <label className="label" htmlFor="instructor_id">Instructor <span className="text-muted font-normal normal-case">(optional)</span></label>
                <select id="instructor_id" {...register("instructor_id")} className="select-input">
                  <option value="">— No instructor (solo) —</option>
                  {instructors.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.full_name} · {i.ratings ?? "CFI"}
                    </option>
                  ))}
                </select>
              </div>

              {/* Notes */}
              <div className="field">
                <label className="label" htmlFor="notes">Notes <span className="text-muted font-normal normal-case">(optional)</span></label>
                <textarea
                  id="notes"
                  {...register("notes")}
                  rows={3}
                  placeholder="e.g. IFR practice, cross-country to KDAL…"
                  className="input resize-none"
                />
              </div>

              {/* API error */}
              {create.isError && (
                <div className="bg-danger/10 border border-danger/20 rounded-xl px-4 py-3 text-sm text-danger">
                  {apiError ?? "Booking failed — check for conflicts"}
                </div>
              )}

              {/* Submit */}
              <div className="flex gap-3 pt-2">
                <button
                  type="submit"
                  id="submit-reservation"
                  disabled={create.isPending}
                  className="btn-primary"
                >
                  {create.isPending ? "Booking…" : "Confirm Booking →"}
                </button>
                <button type="button" onClick={() => router.back()} className="btn-ghost">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </Layout>
    </>
  );
}
