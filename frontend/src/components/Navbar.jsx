import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="fixed top-0 left-0 w-full z-50 border-b border-white/10 backdrop-blur-xl bg-[#07080c]/70">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-6 px-6 py-4">

        <Link to="/" className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 via-purple-500 to-blue-300 text-lg font-semibold text-white shadow-[0_15px_35px_rgba(59,130,246,0.35)]">
            AI
          </span>
          <span className="bg-gradient-to-r from-blue-300 via-purple-300 to-blue-200 bg-clip-text text-xl font-semibold tracking-tight text-transparent">
            Doc Builder
          </span>
        </Link>

        <div className="flex items-center gap-3 text-sm font-medium text-gray-300">
          <Link
            to="/dashboard"
            className="transition hover:text-white"
          >
            Dashboard
          </Link>
          <Link
            to="/login"
            className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-gray-200 transition hover:bg-white/10"
          >
            Log in
          </Link>
        </div>

      </div>
    </header>
  );
}
