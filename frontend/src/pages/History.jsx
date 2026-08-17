import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Trash2, ArrowUpDown, Inbox } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import AuthedImage from "../components/AuthedImage";
import { getMyAnalyses, deleteAnalysisById } from "../services/api";

export default function History() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [sortOrder, setSortOrder] = useState("desc");
  const [loading, setLoading] = useState(true);

  const pageSize = 10;

  const fetchHistory = useCallback(() => {
    setLoading(true);
    getMyAnalyses({ search: search || undefined, sort_order: sortOrder, page, page_size: pageSize })
      .then((res) => {
        setItems(res.data.items);
        setTotal(res.data.total);
        setTotalPages(res.data.total_pages);
      })
      .finally(() => setLoading(false));
  }, [search, sortOrder, page]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm("Delete this analysis? This can't be undone.")) return;
    await deleteAnalysisById(id);
    fetchHistory();
  };

  return (
    <div className="px-8 py-8 max-w-6xl mx-auto">
      <Breadcrumbs />

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl text-ink-900 tracking-tight">Analysis History</h1>
          <p className="font-body text-sm text-ink-600 mt-1.5">
            {total} analysis{total !== 1 ? "es" : ""} on record
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div className="relative flex-1 min-w-[240px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-400" />
          <input
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            placeholder="Search by filename..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-paper-raised border border-ink-900/[0.08]
                       text-ink-900 text-sm font-body placeholder:text-ink-400
                       focus:outline-none focus:border-fiber-teal/50 focus:shadow-card transition-all duration-200"
          />
        </div>

        <button
          onClick={() => { setSortOrder((s) => (s === "desc" ? "asc" : "desc")); setPage(1); }}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-paper-raised font-body text-sm
                     border border-ink-900/[0.08] text-ink-600 hover:text-ink-900 hover:border-ink-900/15
                     transition-all duration-200"
        >
          <ArrowUpDown size={14} />
          {sortOrder === "desc" ? "Newest first" : "Oldest first"}
        </button>
      </div>

      {loading ? (
        <div className="grid gap-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 rounded-xl bg-ink-900/[0.03] border border-ink-900/[0.05] animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center rounded-2xl bg-paper-raised border border-dashed border-ink-900/10">
          <Inbox size={32} className="text-ink-400 mb-4" strokeWidth={1.5} />
          <p className="font-display text-xl text-ink-700 mb-2">No analyses yet</p>
          <p className="font-body text-sm text-ink-400">Run your first textile analysis to see it appear here.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {items.map((a) => (
            <div
              key={a.id}
              onClick={() => navigate(`/analysis/${a.id}`)}
              className="group flex items-center gap-4 p-4 rounded-xl bg-paper-raised
                         border border-ink-900/[0.06] shadow-card
                         hover:border-fiber-teal/30 hover:shadow-card-hover hover:-translate-y-0.5
                         cursor-pointer transition-all duration-200"
            >
              <AuthedImage
                analysisId={a.id}
                className="w-16 h-16 rounded-lg object-cover shrink-0 ring-1 ring-ink-900/[0.06]"
              />

              <div className="flex-1 min-w-0">
                <p className="font-body text-sm text-ink-900 truncate">{a.filename}</p>
                <div className="flex items-center gap-3 mt-1.5">
                  {a.material && <span className="font-mono text-xs text-fiber-teal">{a.material}</span>}
                  {a.waste_category && <span className="font-mono text-xs text-ink-600">{a.waste_category}</span>}
                  <span className="font-mono text-xs text-ink-400">
                    {new Date(a.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {a.recyclability_percentage != null && (
                <div className="text-right shrink-0">
                  <p className="font-mono text-lg text-fiber-teal">{a.recyclability_percentage.toFixed(0)}%</p>
                  <p className="font-mono text-[10px] text-ink-400 uppercase tracking-wider">recyclable</p>
                </div>
              )}

              <span className={`shrink-0 px-2.5 py-1 rounded-full font-mono text-[10px] uppercase tracking-wider border ${
                a.status === "processed" || a.status === "completed"
                  ? "bg-fiber-moss/10 text-fiber-moss border-fiber-moss/20"
                  : a.status === "failed"
                  ? "bg-fiber-rust/10 text-fiber-rust border-fiber-rust/20"
                  : "bg-fiber-amber/10 text-fiber-amber border-fiber-amber/20"
              }`}>
                {a.status}
              </span>

              <button
                onClick={(e) => handleDelete(e, a.id)}
                className="shrink-0 p-2 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-fiber-rust/10 transition-all duration-200"
              >
                <Trash2 size={16} className="text-ink-400 hover:text-fiber-rust" />
              </button>
            </div>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-8">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-8 h-8 rounded-lg font-mono text-xs transition-all duration-200 ${
                p === page ? "bg-fiber-teal text-white shadow-card" : "text-ink-400 hover:text-ink-900 hover:bg-ink-900/5"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}