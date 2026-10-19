import { useEffect, useState } from "react";
import "./App.css";

const STATES = [
  "IDLE",
  "LISTENING",
  "THINKING",
  "EXECUTING",
  "SPEAKING",
  "PAUSED",
  "STOPPED",
];

function App() {
  const [ariaState, setAriaState] = useState("IDLE");
  const [audioLevel, setAudioLevel] = useState(0);
  const [currentTime, setCurrentTime] = useState(() => new Date());
  const [connectionStatus, setConnectionStatus] = useState("CONNECTING");
  const [controlMode, setControlMode] = useState("RUNNING");
  const [controlBusy, setControlBusy] = useState(false);
  const [controlError, setControlError] = useState("");

  useEffect(() => {
    let isMounted = true;

    const fetchAriaState = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8765/state",
          { cache: "no-store" }
        );

        if (!response.ok) {
          if (isMounted) setConnectionStatus("OFFLINE");
          return;
        }

        const data = await response.json();

        if (!isMounted) return;

        setConnectionStatus("ONLINE");
        setControlMode(String(data.control_mode || "RUNNING").trim().toUpperCase());

        const nextState = String(data.state || "")
          .trim()
          .toUpperCase();

        if (STATES.includes(nextState)) {
          setAriaState(nextState);
        }

        const level = Number(data.audio_level);

        setAudioLevel(
          Number.isFinite(level)
            ? Math.max(0, Math.min(1, level))
            : 0
        );
      } catch (error) {
        if (isMounted) setConnectionStatus("OFFLINE");
        console.error("ARIA state connection error:", error);
      }
    };

    fetchAriaState();

    const interval = setInterval(fetchAriaState, 250);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const sendControl = async (command) => {
    setControlBusy(true);
    setControlError("");

    try {
      const response = await fetch("http://127.0.0.1:8765/control", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Control request failed.");
      setControlMode(String(data.control_mode || "").toUpperCase());
    } catch {
      setControlError("Could not control Aria. Check that the Python backend is running.");
    } finally {
      setControlBusy(false);
    }
  };

  const displayedState =
    controlMode === "PAUSED" || controlMode === "STOPPED"
      ? controlMode
      : ariaState;

  const clockText = currentTime.toLocaleTimeString("en-IN", {
    hour12: false,
  });

  return (
    <main
      className={`aria-screen state-${displayedState.toLowerCase()}`}
      style={{
        "--audio-level": displayedState === "SPEAKING" ? audioLevel : 0,
      }}
    >
      <div className="space-noise" />
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <header className="aria-header">
        <div className="aria-brand">
          <span className="brand-dot" />
          <span>ARIA</span>
        </div>

        <div className="header-metrics">
          <div className="system-status">
            <span
              className={`status-dot ${
                connectionStatus === "ONLINE"
                  ? "connected"
                  : connectionStatus === "OFFLINE"
                  ? "disconnected"
                  : ""
              }`}
            />
            PYTHON LINK {connectionStatus}
          </div>

          <div className="system-clock">{clockText}</div>
        </div>
      </header>

      <aside className="hud-panel hud-panel-left">
        <div className="hud-panel-title">SYSTEM TELEMETRY</div>
        <div className="hud-panel-line" />

        <div className="hud-row">
          <span>PYTHON LINK</span>
          <strong>{connectionStatus}</strong>
        </div>

        <div className="hud-row">
          <span>CORE STATE</span>
          <strong>{displayedState}</strong>
        </div>

        <div className="hud-row">
          <span>VOICE LEVEL</span>
          <strong>{Math.round(audioLevel * 100)}%</strong>
        </div>

        <div className="hud-row">
          <span>RUNTIME</span>
          <strong>LOCAL</strong>
        </div>

        <div className="hud-footer">ARIA / SYSTEM 01</div>
      </aside>

      <aside className="hud-panel hud-panel-right">
        <div className="hud-panel-title">MODULE ACTIVITY</div>
        <div className="hud-panel-line" />

        {[
          ["LISTENING", "VOICE INPUT"],
          ["THINKING", "AI PROCESSING"],
          ["EXECUTING", "COMMAND ENGINE"],
          ["SPEAKING", "VOICE OUTPUT"],
        ].map(([state, name]) => (
          <div className="hud-module" key={state}>
            <span
              className={`module-indicator ${
                displayedState === state ? "active" : ""
              }`}
            />

            <div>
              <span className="module-name">{name}</span>
              <small>
                {displayedState === state ? state : "STANDBY"}
              </small>
            </div>
          </div>
        ))}

        <div className="hud-footer">LIVE STATE FEED</div>
      </aside>

      <section className="core-stage">
        <div className="core-label">
          ARTIFICIAL INTELLIGENCE CORE
        </div>

        <div className="aria-core">
          <div className="orbit orbit-one">
            <div className="orbit-glow" />
          </div>

          <div className="orbit orbit-two">
            <div className="orbit-glow" />
          </div>

          <div className="orbit orbit-three">
            <div className="orbit-glow" />
          </div>

          <div className="orbit orbit-four">
            <div className="orbit-glow" />
          </div>

          <div className="tech-ring tech-ring-one" />
          <div className="tech-ring tech-ring-two" />

          <div className="energy-field">
            <div className="energy-layer energy-layer-one" />
            <div className="energy-layer energy-layer-two" />
            <div className="energy-layer energy-layer-three" />
          </div>

          <div className="core-glow" />

          <div className="core-sphere">
            <div className="core-inner">
              <div className="core-light" />
              <div className="core-hotspot" />
            </div>
          </div>

          <div className="particles particles-one" />
          <div className="particles particles-two" />
          <div className="particles particles-three" />

          <div className="energy-fragments fragment-one" />
          <div className="energy-fragments fragment-two" />
          <div className="energy-fragments fragment-three" />
        </div>

        <div className="core-state">
          <span className="state-pulse" />
          <span>{displayedState}</span>
        </div>

        <p className="core-subtitle">
          {displayedState === "IDLE" && "Ready when you are."}
          {displayedState === "LISTENING" && "Listening..."}
          {displayedState === "THINKING" && "Processing intelligence..."}
          {displayedState === "EXECUTING" && "Executing command..."}
          {displayedState === "SPEAKING" && "Speaking..."}
          {displayedState === "PAUSED" && "Listening is paused."}
          {displayedState === "STOPPED" && "Aria is stopped."}
        </p>

        <div className="aria-controls" aria-label="Aria controls">
          {controlMode === "STOPPED" && (
            <button className="aria-control-button primary" disabled={controlBusy || connectionStatus !== "ONLINE"} onClick={() => sendControl("START")}>Start</button>
          )}
          {controlMode === "RUNNING" && (
            <button className="aria-control-button" disabled={controlBusy || connectionStatus !== "ONLINE"} onClick={() => sendControl("PAUSE")}>Pause</button>
          )}
          {controlMode === "PAUSED" && (
            <button className="aria-control-button primary" disabled={controlBusy || connectionStatus !== "ONLINE"} onClick={() => sendControl("RESUME")}>Resume</button>
          )}
          {controlMode !== "STOPPED" && (
            <button className="aria-control-button danger" disabled={controlBusy || connectionStatus !== "ONLINE"} onClick={() => sendControl("STOP")}>Stop</button>
          )}
        </div>
        {controlError && <p className="aria-control-error" role="alert">{controlError}</p>}
        <p className="aria-control-note">Pause and Stop take effect after the current microphone operation returns.</p>
      </section>

      <footer className="aria-footer">
        <div className="footer-line" />
        <span>ARIA INTELLIGENCE SYSTEM</span>
        <span>V1.0</span>
      </footer>
    </main>
  );
}

export default App;