import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { getWastes, createWaste, updateWaste, deleteWaste } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useAnalysis } from "../context/AnalysisContext";
import {
  LayoutDashboard, PlusCircle, ScanSearch, Boxes, Leaf, LogOut, Search,
  Pencil, Trash2, AlertCircle, CalendarDays, Layers, Scale, Clock, Recycle,
  Sparkles, Image as ImageIcon, PackageSearch, Shirt, BarChart3,
} from "lucide-react";

const FABRIC_STYLES = {
  Cotton: { badge: "text-fiber-teal border-fiber-teal/30 bg-fiber-teal/10", bar: "bg-fiber-teal" },
  Polyester: { badge: "text-fiber-rust border-fiber-rust/30 bg-fiber-rust/10", bar: "bg-fiber-rust" },
  Denim: { badge: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10", bar: "bg-fiber-moss" },
  Wool: { badge: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10", bar: "bg-fiber-amber" },
  Silk: { badge: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10", bar: "bg-fiber-amber" },
  Other: { badge: "text-ink-600 border-ink-900/15 bg-ink-900/5", bar: "bg-ink-400" },
};

const STATUS_STYLES = {
  Pending: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10",
  Approved: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10",
  Processed: "text-fiber-teal border-fiber-teal/30 bg-fiber-teal/10",
};

export default function Dashboard() {
  const [wastes, setWastes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [fabricFilter, setFabricFilter] = useState("All");

  const [batchId, setBatchId] = useState("");
  const [fabricType, setFabricType] = useState("Cotton");
  const [source, setSource] = useState("");
  const [quantity, setQuantity] = useState("");
  const [condition, setCondition] = useState("Clean");
  const [collectionDate, setCollectionDate] = useState("");
  const [status, setStatus] = useState("Pending");

  const [editingId, setEditingId] = useState(null);

  const navigate = useNavigate();
  const { user, token, logout } = useAuth();
  const { currentAnalysis } = useAnalysis();

  useEffect(() => {
    if (!token) {
      navigate("/login");
    } else {
      fetchWasteData();
    }
  }, [token, navigate]);

  const fetchWasteData = async () => {
    try {
      setLoading(true);
      const data = await getWastes();
      setWastes(data);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to fetch waste records. Make sure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const resetForm = () => {
    setBatchId("");
    setFabricType("Cotton");
    setSource("");
    setQuantity("");
    setCondition("Clean");
    setCollectionDate("");
    setStatus("Pending");
    setEditingId(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!batchId || !fabricType || !source || !quantity || !condition || !collectionDate) {
      setError("Please fill out all fields.");
      return;
    }

    const payload = {
      batch_id: batchId,
      fabric_type: fabricType,
      source: source,
      quantity: parseFloat(quantity),
      condition: condition,
      collection_date: collectionDate,
      image_path: "",
      status: status,
    };

    try {
      if (editingId) {
        await updateWaste(editingId, payload);
      } else {
        await createWaste(payload);
      }
      resetForm();
      fetchWasteData();
    } catch (err) {
      setError(err.message || "Failed to save record.");
    }
  };

  const handleEdit = (item) => {
    setEditingId(item.id);
    setBatchId(item.batch_id || "");
    setFabricType(item.fabric_type || "Cotton");
    setSource(item.source || "");
    setQuantity((item.quantity ?? "").toString());
    setCondition(item.condition || "Clean");
    setCollectionDate(item.collection_date || "");
    setStatus(item.status || "Pending");
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this waste record?")) {
      try {
        await deleteWaste(id);
        fetchWasteData();
      } catch (err) {
        setError("Failed to delete record.");
      }
    }
  };

  const totalBatches = wastes.length;
  const totalWeight = wastes.reduce((acc, curr) => acc + (curr.quantity || 0), 0);
  const pendingCount = wastes.filter((w) => w.status === "Pending").length;
  const recyclingStreamPct = totalBatches > 0 ? (((totalBatches - pendingCount) / totalBatches) * 100).toFixed(0) : 0;

  const fabricStats = { Cotton: 0, Polyester: 0, Denim: 0, Wool: 0, Silk: 0, Other: 0 };
  wastes.forEach((w) => {
    const type = w.fabric_type;
    if (fabricStats[type] !== undefined) {
      fabricStats[type] += w.quantity || 0;
    } else {
      fabricStats.Other += w.quantity || 0;
    }
  });

  const maxFabricWeight = Math.max(...Object.values(fabricStats), 1);

  const filteredWastes = wastes.filter((w) => {
    const haystack = `${w.batch_id || ""} ${w.source || ""} ${w.title || ""}`.toLowerCase();
    const matchesSearch = haystack.includes(search.toLowerCase());
    const matchesFabric = fabricFilter === "All" || w.fabric_type === fabricFilter;
    return matchesSearch && matchesFabric;
  });

  const getFabricStyle = (type) => FABRIC_STYLES[type] || FABRIC_STYLES.Other;
  const getStatusStyle = (s) => STATUS_STYLES[s] || STATUS_STYLES.Pending;

  const aiImage = currentAnalysis?.image_analysis;
  const aiMaterial = currentAnalysis?.material_classification;
  const aiWaste = currentAnalysis?.waste_classification;
  const aiRecommendation = currentAnalysis?.recycling_recommendation;

  const navItems = [
    { key: "dashboard", label: "Dashboard", icon: LayoutDashboard, active: true, onClick: () => {} },
    {
      key: "quicklog",
      label: "Quick Log",
      icon: PlusCircle,
      onClick: () => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }),
    },
    { key: "scan", label: "AI Material Scan", icon: ScanSearch, onClick: () => navigate("/upload") },
    ...(user?.role === "Industry" || user?.role === "Admin"
      ? [{ key: "inventory", label: "Inventory", icon: Boxes, onClick: () => navigate("/inventory") }]
      : []),
    { key: "sustainability", label: "Sustainability", icon: Leaf, onClick: () => navigate("/sustainability") },
  ];

  return (
    <div className="text-ink-900">
      {/* Page content — sidebar comes from DashboardLayout, not rendered here */}
      <div className="px-6 py-8 lg:px-10 lg:py-10">
        <header className="flex flex-wrap items-start justify-between gap-4 mb-8">
          <div>
            <h1 className="font-display text-3xl text-ink-900 tracking-tight">Intelligence Dashboard</h1>
            <p className="text-sm text-ink-500 mt-1.5">Monitor textile waste analytics and process recovery streams.</p>
          </div>
          <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-fiber-amber/10 border border-fiber-amber/20">
            <CalendarDays className="w-3.5 h-3.5 text-fiber-amber" />
            <span className="text-xs font-mono font-semibold text-fiber-amber">
              {new Date().toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
            </span>
          </div>
        </header>

        {error && (
          <div className="flex items-center gap-2.5 mb-6 px-4 py-3 rounded-xl bg-fiber-rust/10 border border-fiber-rust/25 text-fiber-rust text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {error}
          </div>
        )}

        {/* Stats Grid */}
        <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5 mb-8">
          {[
            { label: "Total Batches", value: totalBatches, icon: Layers, accent: "teal" },
            { label: "Total Weight", value: `${totalWeight.toLocaleString()} kg`, icon: Scale, accent: "moss" },
            { label: "Pending Review", value: pendingCount, icon: Clock, accent: "amber" },
            { label: "Recycling Streams", value: `${recyclingStreamPct}%`, icon: Recycle, accent: "rust" },
          ].map(({ label, value, icon: Icon, accent }) => {
            const iconClasses = {
              teal: "text-fiber-teal bg-fiber-teal/10 border-fiber-teal/20",
              moss: "text-fiber-moss bg-fiber-moss/10 border-fiber-moss/20",
              amber: "text-fiber-amber bg-fiber-amber/10 border-fiber-amber/20",
              rust: "text-fiber-rust bg-fiber-rust/10 border-fiber-rust/20",
            }[accent];
            return (
              <div key={label} className="card-panel p-5 flex items-start gap-4">
                <div className={`w-10 h-10 rounded-xl border flex items-center justify-center shrink-0 ${iconClasses}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="min-w-0">
                  <p className="text-xs uppercase tracking-wider text-ink-500">{label}</p>
                  <p className="font-mono text-xl font-semibold text-ink-900 truncate mt-0.5">{value}</p>
                </div>
              </div>
            );
          })}
        </section>

        {/* Milestone 2: latest AI analysis snapshot */}
        {currentAnalysis && (
          <section className="card-panel p-6 mb-8">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-fiber-amber" />
                <h2 className="font-display text-lg text-ink-900">Latest AI Analysis</h2>
              </div>
              {aiImage?.filename && (
                <span className="flex items-center gap-1.5 text-xs text-ink-500">
                  <ImageIcon className="w-3.5 h-3.5" />
                  {aiImage.filename}
                </span>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
              <div className="rounded-xl border border-fiber-teal/20 bg-fiber-teal/10 p-4">
                <p className="text-xs uppercase tracking-wider text-ink-500">Material Prediction</p>
                <p className="font-display text-lg text-ink-900 mt-1 truncate">{aiMaterial?.material_name || "—"}</p>
              </div>
              <div className="rounded-xl border border-fiber-moss/20 bg-fiber-moss/10 p-4">
                <p className="text-xs uppercase tracking-wider text-ink-500">Sustainability Score</p>
                <p className="font-display text-lg text-ink-900 mt-1">{aiMaterial?.sustainability_score ?? "—"}/100</p>
              </div>
              <div className="rounded-xl border border-fiber-amber/20 bg-fiber-amber/10 p-4">
                <p className="text-xs uppercase tracking-wider text-ink-500">Waste Category</p>
                <p className="font-display text-lg text-ink-900 mt-1 truncate">{aiWaste?.waste_category || "—"}</p>
              </div>
              <div
                className={`rounded-xl border p-4 ${
                  aiImage?.damage_detected || aiImage?.contamination_detected
                    ? "border-fiber-rust/20 bg-fiber-rust/10"
                    : "border-ink-900/10 bg-ink-900/[0.03]"
                }`}
              >
                <p className="text-xs uppercase tracking-wider text-ink-500">Recommended Method</p>
                <p className="font-display text-lg text-ink-900 mt-1 truncate">{aiRecommendation?.best_recycling_method || "—"}</p>
              </div>
            </div>

            {(aiImage?.damage_detected || aiImage?.contamination_detected) && (
              <div className="mt-4 flex flex-wrap gap-2">
                {aiImage?.damage_detected && (
                  <span className="text-[11px] px-2.5 py-1 rounded-md bg-fiber-rust/10 text-fiber-rust border border-fiber-rust/25">
                    Damage: {aiImage.damage_level}
                  </span>
                )}
                {aiImage?.contamination_detected && (
                  <span className="text-[11px] px-2.5 py-1 rounded-md bg-fiber-amber/10 text-fiber-amber border border-fiber-amber/25">
                    Contamination: {aiImage.contamination_percentage}%
                  </span>
                )}
              </div>
            )}
          </section>
        )}

        {/* Analytics Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-[2fr_1.2fr] gap-8 items-start">
          {/* Waste Records Panel */}
          <section className="card-panel p-6">
            <div className="flex items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-2">
                <Boxes className="w-4 h-4 text-fiber-teal" />
                <h2 className="font-display text-lg text-ink-900">Waste Batches</h2>
              </div>
              <span className="text-xs text-ink-500">Showing {filteredWastes.length} items</span>
            </div>

            <div className="flex flex-wrap gap-3 mb-5">
              <div className="relative flex-1 min-w-[200px]">
                <Search className="w-4 h-4 text-ink-400 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="Search by batch ID or source..."
                  className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 placeholder:text-ink-400 pl-9 pr-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>
              <select
                className="rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors w-40"
                value={fabricFilter}
                onChange={(e) => setFabricFilter(e.target.value)}
              >
                <option value="All">All Fabrics</option>
                <option value="Cotton">Cotton</option>
                <option value="Polyester">Polyester</option>
                <option value="Denim">Denim</option>
                <option value="Wool">Wool</option>
                <option value="Silk">Silk</option>
              </select>
            </div>

            {loading ? (
              <div className="text-center py-16 text-sm text-ink-500">Loading textile records...</div>
            ) : filteredWastes.length === 0 ? (
              <div className="flex flex-col items-center gap-3 py-16 text-center">
                <PackageSearch className="w-10 h-10 text-ink-300" />
                <p className="text-sm text-ink-500 max-w-xs">
                  No waste records found. Use the panel on the right to log your first batch!
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto -mx-2">
                <table className="w-full text-left text-sm border-collapse">
                  <thead>
                    <tr>
                      {["Batch ID", "Fabric Type", "Source", "Qty (kg)", "Condition", "Date", "Status", "Actions"].map((h) => (
                        <th key={h} className="px-3 py-3 text-xs uppercase tracking-wider text-ink-500 font-semibold border-b border-ink-900/[0.08]">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredWastes.map((item) => {
                      const fabricStyle = getFabricStyle(item.fabric_type);
                      return (
                        <tr key={item.id} className="hover:bg-ink-900/[0.02] transition-colors">
                          <td className="px-3 py-3 border-b border-ink-900/[0.06] font-semibold text-ink-900">{item.batch_id}</td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06]">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-wide ${fabricStyle.badge}`}>
                              {item.fabric_type}
                            </span>
                          </td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06] text-ink-600">{item.source}</td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06] font-mono font-semibold text-ink-900">{item.quantity}</td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06] text-ink-600">{item.condition}</td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06] text-ink-600">{item.collection_date}</td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06]">
                            <span className={`inline-flex items-center px-2.5 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-wide ${getStatusStyle(item.status)}`}>
                              {item.status || "Pending"}
                            </span>
                          </td>
                          <td className="px-3 py-3 border-b border-ink-900/[0.06]">
                            <div className="flex items-center gap-2">
                              <button
                                title="Edit Record"
                                onClick={() => handleEdit(item)}
                                className="w-8 h-8 rounded-lg border border-ink-900/10 flex items-center justify-center text-ink-500 hover:text-fiber-amber hover:border-fiber-amber/25 hover:bg-fiber-amber/10 transition-colors"
                              >
                                <Pencil className="w-3.5 h-3.5" />
                              </button>
                              <button
                                title="Delete Record"
                                onClick={() => handleDelete(item.id)}
                                className="w-8 h-8 rounded-lg border border-ink-900/10 flex items-center justify-center text-ink-500 hover:text-fiber-rust hover:border-fiber-rust/25 hover:bg-fiber-rust/10 transition-colors"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          {/* Side Panel: Chart & Form */}
          <div className="flex flex-col gap-8">
            <section className="card-panel p-6">
              <div className="flex items-center gap-2 mb-5">
                <BarChart3 className="w-4 h-4 text-fiber-amber" />
                <h2 className="font-display text-lg text-ink-900">Fabric Volume (kg)</h2>
              </div>
              <div className="flex items-end gap-3 h-36 pb-3 border-b border-ink-900/[0.08]">
                {Object.entries(fabricStats).map(([fabric, weight]) => {
                  const percent = maxFabricWeight > 0 ? (weight / maxFabricWeight) * 100 : 0;
                  const barClass = getFabricStyle(fabric).bar;
                  return (
                    <div key={fabric} className="flex-1 h-full flex flex-col items-center justify-end gap-2" title={`${fabric}: ${weight} kg`}>
                      <div
                        className={`w-full rounded-t-md min-h-[4px] ${barClass} transition-all duration-700 ease-out`}
                        style={{ height: `${percent}%` }}
                      />
                      <span className="text-[10px] font-medium text-ink-500 text-center">{fabric}</span>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="card-panel p-6">
              <div className="flex items-center gap-2 mb-5">
                <PlusCircle className="w-4 h-4 text-fiber-moss" />
                <h2 className="font-display text-lg text-ink-900">{editingId ? "Edit Batch Record" : "Log New Batch"}</h2>
              </div>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="batchId" className="text-xs text-ink-500 block mb-1.5">Batch ID</label>
                  <input
                    type="text"
                    id="batchId"
                    placeholder="e.g. TX-4821"
                    className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 placeholder:text-ink-400 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                    value={batchId}
                    onChange={(e) => setBatchId(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="fabricType" className="text-xs text-ink-500 block mb-1.5">Fabric Type</label>
                    <select
                      id="fabricType"
                      className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                      value={fabricType}
                      onChange={(e) => setFabricType(e.target.value)}
                    >
                      <option value="Cotton">Cotton</option>
                      <option value="Polyester">Polyester</option>
                      <option value="Denim">Denim</option>
                      <option value="Wool">Wool</option>
                      <option value="Silk">Silk</option>
                      <option value="Mixed">Mixed</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="condition" className="text-xs text-ink-500 block mb-1.5">Condition</label>
                    <select
                      id="condition"
                      className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                      value={condition}
                      onChange={(e) => setCondition(e.target.value)}
                    >
                      <option value="Clean">Clean</option>
                      <option value="Dirty">Dirty</option>
                      <option value="Damaged">Damaged</option>
                      <option value="Mixed">Mixed</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="quantity" className="text-xs text-ink-500 block mb-1.5">Quantity (kg)</label>
                    <input
                      type="number"
                      id="quantity"
                      step="0.1"
                      placeholder="e.g. 150.5"
                      className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 placeholder:text-ink-400 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                      value={quantity}
                      onChange={(e) => setQuantity(e.target.value)}
                    />
                  </div>
                  <div>
                    <label htmlFor="collectionDate" className="text-xs text-ink-500 block mb-1.5">Collection Date</label>
                    <input
                      type="date"
                      id="collectionDate"
                      className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                      value={collectionDate}
                      onChange={(e) => setCollectionDate(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="source" className="text-xs text-ink-500 block mb-1.5">Source Origin</label>
                  <input
                    type="text"
                    id="source"
                    placeholder="e.g. Factory A, Post-Consumer"
                    className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 placeholder:text-ink-400 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                    value={source}
                    onChange={(e) => setSource(e.target.value)}
                  />
                </div>

                {editingId && (
                  <div>
                    <label htmlFor="status" className="text-xs text-ink-500 block mb-1.5">Processing Status</label>
                    <select
                      id="status"
                      className="w-full rounded-lg bg-paper border border-ink-900/10 text-ink-900 px-3 py-2.5 text-sm focus:outline-none focus:border-fiber-teal/60 transition-colors"
                      value={status}
                      onChange={(e) => setStatus(e.target.value)}
                    >
                      <option value="Pending">Pending</option>
                      <option value="Approved">Approved</option>
                      <option value="Processed">Processed</option>
                    </select>
                  </div>
                )}

                <button
                  type="submit"
                  className="w-full rounded-lg bg-fiber-teal text-white font-semibold text-sm py-2.5 mt-2 hover:opacity-90 hover:-translate-y-0.5 transition-all"
                >
                  {editingId ? "Update Batch" : "Log Batch"}
                </button>
                {editingId && (
                  <button
                    type="button"
                    onClick={resetForm}
                    className="w-full rounded-lg border border-ink-900/10 text-ink-600 font-medium text-sm py-2.5 hover:bg-ink-900/[0.03] transition-colors"
                  >
                    Cancel Edit
                  </button>
                )}
              </form>
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}