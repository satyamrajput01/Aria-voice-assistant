import { useEffect, useState } from "react";
import "./App.css";

const STATES = [
  "IDLE",
  "LISTENING",
  "THINKING",
  "EXECUTING",
  "SPEAKING",
];

function App() {
  const [ariaState, setAriaState] = useState("IDLE");

  useEffect(() => {
    const fetchAriaState = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8765/state",
          {
            cache: "no-store",
          }
        );

        if (!response.ok) {
          return;
        }

        const data = await response.json();

        const nextState = String(data.state || "")
          .trim()
          .toUpperCase();

        if (STATES.includes(nextState)) {
          setAriaState(nextState);
        }
      } catch (error) {
        console.error(
          "ARIA state connection error:",
          error
        );
      }
    };

    // Get the state immediately when the UI loads
    fetchAriaState();

    // Keep React synchronized with Python
    const interval = setInterval(
      fetchAriaState,
      100
    );

    return () => {
      clearInterval(interval);
    };
  }, []);

  return (
    <main
      className={`aria-screen state-${ariaState.toLowerCase()}`}
    >
      <div className="space-noise" />

      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      {/* ==================================================
          HEADER
          ================================================== */}

      <header className="aria-header">
        <div className="aria-brand">
          <span className="brand-dot" />
          <span>ARIA</span>
        </div>

        <div className="system-status">
          <span className="status-dot" />
          SYSTEM ONLINE
        </div>
      </header>

      {/* ==================================================
          CORE STAGE
          ================================================== */}

      <section className="core-stage">
        <div className="core-label">
          ARTIFICIAL INTELLIGENCE CORE
        </div>

        <div className="aria-core">

          {/* ==================================================
              ORBIT 1
              ================================================== */}

          <div className="orbit orbit-one">
            <div className="orbit-glow" />
          </div>

          {/* ==================================================
              ORBIT 2
              ================================================== */}

          <div className="orbit orbit-two">
            <div className="orbit-glow" />
          </div>

          {/* ==================================================
              ORBIT 3
              ================================================== */}

          <div className="orbit orbit-three">
            <div className="orbit-glow" />
          </div>

          {/* ==================================================
              ORBIT 4
              ================================================== */}

          <div className="orbit orbit-four">
            <div className="orbit-glow" />
          </div>

          {/* ==================================================
              TECHNOLOGY RINGS
              ================================================== */}

          <div className="tech-ring tech-ring-one" />

          <div className="tech-ring tech-ring-two" />

          {/* ==================================================
              ENERGY FIELD
              ================================================== */}

          <div className="energy-field">
            <div className="energy-layer energy-layer-one" />

            <div className="energy-layer energy-layer-two" />

            <div className="energy-layer energy-layer-three" />
          </div>

          {/* ==================================================
              CORE GLOW
              ================================================== */}

          <div className="core-glow" />

          {/* ==================================================
              MAIN CORE SPHERE
              ================================================== */}

          <div className="core-sphere">
            <div className="core-inner">

              <div className="core-light" />

              <div className="core-hotspot" />

            </div>
          </div>

          {/* ==================================================
              PARTICLES
              ================================================== */}

          <div className="particles particles-one" />

          <div className="particles particles-two" />

          <div className="particles particles-three" />

          {/* ==================================================
              ENERGY FRAGMENTS
              ================================================== */}

          <div className="energy-fragments fragment-one" />

          <div className="energy-fragments fragment-two" />

          <div className="energy-fragments fragment-three" />

        </div>

        {/* ==================================================
            CURRENT ARIA STATE
            ================================================== */}

        <div className="core-state">
          <span className="state-pulse" />

          <span>
            {ariaState}
          </span>
        </div>

        {/* ==================================================
            STATE DESCRIPTION
            ================================================== */}

        <p className="core-subtitle">

          {ariaState === "IDLE" &&
            "Ready when you are."}

          {ariaState === "LISTENING" &&
            "Listening..."}

          {ariaState === "THINKING" &&
            "Processing intelligence..."}

          {ariaState === "EXECUTING" &&
            "Executing command..."}

          {ariaState === "SPEAKING" &&
            "Speaking..."}

        </p>
      </section>

      {/* ==================================================
          FOOTER
          ================================================== */}

      <footer className="aria-footer">

        <div className="footer-line" />

        <span>
          ARIA INTELLIGENCE SYSTEM
        </span>

        <span>
          V1.0
        </span>

      </footer>

    </main>
  );
}

export default App;