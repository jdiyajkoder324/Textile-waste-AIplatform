import { useState, useEffect, useRef, useCallback } from "react";
import { Bell, CheckCheck } from "lucide-react";
import { getNotifications, markNotificationRead, markAllNotificationsRead } from "../services/api";

const PRIORITY_DOT = {
  low: "bg-ink-300",
  medium: "bg-fiber-teal",
  high: "bg-fiber-amber",
  critical: "bg-fiber-rust",
};

function timeAgo(dateStr) {
  const diffMs = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diffMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const wrapperRef = useRef(null);

  const fetchNotifications = useCallback(() => {
    setLoading(true);
    getNotifications({ limit: 20 })
      .then((res) => {
        setItems(res.data.items);
        setUnreadCount(res.data.unread_count);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60000); // poll every 60s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleToggle = () => {
    setOpen((o) => !o);
    if (!open) fetchNotifications();
  };

  const handleMarkRead = async (id) => {
    await markNotificationRead(id);
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    setUnreadCount((c) => Math.max(0, c - 1));
  };

  const handleMarkAllRead = async () => {
    await markAllNotificationsRead();
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  };

  return (
    <div className="relative" ref={wrapperRef}>
      <button
        onClick={handleToggle}
        className="relative p-2 rounded-lg text-ink-500 hover:text-ink-900 hover:bg-ink-900/[0.04] transition-colors"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-fiber-rust text-white text-[10px] font-mono font-semibold flex items-center justify-center">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute left-0 top-full mt-2 w-80 max-h-96 overflow-y-auto rounded-2xl bg-paper-raised border border-ink-900/[0.08] shadow-card z-50">
          <div className="flex items-center justify-between px-4 py-3 border-b border-ink-900/[0.06]">
            <h3 className="font-display text-sm text-ink-900">Notifications</h3>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center gap-1 text-xs text-fiber-teal hover:text-fiber-teal/70 transition-colors"
              >
                <CheckCheck size={12} /> Mark all read
              </button>
            )}
          </div>

          {loading && items.length === 0 ? (
            <div className="p-6 text-center text-xs text-ink-400 font-body">Loading...</div>
          ) : items.length === 0 ? (
            <div className="p-6 text-center text-xs text-ink-400 font-body">No notifications yet.</div>
          ) : (
            <div className="divide-y divide-ink-900/[0.05]">
              {items.map((n) => (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && handleMarkRead(n.id)}
                  className={`w-full text-left px-4 py-3 flex gap-2.5 hover:bg-ink-900/[0.02] transition-colors ${
                    n.is_read ? "" : "bg-fiber-teal/[0.03]"
                  }`}
                >
                  <span className={`mt-1.5 w-1.5 h-1.5 rounded-full shrink-0 ${PRIORITY_DOT[n.priority] || PRIORITY_DOT.medium}`} />
                  <div className="min-w-0">
                    <p className={`text-xs font-body ${n.is_read ? "text-ink-600" : "text-ink-900 font-medium"}`}>
                      {n.title}
                    </p>
                    <p className="text-[11px] text-ink-400 mt-0.5 line-clamp-2">{n.message}</p>
                    <p className="text-[10px] text-ink-300 font-mono mt-1">{timeAgo(n.created_at)}</p>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}