import sys
import os

# ✅ ensure project root is in import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from ai_doc_builder.backend.app.workflows.graph import graph
from ai_doc_builder.backend.app.workflows.state import SectionState
from ai_doc_builder.backend.app.services.export_service import export_to_docx, export_to_pptx


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

        final_state = graph.invoke(state)

        full_content[section_title] = final_state["content"]

        print(f"✅ Completed: {section_title}\n")

    return full_content


def run_test():
    project_title = "AI in Healthcare"
    doc_type = "docx"  # ✅ change to "pptx" if needed

    outline = [
        "Introduction",
        "Challenges in Healthcare",
        "Role of AI",
        "Future Scope",
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
