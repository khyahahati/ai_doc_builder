export default function OutlineList({
  items = [],
  activeId,
  onSelect,
  onAddItem
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-white">Outline</h2>
          <p className="text-xs text-gray-400">Arrange sections to guide every draft.</p>
        </div>
        <button
          type="button"
          onClick={onAddItem}
          className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-500"
        >
          Add section
        </button>
      </div>

      <ul className="mt-5 flex flex-col gap-2">
        {items.length === 0 && (
          <li className="rounded-xl border border-dashed border-white/10 bg-black/10 px-4 py-6 text-center text-sm text-gray-400">
            No sections yet. Add one to start outlining.
          </li>
        )}

        {items.map((item) => {
          const isActive = item.id === activeId;

          return (
            <li key={item.id}>
              <button
                type="button"
                onClick={() => onSelect?.(item.id)}
                className={`w-full rounded-xl border px-4 py-3 text-left transition ${
                  isActive
                    ? "border-blue-500 bg-blue-600/40 text-white shadow-[0_10px_30px_rgba(59,130,246,0.2)]"
                    : "border-white/10 bg-white/5 text-gray-200 hover:bg-white/10"
                }`}
              >
                <p className="text-sm font-semibold">{item.title}</p>
                <p className="text-xs text-gray-400">
                  {item.summary?.trim() ? item.summary : "Add summary details"}
                </p>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
