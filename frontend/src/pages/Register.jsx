import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export default function Register() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    if (!email.trim() || !password) {
      setError("Email and password are required.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const registerResponse = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: email.trim(),
          password,
        }),
      });

      const registerData = await registerResponse.json().catch(() => null);
      if (!registerResponse.ok) {
        const message = (typeof registerData === "object" && registerData?.detail) || "Unable to create your account.";
        throw new Error(message);
      }

      const loginPayload = new URLSearchParams();
      loginPayload.append("username", email.trim());
      loginPayload.append("password", password);

      const loginResponse = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: loginPayload.toString(),
      });

      const loginData = await loginResponse.json().catch(() => null);
      if (!loginResponse.ok) {
        const message = (typeof loginData === "object" && loginData?.detail) || "Account created, but automatic login failed.";
        throw new Error(message);
      }

      const accessToken = loginData?.access_token;
      if (!accessToken) {
        throw new Error("Missing token after registration.");
      }

      localStorage.setItem("accessToken", accessToken);

      const profileResponse = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      if (profileResponse.ok) {
        const profile = await profileResponse.json().catch(() => null);
        if (profile) {
          localStorage.setItem("currentUser", JSON.stringify(profile));
        }
      }

      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 pt-32 pb-16">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-8 backdrop-blur-xl">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-semibold text-white">Create your account</h1>
          <p className="text-sm text-gray-400">Start collaborating with AI-assisted document workflows.</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <label className="flex flex-col gap-2 text-sm">
            <span className="text-gray-300">Email</span>
            <input
              type="email"
              autoComplete="email"
              className="rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              disabled={loading}
            />
          </label>

          <label className="flex flex-col gap-2 text-sm">
            <span className="text-gray-300">Password</span>
            <input
              type="password"
              autoComplete="new-password"
              className="rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              placeholder="Create a secure password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              disabled={loading}
            />
          </label>

          {error ? (
            <p className="rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-300">{error}</p>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Creating account…" : "Sign up"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-gray-400">
          Already have an account?{" "}
          <Link to="/login" className="text-blue-400 hover:text-blue-300">
            Log in
          </Link>
        </p>
      </div>
    </section>
  );
}
