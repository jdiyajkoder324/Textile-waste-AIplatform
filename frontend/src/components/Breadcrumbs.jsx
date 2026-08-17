import { Link, useLocation } from "react-router-dom";
import { ChevronRight } from "lucide-react";

const LABELS = {
  dashboard: "Overview",
  upload: "Analyze Textile",
  analysis: "Analysis",
  inventory: "Inventory",
  history: "Analysis History",
  sustainability: "Sustainability",
  "environmental-impact": "Environmental Impact",
  "circular-economy": "Circular Economy",
  "waste-scoring": "Waste Scoring",
  recommendations: "Recommendations",
  report: "Reports",
  profile: "Profile",
};

export default function Breadcrumbs() {
  const location = useLocation();
  const segments = location.pathname.split("/").filter(Boolean);

  if (segments.length === 0) return null;

  return (
    <nav className="flex items-center gap-2 font-mono text-xs text-ink-400 mb-6">
      <Link to="/dashboard" className="hover:text-fiber-teal transition-colors">
        Home
      </Link>
      {segments.map((seg, i) => {
        const path = "/" + segments.slice(0, i + 1).join("/");
        const isLast = i === segments.length - 1;
        const label = LABELS[seg] || seg;
        return (
          <span key={path} className="flex items-center gap-2">
            <ChevronRight size={12} />
            {isLast ? (
              <span className="text-ink-700">{label}</span>
            ) : (
              <Link to={path} className="hover:text-fiber-teal transition-colors">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}