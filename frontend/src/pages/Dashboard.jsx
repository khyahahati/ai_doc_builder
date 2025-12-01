import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../api";

export default function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem("accessToken");

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      setLoading(true);
      try {
        if (!token) {
          setProjects([]);
          return;
        }
        const data = await api.get("/projects/my", token);
        if (mounted) setProjects(data ?? []);
      } catch (err) {
        console.error("Failed to load projects", err);
      } finally {
        if (mounted) setLoading(false);
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, [token]);

  return (
    <section className="mx-auto w-full max-w-6xl px-6 pt-32 pb-16">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-white">Dashboard</h1>
          <p className="text-sm text-gray-400">Pick up where you left off or spin up a new document.</p>
        </div>
        <div className="flex gap-3">
          <Link
            to="/create"
            className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Create project
          </Link>
          <button
            onClick={() => navigate(0)}
            className="inline-flex items-center justify-center rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-gray-200"
          >
            Refresh
          </button>
        </div>
      </header>

      <div className="mt-10 grid gap-4 md:grid-cols-2">
        {loading && <p className="text-sm text-gray-400">Loading projects</p>}
        {!loading && projects.length === 0 && (
          <div className="rounded-2xl border border-dashed border-white/10 bg-black/10 px-6 py-8 text-center text-sm text-gray-400">
            No projects found. Create one to get started.
          </div>
        )}

        {projects.map((project) => (
          <Link
            key={project.id}
            to={`/workspace/${project.id}`}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-blue-500 hover:bg-blue-600/20"
          >
            <p className="text-xs uppercase tracking-[0.25em] text-gray-500">{project.doc_type?.toUpperCase() ?? 'DOC'}</p>
            <h2 className="mt-2 text-lg font-semibold text-white">{project.title}</h2>
            <p className="mt-3 text-xs text-gray-400">Created {new Date(project.created_at).toLocaleString()}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
