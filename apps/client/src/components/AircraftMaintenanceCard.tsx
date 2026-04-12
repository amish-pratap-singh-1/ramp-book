import React from "react";
import { formatDisplay } from "@/lib/date-utils";
import type { components } from "@/api/schema";
import StatusBadge from "./StatusBadge";

type MaintenanceWindow = components["schemas"]["MaintenanceWindowResponse"];
type Aircraft = components["schemas"]["AircraftResponse"];

interface AircraftMaintenanceCardProps {
  aircraft: Aircraft;
  windows: MaintenanceWindow[];
  onAddMaintenance: (aircraftId: number) => void;
  onDeleteMaintenance: (windowId: number) => void;
  isDeleting?: boolean;
}

const AircraftMaintenanceCard: React.FC<AircraftMaintenanceCardProps> = ({
  aircraft,
  windows,
  onAddMaintenance,
  onDeleteMaintenance,
  isDeleting,
}) => {
  const isCurrentlyInMaintenance = windows.some((w) => {
    const now = new Date();
    return new Date(w.start_time) <= now && new Date(w.end_time) >= now;
  });

  const sortedWindows = [...windows].sort(
    (a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
  );

  return (
    <div className="card-hover flex flex-col h-full bg-surface/40 backdrop-blur-md border border-edge-strong">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-extrabold tracking-tight text-primary flex items-center gap-2">
            <span className="text-accent">✈️</span> {aircraft.tail_number}
          </h3>
          <p className="text-xs text-secondary font-medium uppercase tracking-wider mt-0.5">
            {aircraft.model}
          </p>
        </div>
        <StatusBadge status={isCurrentlyInMaintenance ? "maintenance" : "available"} />
      </div>

      <div className="flex-1 space-y-4">
        <div>
          <div className="text-[10px] font-bold text-muted uppercase tracking-widest mb-3 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-accent"></span>
            Schedule Timeline
          </div>
          
          {sortedWindows.length === 0 ? (
            <div className="py-8 px-4 border border-edge border-dashed rounded-xl text-center text-xs text-muted flex flex-col items-center gap-2">
              <span className="text-2xl opacity-20">📅</span>
              No maintenance scheduled
            </div>
          ) : (
            <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1 custom-scrollbar">
              {sortedWindows.map((w) => (
                <div 
                  key={w.id} 
                  className="group relative bg-base/50 border border-edge rounded-xl p-3 hover:border-accent/30 transition-all"
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1 min-w-0">
                      <div className="text-[13px] font-bold text-primary truncate">
                        {w.reason || "Scheduled Inspection"}
                      </div>
                      <div className="text-[11px] text-secondary mt-1 flex flex-col gap-0.5">
                        <span className="flex items-center gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-ok/50"></span>
                          {formatDisplay(w.start_time, "MMM d, h:mm a")}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <span className="w-1 h-1 rounded-full bg-danger/50"></span>
                          {formatDisplay(w.end_time, "MMM d, h:mm a")}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => onDeleteMaintenance(w.id)}
                      disabled={isDeleting}
                      className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-muted hover:text-danger hover:bg-danger/10 transition-all cursor-pointer"
                      title="Remove window"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-edge flex items-center justify-between">
        <div className="text-[10px] text-muted font-medium">
          {windows.length} scheduled windows
        </div>
        <button
          onClick={() => onAddMaintenance(aircraft.id)}
          className="btn-ghost !px-3 !py-1.5 !text-[11px] flex items-center gap-1.5"
        >
          <span>➕</span> Schedule
        </button>
      </div>
    </div>
  );
};

export default AircraftMaintenanceCard;
