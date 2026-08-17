import { useState, useEffect } from "react";
import api from "../services/api";

export default function AuthedImage({ analysisId, alt = "", className = "" }) {
  const [src, setSrc] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let objectUrl;
    let cancelled = false;

    api.get(`/api/image/${analysisId}/preview`, { responseType: "blob" })
      .then((res) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(res.data);
        setSrc(objectUrl);
      })
      .catch(() => { if (!cancelled) setError(true); });

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [analysisId]);

  if (error) {
    return (
      <div className={`flex items-center justify-center bg-ink-950 text-white/30 font-mono text-xs ${className}`}>
        No image
      </div>
    );
  }

  if (!src) {
    return <div className={`animate-pulse bg-white/5 ${className}`} />;
  }

  return <img src={src} alt={alt} className={className} />;
}