import React from "react";

const STREAMLIT_URL =
  (import.meta.env.VITE_STREAMLIT_URL as string) ||
  "https://ai-threat-intel-dashboard.streamlit.app";

const StreamlitDashboard: React.FC = () => {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "#020617",
        color: "#e5e7eb",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        paddingTop: "4rem",
      }}
    >
      <h1 style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>
        AI Threat Intel Dashboard
      </h1>
      <p style={{ maxWidth: 700, textAlign: "center", opacity: 0.8 }}>
        The full backend dashboard (ThreatFox, News, AI summaries, and geo
        view) runs on Streamlit Cloud. Click the button below to open it in a
        separate tab while keeping this 3D globe view active.
      </p>

      <button
        onClick={() => window.open(STREAMLIT_URL, "_blank", "noopener,noreferrer")}
        style={{
          marginTop: "1.5rem",
          padding: "0.9rem 1.8rem",
          borderRadius: 999,
          border: "none",
          background:
            "linear-gradient(90deg, #22c55e, #16a34a)",
          color: "#020617",
          fontWeight: 600,
          fontSize: "1rem",
          cursor: "pointer",
          boxShadow: "0 10px 30px rgba(34,197,94,0.35)",
        }}
      >
        Open Full AI Threat Dashboard
      </button>

      <p style={{ marginTop: "1rem", fontSize: "0.8rem", opacity: 0.7 }}>
        URL: {STREAMLIT_URL}
      </p>
    </div>
  );
};

export default StreamlitDashboard;
