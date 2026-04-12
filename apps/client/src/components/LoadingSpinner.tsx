export default function LoadingSpinner({ fullPage = false }: { fullPage?: boolean }) {
  if (fullPage) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 bg-[#0f172a]">
        <div className="w-10 h-10 border-[3px] border-white/10 border-t-[#0ea5e9] rounded-full animate-spin" />
        <p className="text-sm text-slate-500">Loading...</p>
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center py-20">
      <div className="w-7 h-7 border-2 border-white/10 border-t-[#0ea5e9] rounded-full animate-spin" />
    </div>
  );
}
