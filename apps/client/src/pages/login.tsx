import { useForm } from "react-hook-form";
import { components } from "@/api/schema";
import { useLogin } from "@/hooks/useLogin";

type LoginRequest = components["schemas"]["LoginRequest"];

export default function LoginPage() {
  const { register, handleSubmit } = useForm<LoginRequest>();
  const login = useLogin();

  const onSubmit = (data: LoginRequest) => {
    login.mutate(data);
  };

  return (
    <div style={{ maxWidth: 400, margin: "100px auto" }}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <input
          {...register("email")}
          placeholder="Email"
          style={{ width: "100%", marginBottom: 10 }}
        />

        <input
          {...register("password")}
          type="password"
          placeholder="Password"
          style={{ width: "100%", marginBottom: 10 }}
        />

        <button type="submit" disabled={login.isPending}>
          {login.isPending ? "Logging in..." : "Login"}
        </button>

        {login.isError && <p style={{ color: "red" }}>Login failed</p>}
      </form>
    </div>
  );
}
