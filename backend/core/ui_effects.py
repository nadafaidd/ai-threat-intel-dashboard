import streamlit as st

def add_fireflies_background():
    """Subtle fireflies behind Streamlit content (no blocking)."""
    st.markdown(
        """
        <style>
        /* Make Streamlit app background transparent so we can see the fireflies */
        .stApp {
            background: transparent !important;
        }

        /* Ensure main content & sidebar are above the fireflies */
        .stMain, .stSidebar, [data-testid="stHeader"], [data-testid="stToolbar"] {
            position: relative;
            z-index: 2;
        }

        /* Fireflies layer sits behind content but above page background */
        .fireflies-layer {
            position: fixed;
            inset: 0;
            overflow: hidden;
            pointer-events: none;      /* don't block clicks */
            z-index: 1;                /* below content, above body background */
        }

        .fireflies-layer span {
            position: absolute;
            width: 4px;
            height: 4px;
            border-radius: 999px;
            background: rgba(0, 180, 255, 0.6);
            box-shadow: 0 0 8px rgba(0, 180, 255, 0.9);
            animation: float-firefly 18s linear infinite,
                       flicker 2.4s ease-in-out infinite;
        }

        @keyframes float-firefly {
            0%   { transform: translate3d(0, 0, 0); }
            100% { transform: translate3d(0, -120vh, 0); }
        }

        @keyframes flicker {
            0%, 100% { opacity: 0.1; }
            50%      { opacity: 1;   }
        }

        /* Different positions / speeds so they don't move together */
        .fireflies-layer span:nth-child(1)  { left: 10%; bottom: -10%; animation-duration: 22s, 2.2s; animation-delay: 0s,   0.3s; }
        .fireflies-layer span:nth-child(2)  { left: 25%; bottom: -12%; animation-duration: 18s, 2.8s; animation-delay: 2s,   0.1s; }
        .fireflies-layer span:nth-child(3)  { left: 40%; bottom: -15%; animation-duration: 26s, 2.0s; animation-delay: 4s,   0.5s; }
        .fireflies-layer span:nth-child(4)  { left: 55%; bottom: -18%; animation-duration: 20s, 2.6s; animation-delay: 1s,   0.0s; }
        .fireflies-layer span:nth-child(5)  { left: 70%; bottom: -20%; animation-duration: 24s, 2.1s; animation-delay: 3s,   0.7s; }
        .fireflies-layer span:nth-child(6)  { left: 85%; bottom: -22%; animation-duration: 28s, 2.7s; animation-delay: 6s,   0.2s; }
        .fireflies-layer span:nth-child(7)  { left: 15%; bottom: -25%; animation-duration: 30s, 2.3s; animation-delay: 5s,   0.4s; }
        .fireflies-layer span:nth-child(8)  { left: 32%; bottom: -18%; animation-duration: 21s, 2.9s; animation-delay: 7s,   0.6s; }
        .fireflies-layer span:nth-child(9)  { left: 48%; bottom: -16%; animation-duration: 19s, 2.5s; animation-delay: 3.5s, 0.1s; }
        .fireflies-layer span:nth-child(10) { left: 63%; bottom: -14%; animation-duration: 23s, 2.2s; animation-delay: 1.5s, 0.8s; }
        .fireflies-layer span:nth-child(11) { left: 78%; bottom: -19%; animation-duration: 27s, 2.6s; animation-delay: 4.5s, 0.3s; }
        .fireflies-layer span:nth-child(12) { left: 5%;  bottom: -21%; animation-duration: 25s, 2.4s; animation-delay: 8s,   0.6s; }
        .fireflies-layer span:nth-child(13) { left: 20%; bottom: -23%; animation-duration: 29s, 2.1s; animation-delay: 2.8s, 0.2s; }
        .fireflies-layer span:nth-child(14) { left: 37%; bottom: -17%; animation-duration: 17s, 2.7s; animation-delay: 6.2s, 0.4s; }
        .fireflies-layer span:nth-child(15) { left: 52%; bottom: -24%; animation-duration: 31s, 2.3s; animation-delay: 1.2s, 0.9s; }
        .fireflies-layer span:nth-child(16) { left: 67%; bottom: -26%; animation-duration: 20s, 2.8s; animation-delay: 3.8s, 0.5s; }
        .fireflies-layer span:nth-child(17) { left: 82%; bottom: -15%; animation-duration: 22s, 2.2s; animation-delay: 5.6s, 0.1s; }
        .fireflies-layer span:nth-child(18) { left: 92%; bottom: -19%; animation-duration: 26s, 2.5s; animation-delay: 7.1s, 0.7s; }
        .fireflies-layer span:nth-child(19) { left: 30%; bottom: -27%; animation-duration: 24s, 2.9s; animation-delay: 0.9s, 0.3s; }
        .fireflies-layer span:nth-child(20) { left: 60%; bottom: -29%; animation-duration: 28s, 2.0s; animation-delay: 4.9s, 0.6s; }
        </style>

        <div class="fireflies-layer">
            <span></span><span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span><span></span>
        </div>
        """,
        unsafe_allow_html=True,
    )
