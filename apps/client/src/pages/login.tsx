import { useForm } from "react-hook-form";
import { components } from "@/api/schema";
import { useLogin } from "@/hooks/useLogin";
import Head from "next/head";

type LoginRequest = components["schemas"]["LoginRequest"];

export default function LoginPage() {
  const { register, handleSubmit } = useForm<LoginRequest>();
  const login = useLogin();

  const onSubmit = (data: LoginRequest) => login.mutate(data);

  const apiError = (login.error as { response?: { data?: { detail?: string } } })
    ?.response?.data?.detail;

  return (
    <>
      <Head>
        <title>Sign In — RampBook</title>
        <meta name="description" content="Sign in to RampBook flying club reservation system" />
      </Head>

      <div className="min-h-screen bg-[#0b0f1a] flex items-center justify-center p-6 relative overflow-hidden">
        {/* Ambient glow */}
        <div className="absolute w-[600px] h-[600px] rounded-full bg-accent/5 blur-[80px] pointer-events-none top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />

        <div className="relative w-full max-w-[420px]">
          {/* Card */}
          <div className="bg-[#111827] border border-white/[0.1] rounded-2xl p-10 shadow-2xl">

            {/* Logo */}
            <div className="flex items-center gap-3 mb-8">
              <div className="w-11 h-11 rounded-xl bg-accent flex items-center justify-center text-2xl text-[#0b0f1a]">
                ✈
              </div>
              <div>
                <h1 className="text-xl font-extrabold text-primary tracking-tight">RampBook</h1>
                <p className="text-xs text-muted">Cedar Valley Flying Club</p>
              </div>
            </div>

            <h2 className="text-lg font-bold text-primary mb-1">Welcome back</h2>
            <p className="text-sm text-secondary mb-8">Sign in to access your club portal</p>

            <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-5" id="login-form">
              <div className="field">
                <label className="label" htmlFor="email">Email</label>
                <input
                  id="email"
                  {...register("email")}
                  type="email"
                  placeholder="you@cedarvalleyfc.com"
                  className="input"
                  autoComplete="email"
                />
              </div>

              <div className="field">
                <label className="label" htmlFor="password">Password</label>
                <input
                  id="password"
                  {...register("password")}
                  type="password"
                  placeholder="••••••••"
                  className="input"
                  autoComplete="current-password"
                />
              </div>

              {login.isError && (
                <div className="bg-danger/10 border border-danger/20 rounded-xl px-4 py-3 text-sm text-danger">
                  {apiError ?? "Invalid email or password"}
                </div>
              )}

              <button
                type="submit"
                id="login-submit"
                disabled={login.isPending}
                className="btn-primary w-full justify-center mt-1"
              >
                {login.isPending ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-[#0b0f1a]/30 border-t-[#0b0f1a] rounded-full animate-spin" />
                    Signing in…
                  </span>
                ) : (
                  "Sign In →"
                )}
              </button>
            </form>

            <div className="mt-8 pt-6 border-t border-white/[0.06] text-center">
              <p className="text-xs text-muted">Demo password for all accounts: <span className="text-secondary font-mono">changeme123</span></p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
