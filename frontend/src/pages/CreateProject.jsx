import { useState } from "react";

const documentOptions = [
  { id: "docx", label: "Word document" },
  { id: "pptx", label: "Presentation" }
];

export default function CreateProject() {
  const [selectedType, setSelectedType] = useState("docx");

  return (
    <section className="mx-auto w-full max-w-4xl px-6 pt-32 pb-16">
      <header className="mb-10">
        <h1 className="text-3xl font-semibold text-white">New project</h1>
        <p className="text-sm text-gray-400">Describe what you want to produce and choose the best output format.</p>
      </header>

      <form className="flex flex-col gap-6">
        <label className="flex flex-col gap-2 text-sm">
          <span className="text-gray-300">Project title</span>
          <input
            className="rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            placeholder="Investor Update – November 2025"
          />
        </label>

        <label className="flex flex-col gap-2 text-sm">
          <span className="text-gray-300">Context</span>
          <textarea
            rows={6}
            className="rounded-2xl border border-transparent bg-black/20 px-4 py-4 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            placeholder="Share goals, audience, and any constraints for the document."
          />
        </label>

        <div className="flex flex-col gap-3">
          <span className="text-sm font-medium text-gray-300">Document type</span>
          <div className="grid gap-3 md:grid-cols-2">
            {documentOptions.map((option) => {
              const isSelected = option.id === selectedType;

              return (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => setSelectedType(option.id)}
                  className={`rounded-2xl border px-5 py-4 text-left transition ${
                    isSelected
                      ? "border-blue-500 bg-blue-600/30 text-white"
                      : "border-white/10 bg-white/5 text-gray-200 hover:bg-white/10"
                  }`}
                >
                  <p className="text-sm font-semibold">{option.label}</p>
                  <p className="text-xs text-gray-400">{option.id.toUpperCase()}</p>
                </button>
              );
            })}
          </div>
        </div>

        <button
          type="submit"
          className="mt-4 w-full rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Create and open workspace
        </button>
      </form>
    </section>
  );
}
