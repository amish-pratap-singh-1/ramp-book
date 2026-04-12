import { ReactQueryProvider } from "@/providers/react-query";
import "react-big-calendar/lib/css/react-big-calendar.css";
import "@/styles/globals.css";
import type { AppProps } from "next/app";
import { useEffect, useState } from "react";

export default function App({ Component, pageProps }: AppProps) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <ReactQueryProvider>
      {mounted ? <Component {...pageProps} /> : <div className="min-h-screen bg-[#0f172a]" />}
    </ReactQueryProvider>
  );
}
