import React from "react";
import { NavLink } from "react-router-dom";
import { Shirt, LayoutDashboard, UploadCloud, ScanSearch } from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/upload", label: "Upload", icon: UploadCloud },
  { to: "/analysis", label: "Analysis", icon: ScanSearch },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-30 bg-ink-900/85 backdrop-blur-md border-b border-fiber-sand/10">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-fiber-teal/20 border border-fiber-teal/30 flex items-center justify-center">
            <Shirt className="w-5 h-5 text-fiber-amber" />
          </div>
          <div>
            <p className="font-display text-lg leading-tight text-fiber-sand">Textile Waste Intelligence</p>
            <p className="text-[11px] text-fiber-sand/40 leading-tight">Material Recognition &amp; Waste Classification</p>
          </div>
        </div>

        <nav className="flex items-center gap-1">
          {links.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm transition-colors ${
                  isActive ? "bg-fiber-amber/15 text-fiber-amber" : "text-fiber-sand/60 hover:text-fiber-sand"
                }`
              }
            >
              <Icon className="w-4 h-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
      <div className="thread-divider" />
    </header>
  );
}
