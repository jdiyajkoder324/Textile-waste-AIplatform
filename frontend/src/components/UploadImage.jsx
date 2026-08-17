import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, Image as ImageIcon, X, Loader2 } from "lucide-react";

export default function UploadImage({ onUploadStart, onAnalyzed, uploadFn }) {
  const [items, setItems] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    const newItems = acceptedFiles.map((file) => ({
      id: `${file.name}-${file.size}-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      file,
      preview: URL.createObjectURL(file),
      progress: 0,
      status: "queued",
      error: null,
    }));
    setItems((prev) => [...prev, ...newItems]);
    newItems.forEach((item) => processItem(item));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const processItem = async (item) => {
    setItems((prev) => prev.map((i) => (i.id === item.id ? { ...i, status: "uploading" } : i)));
    onUploadStart?.();
    try {
      const result = await uploadFn(item.file, (pct) => {
        setItems((prev) => prev.map((i) => (i.id === item.id ? { ...i, progress: pct, status: pct >= 100 ? "analyzing" : "uploading" } : i)));
      });
      setItems((prev) => prev.map((i) => (i.id === item.id ? { ...i, status: "done", progress: 100 } : i)));
      onAnalyzed?.(result, item);
    } catch (err) {
      const message = err?.response?.data?.detail || err?.message || "Analysis failed";
      setItems((prev) => prev.map((i) => (i.id === item.id ? { ...i, status: "error", error: message } : i)));
    }
  };

  const removeItem = (id) => setItems((prev) => prev.filter((i) => i.id !== id));

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".png", ".jpg", ".jpeg", ".webp", ".bmp"] },
    multiple: true,
  });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`relative rounded-2xl border-2 border-dashed p-10 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-fiber-amber bg-fiber-amber/5" : "border-ink-900/15 hover:border-fiber-teal/50"}`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-3">
          <div className="w-14 h-14 rounded-full bg-fiber-teal/10 flex items-center justify-center">
            <UploadCloud className="w-7 h-7 text-fiber-amber" />
          </div>
          <p className="font-display text-xl text-ink-900">
            {isDragActive ? "Drop the fabric photos here" : "Drag & drop textile images"}
          </p>
          <p className="text-sm text-ink-600">or click to browse — JPG, PNG, WEBP up to 15MB, multiple files supported</p>
        </div>
      </div>

      <AnimatePresence>
        {items.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
          >
            {items.map((item) => (
              <div key={item.id} className="rounded-2xl border border-ink-900/[0.07] bg-paper-raised shadow-card p-3 relative">
                <button
                  onClick={() => removeItem(item.id)}
                  className="absolute top-2 right-2 z-10 w-6 h-6 rounded-full bg-ink-900/80 flex items-center justify-center text-white/80 hover:text-fiber-rust"
                  aria-label="Remove"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
                <div className="aspect-square rounded-xl overflow-hidden bg-ink-900/[0.04] flex items-center justify-center">
                  {item.preview ? (
                    <img src={item.preview} alt={item.file.name} className="w-full h-full object-cover" />
                  ) : (
                    <ImageIcon className="w-8 h-8 text-ink-400" />
                  )}
                </div>
                <div className="mt-2">
                  <p className="text-xs truncate text-ink-700">{item.file.name}</p>
                  {item.status !== "done" && item.status !== "error" && (
                    <div className="mt-1.5 h-1.5 w-full bg-ink-900/[0.06] rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-fiber-amber"
                        initial={{ width: 0 }}
                        animate={{ width: `${item.status === "analyzing" ? 100 : item.progress}%` }}
                        transition={{ ease: "easeOut" }}
                      />
                    </div>
                  )}
                  <div className="mt-1.5 flex items-center gap-1.5 text-[11px]">
                    {item.status === "uploading" && (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin text-fiber-amber" />
                        <span className="text-ink-600">Uploading {item.progress}%</span>
                      </>
                    )}
                    {item.status === "analyzing" && (
                      <>
                        <Loader2 className="w-3 h-3 animate-spin text-fiber-moss" />
                        <span className="text-ink-600">Running material & waste analysis…</span>
                      </>
                    )}
                    {item.status === "done" && <span className="text-fiber-moss">Analysis complete</span>}
                    {item.status === "error" && <span className="text-fiber-rust">{item.error}</span>}
                  </div>
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}