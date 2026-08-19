import { useState, useEffect, useCallback } from "react";
import { Users, Trash2, ShieldCheck, X } from "lucide-react";
import Breadcrumbs from "../components/Breadcrumbs";
import GlassCard from "../components/GlassCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import { useAuth } from "../context/AuthContext";
import { getAllUsers, updateUserRole, deleteUserAccount } from "../services/api";

const ROLE_STYLES = {
  Industry: "text-fiber-teal border-fiber-teal/30 bg-fiber-teal/10",
  Recycler: "text-fiber-moss border-fiber-moss/30 bg-fiber-moss/10",
  Admin: "text-fiber-amber border-fiber-amber/30 bg-fiber-amber/10",
};

export default function AdminUserManagement() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchUsers = useCallback(() => {
    setLoading(true);
    setError(null);
    getAllUsers()
      .then((res) => setUsers(res.data.items))
      .catch((err) => setError(err.response?.data?.detail || "Could not load users."))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { fetchUsers(); }, [fetchUsers]);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await updateUserRole(userId, newRole);
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, role: newRole } : u)));
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update role.");
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await deleteUserAccount(deleteTarget.id);
      setUsers((prev) => prev.filter((u) => u.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Could not delete user.");
      setDeleteTarget(null);
    }
  };

  if (currentUser && currentUser.role !== "Admin") {
    return (
      <div className="px-8 py-8 max-w-3xl mx-auto">
        <div className="p-5 rounded-xl bg-fiber-rust/10 border border-fiber-rust/20 text-fiber-rust text-sm font-body">
          Access denied. User management is restricted to Admins.
        </div>
      </div>
    );
  }

  return (
    <div className="px-8 py-8 max-w-6xl mx-auto">
      <Breadcrumbs />

      <div className="mb-8">
        <h1 className="font-display text-3xl text-ink-900 tracking-tight">User Management</h1>
        <p className="font-body text-sm text-ink-500 mt-1.5">
          {users.length} account{users.length !== 1 ? "s" : ""} on the platform.
        </p>
      </div>

      {loading && <LoadingState label="Loading users..." />}
      {!loading && error && <ErrorState message={error} onRetry={fetchUsers} />}

      {!loading && !error && users.length === 0 && (
        <EmptyState message="No users registered yet." />
      )}

      {!loading && !error && users.length > 0 && (
        <GlassCard accent="teal" className="p-0 overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-ink-900/[0.06] text-[11px] uppercase tracking-[0.14em] text-ink-400 font-body">
                <th className="px-5 py-3.5">Name</th>
                <th className="px-5 py-3.5">Email</th>
                <th className="px-5 py-3.5">Role</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-900/[0.05]">
              {users.map((u) => (
                <tr key={u.id} className="hover:bg-ink-900/[0.015] transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="w-8 h-8 rounded-full bg-fiber-teal/10 border border-fiber-teal/20 flex items-center justify-center">
                        <span className="text-xs font-display text-fiber-teal">
                          {u.name?.charAt(0)?.toUpperCase() || "U"}
                        </span>
                      </div>
                      <span className="text-sm font-body text-ink-900">{u.name}</span>
                    </div>
                  </td>
                  <td className="px-5 py-3.5 text-sm text-ink-600 font-body">{u.email}</td>
                  <td className="px-5 py-3.5">
                    <select
                      value={u.role}
                      onChange={(e) => handleRoleChange(u.id, e.target.value)}
                      disabled={u.id === currentUser.id}
                      className={`px-2.5 py-1 rounded-full border text-[11px] font-semibold uppercase tracking-wide bg-transparent
                        ${ROLE_STYLES[u.role] || ROLE_STYLES.Industry}
                        ${u.id === currentUser.id ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                    >
                      <option value="Industry">Industry</option>
                      <option value="Recycler">Recycler</option>
                      <option value="Admin">Admin</option>
                    </select>
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    {u.id === currentUser.id ? (
                      <span className="text-[11px] font-mono text-ink-300 uppercase">You</span>
                    ) : (
                      <button
                        onClick={() => setDeleteTarget(u)}
                        className="p-1.5 rounded-lg text-ink-400 hover:text-fiber-rust hover:bg-fiber-rust/10 transition-colors"
                        title="Delete account"
                      >
                        <Trash2 size={15} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </GlassCard>
      )}

      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-ink-900/60 backdrop-blur-sm px-6">
          <div className="w-full max-w-sm p-6 rounded-2xl bg-paper-raised border border-ink-900/[0.08] shadow-card">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-display text-lg text-ink-900">Delete account</h3>
              <button onClick={() => setDeleteTarget(null)} className="text-ink-400 hover:text-ink-700">
                <X size={16} />
              </button>
            </div>
            <p className="text-sm text-ink-500 font-body mb-5">
              This will permanently delete <span className="text-ink-900 font-medium">{deleteTarget.name}</span>'s account. This can't be undone.
            </p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeleteTarget(null)}
                className="px-4 py-2 rounded-lg border border-ink-900/10 text-sm text-ink-600 hover:bg-ink-900/[0.03]"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="px-4 py-2 rounded-lg bg-fiber-rust text-white text-sm font-semibold hover:bg-fiber-rust/90"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
