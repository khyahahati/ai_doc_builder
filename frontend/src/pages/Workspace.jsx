// src/pages/Workspace.jsx
import { useMemo, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import OutlineList from "../components/OutlineList.jsx";
import SectionEditor from "../components/SectionEditor.jsx";
import api from "../api";

const seedSections = [
  {
    id: "overview",
    title: "Overview",
    summary: "Set the stage for what the reader needs to know right away.",
    guidance: "Highlight the big outcome and the teams involved.",
    content: "Our Q4 revenue enablement focuses on equipping field teams with the latest messaging...",
    lastFeedback: null,
    persisted: false,
  },
  {
    id: "initiatives",
    title: "Key initiatives",
    summary: "Break down the programs that drove results.",
    guidance: "List the three initiatives that moved the needle.",
    content: "1. Competitive differentiators workshop...",
    lastFeedback: null,
    persisted: false,
  },
];

export default function Workspace() {
  const [sections, setSections] = useState(seedSections);
  const [activeId, setActiveId] = useState(seedSections[0]?.id ?? null);
  const [generatingSectionId, setGeneratingSectionId] = useState(null);
  const [projectTitle, setProjectTitle] = useState("");          // 🔹 NEW
  const { projectId } = useParams();

  // 🔹 Load persisted sections + project title when entering a saved project
  useEffect(() => {
    const token = localStorage.getItem("accessToken");
    if (!projectId || !token) {
      // No projectId → stay with local seedSections (hero "Generate draft" flow)
      return;
    }

    (async () => {
      try {
        // fetch project meta + sections in parallel
        const [project, data] = await Promise.all([
          api.get(`/projects/${projectId}`, token),
          api.get(`/projects/${projectId}/sections`, token),
        ]);

        if (project && project.title) {
          setProjectTitle(project.title);
        }

        if (!data || data.length === 0) {
          // No sections yet for this project
          return;
        }

        const loaded = data.map((s) => ({
          id: String(s.id),
          title: s.title,
          summary: "",
          guidance: "",
          content: s.content ?? "",
          lastFeedback: null,
          persisted: true,
          version: s.version ?? 1,
        }));

        setSections(loaded);
        setActiveId(loaded[0]?.id ?? null);
      } catch (err) {
        console.error("Failed to load project or sections", err);
      }
    })();
  }, [projectId]);

  const activeSection = useMemo(
    () => sections.find((section) => String(section.id) === String(activeId)) ?? null,
    [sections, activeId]
  );

  // Helper to build the explicit user_prompt from UI fields
  const buildUserPrompt = (section) => {
    if (!section) return "";
    const summaryPart = (section.summary ?? "").trim();
    const guidancePart = (section.guidance ?? "").trim();
    if (summaryPart && guidancePart) {
      return `${summaryPart}\n\nGuidance: ${guidancePart}`;
    }
    if (summaryPart) return summaryPart;
    if (guidancePart) return `Guidance: ${guidancePart}`;
    const contentPart = (section.content ?? "").trim();
    return contentPart ? `Current content: ${contentPart.slice(0, 2000)}` : "";
  };

  const composeDraft = (section) => {
    const paragraphs = [];

    if (section.summary?.trim()) {
      paragraphs.push(section.summary.trim());
    }

    if (section.guidance?.trim()) {
      paragraphs.push(`Guidance applied: ${section.guidance.trim()}`);
    }

    paragraphs.push(
      "[Placeholder] Generated content will appear here once the backend service is connected."
    );

    return paragraphs.join("\n\n");
  };

  const handleAddSection = () => {
    const index = sections.length + 1;
    const id = `draft-${index}`;

    setSections((current) => [
      ...current,
      {
        id,
        title: `Draft section ${index}`,
        summary: "Describe the goals of this section before refining.",
        guidance: "Add tone, data, or constraints the AI should follow.",
        content: "",
        lastFeedback: null,
        persisted: false,
      },
    ]);

    setActiveId(id);
  };

  const handleSectionChange = (sectionId, updates) => {
    setSections((current) =>
      current.map((section) =>
        String(section.id) === String(sectionId) ? { ...section, ...updates } : section
      )
    );
  };

  // === GENERATE ===
  const handleGenerate = async (sectionId) => {
    setGeneratingSectionId(sectionId);
    const token = localStorage.getItem("accessToken");
    const section = sections.find((s) => String(s.id) === String(sectionId));
    const persisted = !!section?.persisted;

    if (!persisted) {
      if (!token || !projectId) {
        console.warn("No token or project; cannot persist section. Falling back to local placeholder.");
        await new Promise((r) => setTimeout(r, 800));
        setSections((current) =>
          current.map((s) =>
            String(s.id) === String(sectionId)
              ? {
                  ...s,
                  content: composeDraft(s),
                  lastFeedback: {
                    sentiment: "generate",
                    message: "Draft generated (local)",
                    at: new Date().toISOString(),
                  },
                }
              : s
          )
        );
        setGeneratingSectionId(null);
        return;
      }

      try {
        const titles = sections.map((s) => s.title);
        await api.postJSON(`/projects/${projectId}/outline`, { sections: titles }, token);

        const data = await api.get(`/projects/${projectId}/sections`, token);
        const localByTitle = new Map(sections.map((s) => [String(s.title), s]));
        const normalized = (data || []).map((s) => {
          const idStr = String(s.id);
          const local = localByTitle.get(String(s.title));
          return {
            ...s,
            id: idStr,
            persisted: true,
            content: (local && local.content) ? local.content : (s.content ?? ""),
            summary: local?.summary ?? "",
            guidance: local?.guidance ?? "",
            lastFeedback: local?.lastFeedback ?? null,
          };
        });
        setSections(normalized);

        const created = normalized.find((s) => s.title === section.title);
        if (!created) {
          throw new Error("Created section not found after persist");
        }

        const numericId = Number(created.id);
        const userPrompt = buildUserPrompt(section);
        const payload = { feedback: "generate", user_prompt: userPrompt, persist: false };

        console.debug("POST /sections/:id/refine payload (persisted):", payload);

        const res = await api.postJSON(`/sections/${numericId}/refine`, payload, token);

        console.log("generate (persisted) response:", res);

        if (res && (res.content || res)) {
          const content = typeof res === "string" ? res : res.content ?? res;
          setSections((current) =>
            current.map((s) =>
              String(s.id) === String(created.id)
                ? {
                    ...s,
                    content,
                    lastFeedback: {
                      sentiment: "generate",
                      message: "Draft generated",
                      at: new Date().toISOString(),
                    },
                    persisted: true,
                  }
                : s
            )
          );
        }
      } catch (err) {
        console.error("Persist+generate failed", err);
      } finally {
        setGeneratingSectionId(null);
      }

      return;
    }

    if (!token) {
      console.warn("No token available to request generation");
      setGeneratingSectionId(null);
      return;
    }

    try {
      const numericId = Number(sectionId);

      const userPrompt = buildUserPrompt(section);
      const payload = { feedback: "generate", user_prompt: userPrompt };

      console.debug("POST /sections/:id/refine payload (existing):", payload);

      const res = await api.postJSON(`/sections/${numericId}/refine`, payload, token);

      console.log("generate (existing) response:", res);

      if (res && (res.content || res)) {
        const content = typeof res === "string" ? res : res.content ?? res;
        setSections((current) =>
          current.map((s) =>
            String(s.id) === String(sectionId)
              ? {
                  ...s,
                  content,
                  lastFeedback: {
                    sentiment: "generate",
                    message: "Draft generated",
                    at: new Date().toISOString(),
                  },
                }
              : s
          )
        );
      }
    } catch (err) {
      console.error("Generate failed", err);
    } finally {
      setGeneratingSectionId(null);
    }
  };

  // === FEEDBACK (Looks good / Needs changes) ===
  const handleFeedback = async (sectionId, feedback) => {
    const token = localStorage.getItem("accessToken");
    const section = sections.find((s) => String(s.id) === String(sectionId));
    if (!section) return;

    const explicitMessage = (feedback.message || "").trim();
    const userPrompt = explicitMessage || buildUserPrompt(section);
    const persist = feedback.sentiment === "like";

    let numericId = Number(sectionId);
    if (!section.persisted) {
      if (!token || !projectId) {
        console.warn("No token/project to persist; saving only locally.");
        setSections((cur) =>
          cur.map((s) =>
            String(s.id) === String(sectionId)
              ? { ...s, lastFeedback: { ...feedback, at: new Date().toISOString() } }
              : s
          )
        );
        return;
      }

      try {
        const titles = sections.map((s) => s.title);
        await api.postJSON(`/projects/${projectId}/outline`, { sections: titles }, token);

        const data = await api.get(`/projects/${projectId}/sections`, token);
        const localByTitle = new Map(sections.map((s) => [String(s.title), s]));
        const normalized = (data || []).map((s) => {
          const idStr = String(s.id);
          const local = localByTitle.get(String(s.title));
          return {
            ...s,
            id: idStr,
            persisted: true,
            content: (local && local.content) ? local.content : (s.content ?? ""),
            summary: local?.summary ?? "",
            guidance: local?.guidance ?? "",
            lastFeedback: local?.lastFeedback ?? null,
          };
        });

        setSections(normalized);

        const created = normalized.find((s) => s.title === section.title);
        if (!created) {
          throw new Error("Created section not found after persist");
        }
        numericId = Number(created.id);
      } catch (err) {
        console.error("Persist+refresh before feedback failed", err);
        return;
      }
    }

    const payload = {
      feedback: feedback.sentiment,
      user_prompt: userPrompt,
      persist,
      current_content: section.content || "",
    };

    try {
      const res = await api.postJSON(`/sections/${numericId}/refine`, payload, token);
      const content = typeof res === "string" ? res : res.content ?? res;
      const version = res.version ?? null;

      setSections((cur) =>
        cur.map((s) =>
          String(s.id) === String(sectionId) || String(s.id) === String(numericId)
            ? {
                ...s,
                content,
                lastFeedback: { ...feedback, at: new Date().toISOString() },
                persisted: persist ? true : (s.persisted ?? false),
                version: version ?? s.version,
              }
            : s
        )
      );
    } catch (err) {
      console.error("Feedback submit failed", err);
    }
  };

  const handleExport = () => {
    if (typeof window === "undefined") return;

    const filename = projectId ? `workspace-${projectId}.txt` : "workspace-draft.txt";
    const exportText = sections
      .map((section, index) => {
        const heading = `${index + 1}. ${section.title}`;
        const outline = section.summary ? `Summary: ${section.summary}` : "Summary: (none)";
        const guidance = section.guidance ? `Guidance: ${section.guidance}` : "Guidance: (none)";
        const content = section.content?.trim()
          ? section.content
          : "[No content generated yet]";

        return `${heading}\n${outline}\n${guidance}\n\n${content}`;
      })
      .join("\n\n-----------------------------\n\n");

    const blob = new Blob([exportText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 🔹 Use project title if we have it, otherwise fall back
  const headerTitle =
    projectId && projectTitle
      ? projectTitle
      : projectId
      ? `Project ${projectId}`
      : "Q4 Revenue Enablement Deck";

  return (
    <section className="mx-auto w-full max-w-6xl px-6 pt-32 pb-16">
      <header className="mb-10 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-gray-500">Workspace</p>
          <h1 className="text-3xl font-semibold text-white">
            {headerTitle}
          </h1>
          <p className="text-sm text-gray-400">
            Build your outline, generate drafts, and keep refining until it is ready to export.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={handleExport}
            className="self-start rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Export current draft
          </button>
        </div>
      </header>

      <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <OutlineList
          items={sections.map((section) => ({
            id: section.id,
            title: section.title,
            summary: section.summary,
          }))}
          activeId={activeId}
          onSelect={setActiveId}
          onAddItem={handleAddSection}
        />

        <SectionEditor
          key={activeId}
          section={activeSection}
          isGenerating={generatingSectionId === activeId}
          onChange={handleSectionChange}
          onGenerate={handleGenerate}
          onFeedback={handleFeedback}
        />
      </div>
    </section>
  );
}
