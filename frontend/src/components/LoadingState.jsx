export default function LoadingState({ message = "Preparing your draft" }) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-white/10 bg-white/5 p-8 text-center text-sm text-gray-300 backdrop-blur-xl">
      <div className="flex h-12 w-12 items-center justify-center rounded-full border-4 border-blue-500/40 border-t-blue-500 animate-spin" />
      <div>
        <p className="text-base font-semibold text-white">Please hold tight</p>
        <p className="text-sm text-gray-400">{message}...</p>
      </div>
    </div>
  );
}
