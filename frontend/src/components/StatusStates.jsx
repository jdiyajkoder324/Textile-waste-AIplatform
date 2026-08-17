import React from "react";
import { Loader2, AlertTriangle, Inbox } from "lucide-react";

export function LoadingState({ label = "Loading sustainability data..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4">
      <Loader2 className="w-9 h-9 text-fiber-teal animate-spin" />
      <p className="text-sm text-ink-500 font-body">{label}</p>
    </div>
  );
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
      <div className="h-14 w-14 rounded-full bg-fiber-rust/10 border border-fiber-rust/20 flex items-center justify-center">
        <AlertTriangle className="w-6 h-6 text-fiber-rust" />
      </div>
      <p className="text-sm text-fiber-rust max-w-sm font-body">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 rounded-lg bg-fiber-rust/10 border border-fiber-rust/25 text-fiber-rust text-sm hover:bg-fiber-rust/15 transition"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message = "No data available yet." }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="h-14 w-14 rounded-full bg-ink-900/[0.03] border border-ink-900/10 flex items-center justify-center">
        <Inbox className="w-6 h-6 text-ink-400" />
      </div>
      <p className="text-sm text-ink-500 max-w-sm font-body">{message}</p>
    </div>
  );
}