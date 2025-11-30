import { useState } from "react";

export default function SectionEditor({
  section,
  isGenerating = false,
  onChange,
  onGenerate,
  onFeedback
}) {
  const [showFeedbackForm, setShowFeedbackForm] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState("");

  if (!section) {
    return (
      <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-white/10 bg-white/5 text-sm text-gray-400">
        Select a section to begin.
      </div>
    );
  }

  const handleFieldChange = (field, value) => {
    onChange?.(section.id, { [field]: value });
  };

  const handleGenerate = () => {
    onGenerate?.(section.id);
  };

  const handleLike = () => {
    onFeedback?.(section.id, { sentiment: "like" });
    setShowFeedbackForm(false);
    setFeedbackMessage("");
  };

  const handleDislike = () => {
    setShowFeedbackForm(true);
  };

  const submitFeedback = () => {
    const trimmed = feedbackMessage.trim();
    if (!trimmed) {
      return;
    }

    onFeedback?.(section.id, { sentiment: "dislike", message: trimmed });
    setFeedbackMessage("");
    setShowFeedbackForm(false);
  };

  const cancelFeedback = () => {
    setShowFeedbackForm(false);
    setFeedbackMessage("");
  };

  return (
    <div className="relative rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
      {isGenerating && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-3 rounded-3xl bg-[#0e0f14]/90">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-500/40 border-t-blue-500" />
          <p className="text-sm font-medium text-gray-200">Generating updated content...</p>
        </div>
      )}

      <div className="flex flex-col gap-6">
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
              Section title
            </label>
            <button
              type="button"
              onClick={handleGenerate}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-900/60"
              disabled={isGenerating}
            >
              Generate content
            </button>
          </div>
          <input
            value={section.title}
            onChange={(event) => handleFieldChange("title", event.target.value)}
            className="rounded-xl border border-transparent bg-black/20 px-4 py-3 text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            placeholder="Executive Summary"
            disabled={isGenerating}
          />
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
              Summary / beats
            </label>
            <textarea
              value={section.summary ?? ""}
              onChange={(event) => handleFieldChange("summary", event.target.value)}
              rows={5}
              className="rounded-2xl border border-transparent bg-black/20 px-4 py-4 text-sm leading-relaxed text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              placeholder="Outline the beats you want the AI to cover."
              disabled={isGenerating}
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
              Guidance for AI
            </label>
            <textarea
              value={section.guidance ?? ""}
              onChange={(event) => handleFieldChange("guidance", event.target.value)}
              rows={5}
              className="rounded-2xl border border-transparent bg-black/10 px-4 py-4 text-sm leading-relaxed text-gray-200 placeholder-gray-500 focus:border-blue-500 focus:outline-none"
              placeholder="Share tone, data points, or links to include when generating content."
              disabled={isGenerating}
            />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
            Generated content
          </label>
          <textarea
            value={section.content ?? ""}
            onChange={(event) => handleFieldChange("content", event.target.value)}
            rows={12}
            className="min-h-[240px] rounded-2xl border border-transparent bg-black/20 px-4 py-4 text-sm leading-relaxed text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
            placeholder="Once you generate a draft, it will appear here for polishing."
            disabled={isGenerating}
          />
        </div>

        <div className="flex flex-col gap-4 border-t border-white/10 pt-4">
          <div className="flex flex-wrap items-center gap-3">
            <span className="text-xs font-semibold uppercase tracking-[0.3em] text-gray-500">
              Rate this draft
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleLike}
                className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-gray-200 transition hover:bg-white/10"
                disabled={isGenerating}
              >
                👍 Looks good
              </button>
              <button
                type="button"
                onClick={handleDislike}
                className="rounded-full border border-white/10 px-4 py-2 text-xs font-semibold text-gray-200 transition hover:bg-white/10"
                disabled={isGenerating}
              >
                👎 Needs changes
              </button>
            </div>
          </div>

          {showFeedbackForm && (
            <div className="rounded-2xl border border-white/10 bg-black/30 p-4">
              <label className="text-xs font-semibold uppercase tracking-[0.12em] text-gray-400">
                Tell us what to fix
              </label>
              <textarea
                value={feedbackMessage}
                onChange={(event) => setFeedbackMessage(event.target.value)}
                rows={4}
                className="mt-2 w-full rounded-2xl border border-transparent bg-black/40 px-4 py-3 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
                placeholder="Describe what you want to adjust, e.g. tone, missing data, structure."
                disabled={isGenerating}
              />
              <div className="mt-3 flex gap-2">
                <button
                  type="button"
                  onClick={submitFeedback}
                  className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-blue-900/60"
                  disabled={isGenerating}
                >
                  Send to AI
                </button>
                <button
                  type="button"
                  onClick={cancelFeedback}
                  className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-gray-300 transition hover:bg-white/10"
                  disabled={isGenerating}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {section.lastFeedback && (
            <p className="text-xs text-gray-400">
              Last feedback sent · {section.lastFeedback.sentiment === "like" ? "Marked as ready" : section.lastFeedback.message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
