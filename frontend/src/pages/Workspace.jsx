import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import OutlineList from "../components/OutlineList.jsx";
import SectionEditor from "../components/SectionEditor.jsx";

const seedSections = [
  {
    id: "overview",
    title: "Overview",
    summary: "Set the stage for what the reader needs to know right away.",
    guidance: "Highlight the big outcome and the teams involved.",
    content: "Our Q4 revenue enablement focuses on equipping field teams with the latest messaging...",
    lastFeedback: null
  },
  {
    id: "initiatives",
    title: "Key initiatives",
    summary: "Break down the programs that drove results.",
    guidance: "List the three initiatives that moved the needle.",
    content: "1. Competitive differentiators workshop...",
    lastFeedback: null
  }
];

export default function Workspace() {
  const [sections, setSections] = useState(seedSections);
  const [activeId, setActiveId] = useState(seedSections[0]?.id ?? null);
  const [generatingSectionId, setGeneratingSectionId] = useState(null);
  const { projectId } = useParams();

  const activeSection = useMemo(
    () => sections.find((section) => section.id === activeId) ?? null,
    [sections, activeId]
  );

  // Placeholder content generator until the backend endpoint is wired up.
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
        lastFeedback: null
      }
    ]);

    setActiveId(id);
  };

  const handleSectionChange = (sectionId, updates) => {
    setSections((current) =>
      current.map((section) =>
        section.id === sectionId ? { ...section, ...updates } : section
      )
    );
  };

  const handleGenerate = async (sectionId) => {
    setGeneratingSectionId(sectionId);
    await new Promise((resolve) => setTimeout(resolve, 1100));

    setSections((current) =>
      current.map((section) => {
        if (section.id !== sectionId) {
          return section;
        }

        const content = composeDraft(section);

        return {
          ...section,
          content,
          lastFeedback: {
            sentiment: "generate",
            message: "Draft generated.",
            at: new Date().toISOString()
          }
        };
      })
    );

    setGeneratingSectionId(null);
  };

  // Simulate sending structured feedback to the refinement endpoint.
  const handleFeedback = async (sectionId, feedback) => {
    await new Promise((resolve) => setTimeout(resolve, 400));

    setSections((current) =>
      current.map((section) =>
        section.id === sectionId
          ? {
              ...section,
              lastFeedback: {
                ...feedback,
                at: new Date().toISOString()
              }
            }
          : section
      )
    );
  };

  const handleExport = () => {
    if (typeof window === "undefined") {
      return;
    }

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

  return (
    <section className="mx-auto w-full max-w-6xl px-6 pt-32 pb-16">
      <header className="mb-10 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-gray-500">Workspace</p>
          <h1 className="text-3xl font-semibold text-white">
            {projectId ? `Project ${projectId}` : "Q4 Revenue Enablement Deck"}
          </h1>
          <p className="text-sm text-gray-400">
            Build your outline, generate drafts, and keep refining until it is ready to export.
          </p>
        </div>
        <button
          type="button"
          onClick={handleExport}
          className="self-start rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Export current draft
        </button>
      </header>

      <div className="grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
        <OutlineList
          items={sections.map((section) => ({
            id: section.id,
            title: section.title,
            summary: section.summary
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
