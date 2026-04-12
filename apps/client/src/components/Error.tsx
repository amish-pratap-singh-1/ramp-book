import React from "react";
import Link from "next/link";

interface ErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export default function Error({ 
  title = "Something went wrong", 
  message = "We encountered an error while fetching the data. Please try again later.",
  onRetry 
}: ErrorProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 px-6 text-center animate-[fadeIn_0.3s_ease]">
      <div className="w-16 h-16 bg-danger/10 text-danger rounded-2xl flex items-center justify-center mb-6 text-3xl shadow-[0_0_20px_rgba(239,68,68,0.15)]">
        ⚠️
      </div>
      <h2 className="text-xl font-bold text-primary mb-2 tracking-tight">{title}</h2>
      <p className="text-sm text-secondary max-w-xs mb-8 leading-relaxed">
        {message}
      </p>
      <div className="flex gap-3">
        {onRetry && (
          <button 
            onClick={onRetry}
            className="btn-primary"
          >
            Try Again
          </button>
        )}
        <Link href="/dashboard" className="btn-ghost">
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
