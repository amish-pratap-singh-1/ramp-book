import { useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import { useForm } from "react-hook-form";
import Layout from "@/components/Layout";
import LoadingSpinner from "@/components/LoadingSpinner";
import QueryBoundary from "@/components/QueryBoundary";
import { useUpdateReservation } from "@/hooks/useReservations";
import { useInstructors } from "@/hooks/useInstructors";
import { useReservations } from "@/hooks/useReservations";
import { isAuthenticated } from "@/lib/auth";
import type { components } from "@/api/schema";

function toInputVal(iso: string) {
  // Convert ISO string to datetime-local input format
  const d = new Date(iso);
  return d.toISOString().slice(0, 16);
}

export default function EditReservationPage() {
  const router = useRouter();
  const { id } = router.query;
  const { data: reservationsData, isLoading } = useReservations();
  const reservations = reservationsData?.reservations ?? [];
  const { data: instructorsData } = useInstructors();
  const instructors = instructorsData?.users ?? [];
  const update = useUpdateReservation();

  const reservation = reservations.find((r) => r.id === parseInt(id as string));

  const { register, handleSubmit, reset, formState: { errors } } = useForm<{
    instructor_id: string;
    start_time: string;
    end_time: string;
    notes: string;
  }>();

  useEffect(() => {
    if (!isAuthenticated()) router.replace("/login");
  }, [router]);

  useEffect(() => {
    if (reservation) {
      reset({
        instructor_id: reservation.instructor_id?.toString() ?? "",
        start_time: toInputVal(reservation.start_time),
        end_time: toInputVal(reservation.end_time),
        notes: reservation.notes ?? "",
      });
    }
  }, [reservation, reset]);

  // Removed manual isLoading check, handled by QueryBoundary below

  const apiError = (update.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail;

  const onSubmit = async (values: { instructor_id: string; start_time: string; end_time: string; notes: string }) => {
    const payload: components["schemas"]["ReservationUpdateRequest"] = {
      reservation: {
        instructor_id: values.instructor_id ? parseInt(values.instructor_id) : undefined,
        start_time: new Date(values.start_time).toISOString(),
        end_time: new Date(values.end_time).toISOString(),
        notes: values.notes || undefined,
      }
    };
    if (!reservation) return;
    await update.mutateAsync({ id: reservation.id, data: payload });

    router.push("/reservations");
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
            <div className="max-w-lg">
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

                {update.isError && (
                  <div className="bg-danger/10 border border-danger/20 rounded-xl px-4 py-3 text-sm text-danger">
                    {apiError ?? "Update failed — check for conflicts"}
                  </div>
                )}

                <div className="flex gap-3 pt-2">
                  <button type="submit" disabled={update.isPending} className="btn-primary" id="save-edit">
                    {update.isPending ? "Saving…" : "Save Changes"}
                  </button>
                  <button type="button" onClick={() => router.back()} className="btn-ghost">Cancel</button>
                </div>
              </form>
            </div>
          </div>
        </QueryBoundary>
      </Layout>

    </>
  );
}
