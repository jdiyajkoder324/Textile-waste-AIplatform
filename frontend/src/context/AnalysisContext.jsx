import React, { createContext, useContext, useState, useCallback } from "react";

const AnalysisContext = createContext(null);

export function AnalysisProvider({ children }) {
  const [currentAnalysis, setCurrentAnalysis] = useState(null); // FullAnalysisOut
  const [recentAnalyses, setRecentAnalyses] = useState([]); // array of FullAnalysisOut

  const addAnalysis = useCallback((result) => {
    setCurrentAnalysis(result);
    setRecentAnalyses((prev) => [result, ...prev].slice(0, 20));
  }, []);

  return (
    <AnalysisContext.Provider value={{ currentAnalysis, recentAnalyses, addAnalysis, setCurrentAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error("useAnalysis must be used within AnalysisProvider");
  return ctx;
}
