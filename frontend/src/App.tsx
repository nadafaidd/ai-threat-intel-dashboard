import React, { useState } from "react";
import GlobeMap from "./GlobeMap";
import StreamlitDashboard from "./StreamlitDashboard";

type Page = "globe" | "dashboard";

const App: React.FC = () => {
  const [page, setPage] = useState<Page>("globe");

  return (
    <div style={{ width: "100vw", height: "100vh", overflow: "hidden" }}>
      {/* simple top nav */}
      <nav
        style={{
          position: "absolute",
          top: 10,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 10,
          display: "flex",
          gap: "0.5rem",
          padding: "0.4rem 0.8rem",
          borderRadius: 999,
          background: "rgba(15,23,42,0.85)",
          border: "1px solid #1f2937",
          backdropFilter: "blur(10px)",
        }}
      >
        <button
          onClick={() => setPage("globe")}
          style={{
            padding: "0.3rem 0.9rem",
            borderRadius: 999,
            border: "1px solid",
            borderColor: page === "globe" ? "#22c55e" : "transparent",
            background: page === "globe" ? "#16a34a" : "#0f172a",
            color: "#e5e7eb",
            fontSize: "0.8rem",
            cursor: "pointer",
          }}
        >
          Global IOC Map
        </button>
        <button
          onClick={() => setPage("dashboard")}
          style={{
            padding: "0.3rem 0.9rem",
            borderRadius: 999,
            border: "1px solid",
            borderColor: page === "dashboard" ? "#22c55e" : "transparent",
            background: page === "dashboard" ? "#16a34a" : "#0f172a",
            color: "#e5e7eb",
            fontSize: "0.8rem",
            cursor: "pointer",
          }}
        >
          AI Threat Dashboard
        </button>
      </nav>

      {page === "globe" && <GlobeMap />}
      {page === "dashboard" && <StreamlitDashboard />}
    </div>
  );
};

export default App;
