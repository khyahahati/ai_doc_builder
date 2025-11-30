import { Link } from "react-router-dom";

const mockProjects = [
  {
    id: "1",
    name: "Q4 Revenue Enablement Deck",
    updatedAt: "20 minutes ago",
    docType: "pptx"
  },
  {
    id: "2",
    name: "Customer Success Playbook",
    updatedAt: "Yesterday",
    docType: "docx"
  }
];

export default function Dashboard() {
  return (
    <section className="mx-auto w-full max-w-6xl px-6 pt-32 pb-16">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-semibold text-white">Dashboard</h1>
          <p className="text-sm text-gray-400">Pick up where you left off or spin up a new document.</p>
        </div>
        <Link
          to="/create"
          className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Create project
        </Link>
      </header>

      <div className="mt-10 grid gap-4 md:grid-cols-2">
        {mockProjects.map((project) => (
          <Link
            key={project.id}
            to={`/workspace/${project.id}`}
            className="rounded-2xl border border-white/10 bg-white/5 p-5 transition hover:border-blue-500 hover:bg-blue-600/20"
          >
            <p className="text-xs uppercase tracking-[0.25em] text-gray-500">{project.docType.toUpperCase()}</p>
            <h2 className="mt-2 text-lg font-semibold text-white">{project.name}</h2>
            <p className="mt-3 text-xs text-gray-400">Last updated {project.updatedAt}</p>
          </Link>
        ))}
      </div>
    </section>
  );
}
