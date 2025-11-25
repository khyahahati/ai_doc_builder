from .export_service import export_to_docx, export_to_pptx
from ..workflows.graph import DEFAULT_GRAPH_CONFIG, graph
from ..workflows.state import SectionState


def generate_full_document(project_title: str, doc_type: str, outline: list):
    full_content = {}

    print(f"\n🔥 Generating document content for: {project_title}\n")

    for idx, section_title in enumerate(outline, start=1):
        print(f"📝 Generating section {idx}: {section_title}...")

        state = SectionState(
            section_id=idx,
            section_title=section_title,
            doc_type=doc_type,
            content=None,
            raw_outline=outline,
            context_summary=f"Document Title: {project_title}"
        )

        final_state = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)

        full_content[section_title] = final_state["content"]

        print(f"✅ Completed: {section_title}\n")

    return full_content


def run_test():
    project_title = input("Enter Project Title: ") 
    doc_type = input("Enter Document Type (docx or pptx): ")

    outline = [
        "Introduction",
        "Problem Statement",
        "Proposed Solution",
        "Implementation Plan",
        "Conclusion"
    ]

    # ✅ first generate content using workflow
    sections = generate_full_document(project_title, doc_type, outline)

    # ✅ then export using export_service
    docx_path = export_to_docx(project_title, sections)
    pptx_path = export_to_pptx(project_title, sections)

    print("\n✅ EXPORT COMPLETE ✅")
    print(f"📄 DOCX saved at: {docx_path}")
    print(f"📊 PPTX saved at: {pptx_path}\n")


if __name__ == "__main__":
    run_test()
