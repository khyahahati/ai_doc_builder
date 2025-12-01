// src/pages/Home.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../api";

const heroVariants = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0 }
};

export default function Home() {
  const [docType, setDocType] = useState("docx");
  const [title, setTitle] = useState("");
  const [outline, setOutline] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleGenerateDraft = async () => {
    // If no title, just navigate to workspace without creating
    if (!title.trim()) {
      // fallback: open workspace in dev mode with docType query
      navigate(`/workspace?docType=${docType}`);
      return;
    }

    setLoading(true);
    const token = localStorage.getItem("accessToken");

    // Payload expected by your backend: { title, doc_type }
    // you said you don't want to save summary/guidance here — but workspace expects a project.
    // pass `context` as the outline so backend can use it when generating/initializing.
    const payload = {
      title: title.trim(),
      doc_type: docType,
      context: outline.trim() || undefined
    };

    try {
      // If the user is authenticated, create project on backend and open workspace for returned id
      if (token) {
        const data = await api.postJSON("/projects/", payload, token);
        if (data && data.id) {
          // navigate to workspace with created project id
          navigate(`/workspace/${data.id}`);
          return;
        }
      }

      // If unauthenticated or backend didn't return id, fall back to workspace query-mode
      // We'll encode title + outline into query params (note: keep small)
      const q = new URLSearchParams({
        docType,
        title: title.trim(),
        context: outline.trim()
      }).toString();
      navigate(`/workspace?${q}`);
    } catch (err) {
      // If project creation failed, still open workspace in query-mode and log error
      console.error("Create project failed — falling back to local workspace", err);
      const q = new URLSearchParams({
        docType,
        title: title.trim(),
        context: outline.trim()
      }).toString();
      navigate(`/workspace?${q}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-[#0e0f14]">
      {/* background glow */}
      <div className="pointer-events-none absolute inset-0 -z-10 flex justify-center">
        <div className="h-[42rem] w-[42rem] rounded-full bg-blue-600/20 blur-[180px]" />
      </div>

      <section className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl flex-col items-center justify-center px-6 pt-32 pb-20 text-center">
        <motion.h1
          variants={heroVariants}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.6 }}
          className="text-4xl font-bold leading-tight text-white md:text-6xl lg:text-7xl"
        >
          Craft polished documents
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-300 bg-clip-text text-transparent"> effortlessly </span>
          with AI guidance.
        </motion.h1>

        <motion.p
          variants={heroVariants}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.6, delay: 0.15 }}
          className="mt-6 max-w-3xl text-base text-gray-300 md:text-lg"
        >
          Generate outlines, produce long-form content, and iterate with feedback in one workspace. We streamline every revision so your team ships documentation that reads like it was handcrafted.
        </motion.p>

        <motion.div
          variants={heroVariants}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 w-full max-w-2xl"
        >
          <div className="flex flex-col gap-4 rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl shadow-[0_0_35px_rgba(59,130,246,0.15)]">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="flex flex-col gap-2">
                <label className="text-left text-xs font-semibold uppercase tracking-[0.14em] text-gray-400">
                  Title
                </label>
                <input
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  placeholder="e.g. Onboarding Guide for Sales"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-left text-xs font-semibold uppercase tracking-[0.14em] text-gray-400">
                  Outline / Sections
                </label>
                <textarea
                  value={outline}
                  onChange={(e) => setOutline(e.target.value)}
                  rows={1}
                  className="h-full min-h-[48px] w-full rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-400 focus:border-blue-500 focus:outline-none"
                  placeholder="Enter Sections/Outline points here"
                />
              </div>
            </div>

            <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
              <div className="flex flex-col gap-3 md:w-64">
                <span className="text-xs font-semibold uppercase tracking-[0.14em] text-gray-400">
                  Document type
                </span>
                <div className="flex gap-2">
                  {[
                    { id: "docx", label: "DOCX" },
                    { id: "pptx", label: "PPTX" }
                  ].map(({ id, label }) => (
                    <button
                      key={id}
                      type="button"
                      onClick={() => setDocType(id)}
                      className={`flex-1 rounded-lg border px-4 py-3 text-sm font-semibold transition ${
                        docType === id
                          ? "border-blue-500 bg-blue-600 text-white shadow-[0_8px_25px_rgba(59,130,246,0.25)]"
                          : "border-white/10 bg-transparent text-gray-300 hover:bg-white/10"
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={handleGenerateDraft}
                disabled={loading}
                className="w-full rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 md:w-48 disabled:opacity-60"
              >
                {loading ? "Creating draft…" : "Generate draft"}
              </button>
            </div>
          </div>

          <p className="mt-3 text-xs text-gray-400 md:text-sm">
            No credit card required. Spin up a draft in seconds, then refine it with real-time AI suggestions.
          </p>
        </motion.div>

        <motion.div
          variants={heroVariants}
          initial="hidden"
          animate="show"
          transition={{ duration: 0.6, delay: 0.45 }}
          className="mt-16 grid w-full max-w-5xl gap-6 md:grid-cols-3"
        >
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-left">
            <h3 className="text-lg font-semibold text-white">Smarter outlines</h3>
            <p className="mt-2 text-sm text-gray-300">
              Auto-refine structure suggestions tailored to the document type and your audience.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-left">
            <h3 className="text-lg font-semibold text-white">Guided revisions</h3>
            <p className="mt-2 text-sm text-gray-300">
              Evaluate drafts instantly and apply targeted edits sourced from expert writing patterns.
            </p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-6 text-left">
            <h3 className="text-lg font-semibold text-white">One-click exports</h3>
            <p className="mt-2 text-sm text-gray-300">
              Deliver polished PDFs or DOCX files pre-formatted for stakeholders and clients.
            </p>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
