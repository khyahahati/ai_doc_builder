from .graph import DEFAULT_GRAPH_CONFIG, graph
from .state import SectionState


def run_full_document_test():
    print("\n🔥 Running FULL DOCUMENT generation test...\n")

    # ✅ USER INPUTS
    doc_type = input("Select document type (docx / pptx): ").strip().lower()
    title = input("Enter the document title: ").strip()

    print("\nEnter outline sections one per line.")
    print("Press ENTER on empty line to finish:\n")

    outline = []
    while True:
        section = input("> ").strip()
        if section == "":
            break
        outline.append(section)

    if not outline:
        print("\n❌ No outline provided. Exiting.")
        return

    print(f"\n✅ Outline received: {outline}\n")

    full_document = {}

    # ✅ Generate content for EACH section
    for idx, section_title in enumerate(outline, start=1):
        print(f"\n📝 Generating section {idx}: {section_title}\n")

        state = SectionState(
            section_id=idx,
            section_title=section_title,
            doc_type=doc_type,
            content=None,
            raw_outline=outline,
            context_summary=f"Document Title: {title}",
        )

        final_state = graph.invoke(state, config=DEFAULT_GRAPH_CONFIG)

        full_document[section_title] = final_state["content"]

        print(f"✅ Done: {section_title}\n")

    # ✅ Display final assembled output
    print("\n✅ FULL DOCUMENT GENERATED ✅\n")
    print(f"📌 TITLE: {title}\n")
    print("=" * 50)

    for section_title, content in full_document.items():
        print(f"\n### {section_title}\n")
        print(content)
        print("\n" + "-" * 50)

    print("\n🎉 Test completed successfully!\n")


if __name__ == "__main__":
    run_full_document_test()
