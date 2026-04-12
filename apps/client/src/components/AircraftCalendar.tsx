import { Calendar, dateFnsLocalizer, SlotInfo, View } from "react-big-calendar";
import { format, parse, startOfWeek, getDay } from "date-fns";
import { enUS } from "date-fns/locale";
import React from "react";
import LoadingSpinner from "./LoadingSpinner";

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales: { "en-US": enUS },
});

export interface CalendarEvent {
  id: string | number;
  title: string;
  start: Date;
  end: Date;
  type?: "reservation" | "maintenance" | "draft";
  resourceId?: number;
  isDraft?: boolean;
}

export interface CalendarResource {
  id: number;
  title: string;
}

interface AircraftCalendarProps {
  events: CalendarEvent[];
  resources?: CalendarResource[];
  view?: View;
  onViewChange?: (view: View) => void;
  date?: Date;
  onDateChange?: (date: Date) => void;
  onSelectSlot?: (slotInfo: SlotInfo) => void;
  onSelectEvent?: (event: CalendarEvent) => void;
  isLoading?: boolean;
  minTime?: Date;
  maxTime?: Date;
  selectable?: boolean;
  height?: string | number;
}

const AircraftCalendar: React.FC<AircraftCalendarProps> = ({
  events,
  resources,
  view = "week",
  onViewChange,
  date = new Date(),
  onDateChange,
  onSelectSlot,
  onSelectEvent,
  isLoading,
  minTime = new Date(0, 0, 0, 6, 0, 0),
  maxTime = new Date(0, 0, 0, 22, 0, 0),
  selectable = true,
  height = 750,
}) => {
  const eventPropGetter = (event: CalendarEvent) => {
    if (event.isDraft) {
      if (event.type === "maintenance") {
        return { 
          className: "rbc-event-draft-maintenance",
          style: { backgroundColor: "rgba(239, 68, 68, 0.4)", border: "2px dashed #b91c1c", color: "#000" } 
        };
      }
      return { 
        className: "rbc-event-draft",
        style: { backgroundColor: "rgba(56, 189, 248, 0.4)", border: "2px dashed #0ea5e9", color: "#000" } 
      };
    }
    
    if (event.type === "maintenance") {
      return { 
        className: "rbc-event-maintenance",
        style: { 
          backgroundColor: "#ef4444", 
          backgroundImage: "repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(0,0,0,0.05) 10px, rgba(0,0,0,0.05) 20px)",
          borderColor: "#991b1b", 
          color: "#ffffff",
          fontWeight: "bold",
        } 
      };
    }
    
    if (event.type === "reservation") {
      return { 
        className: "rbc-event-reservation",
        style: { backgroundColor: "#38bdf8", borderColor: "#0284c7", color: "#ffffff" } 
      };
    }
    
    return { className: "rbc-event" };
  };

  return (
    <div className="relative" style={{ height }}>
      {isLoading && (
        <div className="absolute inset-0 bg-surface/50 z-10 flex items-center justify-center backdrop-blur-[2px] rounded-xl">
          <LoadingSpinner />
        </div>
      )}
      <Calendar
        localizer={localizer}
        events={events}
        resources={resources}
        resourceIdAccessor="id"
        resourceTitleAccessor="title"
        startAccessor="start"
        endAccessor="end"
        date={date}
        onNavigate={onDateChange}
        view={view}
        onView={onViewChange}
        views={resources ? ["day", "week", "month"] : ["week", "day", "month"]}
        selectable={selectable}
        onSelectSlot={onSelectSlot}
        onSelectEvent={onSelectEvent as any}
        eventPropGetter={eventPropGetter}
        step={30}
        timeslots={2}
        min={minTime}
        max={maxTime}
        className="rounded-xl overflow-hidden"
      />
    </div>
  );
};

export default AircraftCalendar;
