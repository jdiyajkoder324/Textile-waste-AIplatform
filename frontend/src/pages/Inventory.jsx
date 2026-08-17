import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getInventory, createWaste, updateWaste, deleteWaste, uploadWasteImage } from "../services/api";
import "./Inventory.css";
import AnalyzeBatchButton from "../components/inventory/AnalyzeBatchButton";

const FABRIC_OPTIONS = ["Cotton", "Polyester", "Denim", "Wool", "Silk", "Mixed"];
const STATUS_OPTIONS = ["Pending", "Approved", "Processed"];
const PAGE_SIZE = 8;

const emptyForm = {
  title: "",
  description: "",
  fabric_type: "Cotton",
  material: "",
  color: "",
  quantity: "",
  condition: "Clean",
  location: "",
  status: "Pending",
  image_path: "",
};

export default function Inventory() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);

  const [search, setSearch] = useState("");
  const [fabricFilter, setFabricFilter] = useState("All");
  const [statusFilter, setStatusFilter] = useState("All");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState(null);

  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState("");
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);

  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 2800);
  };

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getInventory({
        search,
        fabricType: fabricFilter,
        status: statusFilter,
        page,
        pageSize: PAGE_SIZE,
      });
      setItems(data.items || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      setError(err.message || "Failed to load inventory.");
    } finally {
      setLoading(false);
    }
  }, [search, fabricFilter, statusFilter, page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Reset to page 1 whenever filters/search change
  useEffect(() => {
    setPage(1);
  }, [search, fabricFilter, statusFilter]);

  const openCreateModal = () => {
    setEditingId(null);
    setForm(emptyForm);
    setImageFile(null);
    setImagePreview("");
    setModalOpen(true);
  };

  const openEditModal = (item) => {
    setEditingId(item.id);
    setForm({
      title: item.title || "",
      description: item.description || "",
      fabric_type: item.fabric_type || "Cotton",
      material: item.material || "",
      color: item.color || "",
      quantity: item.quantity ?? "",
      condition: item.condition || "Clean",
      location: item.location || "",
      status: item.status || "Pending",
      image_path: item.image_path || "",
    });
    setImageFile(null);
    setImagePreview(item.image_path ? `http://127.0.0.1:8000${item.image_path}` : "");
    setModalOpen(true);
  };

  const closeModal = () => setModalOpen(false);

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.title || !form.fabric_type || !form.quantity || !form.condition) {
      showToast("Title, fabric type, quantity, and condition are required.", "error");
      return;
    }

    setSaving(true);
    try {
      let imagePath = form.image_path;

      if (imageFile) {
        setUploading(true);
        imagePath = await uploadWasteImage(imageFile);
        setUploading(false);
      }

      const payload = {
        ...form,
        quantity: parseFloat(form.quantity),
        image_path: imagePath,
      };

      if (editingId) {
        await updateWaste(editingId, payload);
        showToast("Inventory item updated.");
      } else {
        await createWaste(payload);
        showToast("Inventory item added.");
      }

      setModalOpen(false);
      fetchData();
    } catch (err) {
      showToast(err.message || "Failed to save item.", "error");
    } finally {
      setSaving(false);
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await deleteWaste(id);
      showToast("Item deleted.");
      setConfirmDeleteId(null);
      fetchData();
    } catch (err) {
      showToast(err.message || "Failed to delete item.", "error");
    }
  };

  const quickStatusUpdate = async (item, newStatus) => {
    try {
      await updateWaste(item.id, { status: newStatus });
      showToast(`Marked as ${newStatus}.`);
      fetchData();
    } catch (err) {
      showToast(err.message || "Failed to update status.", "error");
    }
  };

  return (
    <div className="inv-shell">
      <aside className="inv-sidebar">
        <div>
          <div className="inv-logo">Textile<span>Intel</span></div>
          <nav className="inv-nav">
            <div className="inv-nav-item" onClick={() => navigate("/dashboard")}>Dashboard</div>
            <div className="inv-nav-item active">Inventory</div>
          </nav>
        </div>
        <div className="inv-sidebar-footer">
          <div>
            <div className="inv-user-name">{user?.name || "Account"}</div>
            <div className="inv-user-role">{user?.role || ""}</div>
          </div>
          <button className="inv-logout-btn" onClick={() => { logout(); navigate("/login"); }}>Logout</button>
        </div>
      </aside>

      <main className="inv-main">
        <header className="inv-header">
          <div>
            <h1>Inventory</h1>
            <p className="inv-subtext">{total} batch{total === 1 ? "" : "es"} logged</p>
          </div>
          <button className="inv-add-btn" onClick={openCreateModal}>+ Log New Batch</button>
        </header>

        <div className="inv-toolbar">
          <input
            className="inv-search"
            placeholder="Search by title, batch ID, or location…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select className="inv-select" value={fabricFilter} onChange={(e) => setFabricFilter(e.target.value)}>
            <option value="All">All fabrics</option>
            {FABRIC_OPTIONS.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
          <select className="inv-select" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="All">All statuses</option>
            {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        {error && <div className="inv-error-banner">{error}</div>}

        {loading ? (
          <div className="inv-loading">
            <div className="inv-spinner" />
            <span>Loading inventory…</span>
          </div>
        ) : items.length === 0 ? (
          <div className="inv-empty">
            <div className="inv-empty-icon">🧵</div>
            <h3>No batches match yet</h3>
            <p>Log your first textile waste batch to see it here.</p>
            <button className="inv-add-btn" onClick={openCreateModal}>+ Log New Batch</button>
          </div>
        ) : (
          <div className="inv-grid">
            {items.map((item) => (
              <div className="inv-card" key={item.id}>
                <div className="inv-card-image">
                  {item.image_path ? (
                    <img src={`http://127.0.0.1:8000${item.image_path}`} alt={item.title} />
                  ) : (
                    <div className="inv-card-image-placeholder">No image</div>
                  )}
                  <span className={`inv-tag status-${(item.status || "pending").toLowerCase()}`}>{item.status || "Pending"}</span>
                </div>
                <div className="inv-card-body">
                  <h4>{item.title || item.batch_id || "Untitled batch"}</h4>
                  <p className="inv-card-desc">{item.description || "No description provided."}</p>
                  <div className="inv-card-meta">
                    <span className="inv-tag">{item.fabric_type}</span>
                    <span className="inv-meta-text">{item.quantity} kg · {item.condition}</span>
                  </div>
                  {item.location && <div className="inv-meta-location">📍 {item.location}</div>}
                </div>
                <div className="inv-card-actions">
                  <select
                    className="inv-status-select"
                    value={item.status || "Pending"}
                    onChange={(e) => quickStatusUpdate(item, e.target.value)}
                  >
                    {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
                  </select>
                  <button className="inv-icon-btn" onClick={() => openEditModal(item)} title="Edit">✎</button>
                  <button className="inv-icon-btn danger" onClick={() => setConfirmDeleteId(item.id)} title="Delete">🗑</button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && totalPages > 1 && (
          <div className="inv-pagination">
            <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Prev</button>
            <span>Page {page} of {totalPages}</span>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next</button>
          </div>
        )}
      </main>

      {modalOpen && (
        <div className="inv-modal-overlay" onClick={closeModal}>
          <div className="inv-modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editingId ? "Edit Batch" : "Log New Batch"}</h2>
            <form onSubmit={handleSave}>
              <div className="inv-form-row">
                <div className="inv-field">
                  <label>Title</label>
                  <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} placeholder="e.g. Post-production denim offcuts" />
                </div>
              </div>

              <div className="inv-field">
                <label>Description</label>
                <textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} placeholder="Any notes on origin, blend, or condition" />
              </div>

              <div className="inv-form-row two">
                <div className="inv-field">
                  <label>Fabric Type</label>
                  <select value={form.fabric_type} onChange={(e) => setForm({ ...form, fabric_type: e.target.value })}>
                    {FABRIC_OPTIONS.map((f) => <option key={f} value={f}>{f}</option>)}
                  </select>
                </div>
                <div className="inv-field">
                  <label>Material</label>
                  <input value={form.material} onChange={(e) => setForm({ ...form, material: e.target.value })} placeholder="e.g. 98% cotton, 2% elastane" />
                </div>
              </div>

              <div className="inv-form-row two">
                <div className="inv-field">
                  <label>Color</label>
                  <input value={form.color} onChange={(e) => setForm({ ...form, color: e.target.value })} placeholder="e.g. Indigo" />
                </div>
                <div className="inv-field">
                  <label>Quantity (kg)</label>
                  <input type="number" step="0.1" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} placeholder="150.5" />
                </div>
              </div>

              <div className="inv-form-row two">
                <div className="inv-field">
                  <label>Condition</label>
                  <select value={form.condition} onChange={(e) => setForm({ ...form, condition: e.target.value })}>
                    <option value="Clean">Clean</option>
                    <option value="Dirty">Dirty</option>
                    <option value="Damaged">Damaged</option>
                    <option value="Mixed">Mixed</option>
                  </select>
                </div>
                <div className="inv-field">
                  <label>Location</label>
                  <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} placeholder="e.g. Warehouse B" />
                </div>
              </div>

              <div className="inv-field">
                <label>Image</label>
                <input type="file" accept="image/*" onChange={handleImageSelect} />
                {imagePreview && (
                  <div className="inv-image-preview">
                    <img src={imagePreview} alt="preview" />
                  </div>
                )}
              </div>

              <div className="inv-modal-actions">
                <button type="button" className="inv-cancel-btn" onClick={closeModal}>Cancel</button>
                <button type="submit" className="inv-save-btn" disabled={saving}>
                  {uploading ? "Uploading image…" : saving ? "Saving…" : editingId ? "Update Batch" : "Add Batch"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDeleteId && (
        <div className="inv-modal-overlay" onClick={() => setConfirmDeleteId(null)}>
          <div className="inv-modal small" onClick={(e) => e.stopPropagation()}>
            <h3>Delete this batch?</h3>
            <p>This can't be undone.</p>
            <div className="inv-modal-actions">
              <button className="inv-cancel-btn" onClick={() => setConfirmDeleteId(null)}>Cancel</button>
              <button className="inv-danger-btn" onClick={() => handleDelete(confirmDeleteId)}>Delete</button>
            </div>
          </div>
        </div>
      )}

      {toast && (
        <div className={`inv-toast ${toast.type}`}>{toast.message}</div>
      )}
    </div>
  );
}
