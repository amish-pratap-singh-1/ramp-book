import { useState } from "react";
import { useRouter } from "next/router";
import Link from "next/link";
import { clearToken, getUserRole } from "@/lib/auth";
import { useMe } from "@/hooks/useMe";

const navItems = [
  { href: "/dashboard",    icon: "⊞", label: "Dashboard"  },
  { href: "/fleet",        icon: "✈", label: "Fleet"       },
  { href: "/reservations", icon: "📅", label: "My Bookings" },
];
const adminNav = [
  { href: "/admin", icon: "🛡", label: "Admin Panel" },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { data: meData } = useMe();
  const me = meData?.user;
  const role = getUserRole();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => { clearToken(); router.push("/login"); };

  const initials = me?.full_name
    ? me.full_name.split(" ").map((n: string) => n[0]).join("").slice(0, 2)
    : "?";

  return (
    <div className="flex min-h-screen bg-[#0f172a]">
      {/* ── Mobile Header & Hamburger ── */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-[#1e293b] border-b border-white/[0.07] flex items-center justify-between px-4 z-40">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-accent flex items-center justify-center text-sm text-[#0f172a] font-bold">✈</div>
          <div className="font-extrabold text-primary tracking-tight">RampBook</div>
        </div>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="text-primary p-2 focus:outline-none"
        >
          {mobileMenuOpen ? "✕" : "☰"}
        </button>
      </div>

      {/* ── Mobile Menu Overlay ── */}
      {mobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* ── Sidebar ── */}
      <aside className={`fixed inset-y-0 left-0 w-64 bg-[#1e293b] border-r border-white/[0.07] flex flex-col z-50 transform transition-transform duration-300 ease-in-out ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}`}>

        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-6 border-b border-white/[0.07]">
          <div className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center text-lg text-[#0f172a] flex-shrink-0">
            ✈
          </div>
          <div>
            <div className="text-[15px] font-extrabold text-primary tracking-tight">RampBook</div>
            <div className="text-[10px] text-muted uppercase tracking-widest">Flying Club</div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-3 flex flex-col gap-0.5">
          <p className="text-[10px] font-bold text-muted uppercase tracking-widest px-2 py-2">
            Navigation
          </p>
          {navItems.map((item) => {
            const active = router.pathname === item.href || router.pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150 ${
                  active
                    ? "bg-accent/10 text-accent"
                    : "text-secondary hover:bg-elevated hover:text-primary"
                }`}
              >
                <span className="w-5 text-center">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}

          {role === "admin" && (
            <>
              <p className="text-[10px] font-bold text-muted uppercase tracking-widest px-2 py-2 mt-3">
                Admin
              </p>
              {adminNav.map((item) => {
                const active = router.pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors duration-150 ${
                      active
                        ? "bg-accent/10 text-accent"
                        : "text-secondary hover:bg-elevated hover:text-primary"
                    }`}
                  >
                    <span className="w-5 text-center">{item.icon}</span>
                    {item.label}
                  </Link>
                );
              })}
            </>
          )}
        </nav>

        {/* User footer */}
        <div className="p-3 border-t border-white/[0.07]">
          <div className="flex items-center gap-2.5 p-2.5 rounded-xl hover:bg-elevated transition-colors group cursor-default">
            <div className="w-8 h-8 rounded-full bg-accent/10 border-2 border-accent/30 flex items-center justify-center text-xs font-bold text-accent flex-shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-primary truncate">{me?.full_name ?? "…"}</div>
              <div className="text-[10px] text-muted capitalize">{me?.role ?? role ?? ""}</div>
            </div>
            <button
              onClick={handleLogout}
              title="Logout"
              className="text-muted hover:text-danger transition-colors text-sm opacity-0 group-hover:opacity-100 ml-auto"
            >
              ⏻
            </button>
          </div>
        </div>
      </aside>

      {/* ── Page content ── */}
      <main className="flex-1 min-h-screen pt-16 lg:pt-0 lg:ml-64">{children}</main>
    </div>
  );
}
