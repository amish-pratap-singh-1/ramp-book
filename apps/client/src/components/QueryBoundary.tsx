import React from "react";
import LoadingSpinner from "./LoadingSpinner";
import Error from "./Error";

interface QueryBoundaryProps {
  isLoading?: boolean;
  isError?: boolean;
  data?: any;
  error?: any;
  children: React.ReactNode;
  loadingComponent?: React.ReactNode;
  fallback?: React.ReactNode;
}

/**
 * A centralized boundary for handling API query states.
 * Centralizing this ensures a consistent UI for loading and error states.
 */
export default function QueryBoundary({
  isLoading,
  isError,
  data,
  error,
  children,
  loadingComponent,
  fallback,
}: QueryBoundaryProps) {
  if (isError) {
    return (fallback as React.ReactElement) || (
      <Error 
        message={typeof error === "string" ? error : error?.response?.data?.detail || error?.message} 
      />
    );
  }

  // The condition !data is optional but often requests include it to ensure 
  // we don't render children before data is defined.
  if (isLoading || !data) {
    return (loadingComponent as React.ReactElement) || (
      <div className="w-full flex justify-center py-20">
        <LoadingSpinner />
      </div>
    );
  }

  return <>{children}</>;
}
