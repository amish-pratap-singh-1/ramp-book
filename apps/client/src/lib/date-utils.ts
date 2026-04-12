import { format as dfnsFormat, parseISO } from "date-fns";

/**
 * Converts a Date or ISO string to a local-time string 
 * compatible with <input type="datetime-local"> (YYYY-MM-DDTHH:mm).
 */
export function formatDateForInput(date: string | Date | undefined | null): string {
  if (!date) return "";
  const d = typeof date === "string" ? new Date(date) : date;
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  const hour = String(d.getHours()).padStart(2, "0");
  const min = String(d.getMinutes()).padStart(2, "0");
  
  return `${year}-${month}-${day}T${hour}:${min}`;
}

/**
 * Converts a local datetime-local string (YYYY-MM-DDTHH:mm) 
 * back to a UTC ISO string for the API.
 */
export function formatDateForAPI(localString: string | undefined | null): string | undefined {
  if (!localString) return undefined;
  // new Date("YYYY-MM-DDTHH:mm") parses as LOCAL time
  return new Date(localString).toISOString();
}

/**
 * Formats a date for display using the local timezone.
 * Wrapper for date-fns format.
 */
export function formatDisplay(date: string | Date | undefined | null, pattern: string): string {
  if (!date) return "";
  const d = typeof date === "string" ? parseISO(date) : date;
  return dfnsFormat(d, pattern);
}

/**
 * Safely parses any date input into a local Date object.
 */
export function toLocalDate(date: string | Date | undefined | null): Date {
  if (!date) return new Date();
  return typeof date === "string" ? new Date(date) : date;
}
