import React from "react";
import GlobeMap from "./GlobeMap";

// ⬅️ Put your real Streamlit dashboard URL here
const STREAMLIT_DASHBOARD_URL =
  "https://ai-threat-intel-dashboard.streamlit.app"; // change if different

// Detect if we are inside an iframe (embedded in Streamlit)
function detectEmbedMode(): boolean {
  if (typeof window === "undefined") return false;
  try {
    return window.self !== window.top; // true when inside an iframe
  } catch {
    // Some browsers can throw on cross-origin frame checks; treat as embedded.
    return true;
  }
}

const App: React.FC = () => {
  const embedMode = detectEmbedMode();

  const goToDashboard = () => {
    window.location.href = STREAMLIT_DASHBOARD_URL;
  };

  return (
    <div style={{ width: "100vw", height: "100vh", overflow: "hidden" }}>
      {/* Top nav */}
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
        {/* Label for the globe */}
        <button
          style={{
            padding: "0.3rem 0.9rem",
            borderRadius: 999,
            border: "1px solid #22c55e",
            background: "#16a34a",
            color: "#e5e7eb",
            fontSize: "0.8rem",
            cursor: "default",
          }}
        >
          Global IOC Map
        </button>

        {/* Only show this when NOT embedded (i.e., not inside Streamlit iframe) */}
        {!embedMode && (
          <button
            onClick={goToDashboard}
            style={{
              padding: "0.3rem 0.9rem",
              borderRadius: 999,
              border: "1px solid #22c55e",
              background: "#0f172a",
              color: "#e5e7eb",
              fontSize: "0.8rem",
              cursor: "pointer",
            }}
          >
            AI Threat Dashboard
          </button>
        )}
      </nav>

      {/* Always show the globe as main content */}
      <GlobeMap />
    </div>
  );
};

export default App;
