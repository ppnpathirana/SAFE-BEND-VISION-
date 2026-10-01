import { useState, useEffect, useRef } from "react";
import "./App.css";

// Change to your Pi's IP address if needed
const API = "http://raspberrypi.local:5000";

const STATUS_CONFIG = {
  clear:   { label: "CLEAR",          color: "#22c55e", bg: "#052e16", border: "#166534" },
  far:     { label: "VEHICLE / FAR",  color: "#eab308", bg: "#1c1500", border: "#854d0e" },
  close:   { label: "DANGER / CLOSE", color: "#ef4444", bg: "#1c0000", border: "#991b1b" },
  unknown: { label: "NO SIGNAL",      color: "#6b7280", bg: "#111827", border: "#374151" },
};

function zoneCfg(z) {
  return STATUS_CONFIG[z] ?? STATUS_CONFIG.unknown;
}

function SidePanel({ label, side, data, streamUrl }) {
  const cfg = zoneCfg(data?.status);
  return (
    <div className="side-panel" style={{ borderColor: cfg.border, background: cfg.bg }}>
      <div className="side-header">
        <div className="side-header-left">
          <span className="dot" style={{ background: cfg.color, boxShadow: `0 0 6px ${cfg.color}88` }} />
          <span className="side-label">CAM {side.toUpperCase()} — {label}</span>
        </div>
        <span className="status-badge" style={{ color: cfg.color, borderColor: cfg.border }}>
          {cfg.label}
        </span>
      </div>
      <div className="stream-container">
        <img src={streamUrl} alt={`Camera ${label}`} className="stream-img"
          onError={e => { e.target.style.display = "none"; }} />
        <div className="rec-tag">
          <span className="rec-dot" />REC
        </div>
        <div className="cam-tag">640×480 · YOLOv8n</div>
      </div>
      <div className="metrics">
        {[
          ["Vehicles",   data?.vehicle_count ?? 0],
          ["Confidence", data?.confidence ? `${(data.confidence * 100).toFixed(0)}%` : "—"],
          ["Risk",       (data?.status ?? "—").toUpperCase()],
        ].map(([l, v]) => (
          <div key={l} className="metric">
            <span className="metric-label">{l}</span>
            <span className="metric-value" style={{ color: cfg.color }}>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function EventLog({ events }) {
  return (
    <div className="event-log">
      <p className="log-title">Event Log</p>
      <div className="log-list">
        {events.length === 0
          ? <p className="log-empty">No events yet</p>
          : events.map((e, i) => (
              <div key={i} className="log-entry" style={{ color: zoneCfg(e.status).color }}>
                <span className="log-time">{e.time}</span>
                <span>CAM {e.side} — {e.status.toUpperCase()}</span>
                {e.count > 0 && <span className="log-count">{e.count} vehicle{e.count > 1 ? "s" : ""}</span>}
              </div>
            ))}
      </div>
    </div>
  );
}

export default function App() {
  const [status, setStatus]       = useState(null);
  const [events, setEvents]       = useState([]);
  const [connected, setConnected] = useState(false);
  const prevRef = useRef({ a: "clear", b: "clear" });

  useEffect(() => {
    const poll = async () => {
      try {
        const res  = await fetch(`${API}/api/status`);
        const data = await res.json();
        setStatus(data);
        setConnected(true);

        const prev = prevRef.current;
        const now  = new Date().toLocaleTimeString();
        const ne   = [];

        if (data.side_a.status !== prev.a) {
          ne.push({ time: now, side: "A", status: data.side_a.status, count: data.side_a.vehicle_count });
          prev.a = data.side_a.status;
        }
        if (data.side_b.status !== prev.b) {
          ne.push({ time: now, side: "B", status: data.side_b.status, count: data.side_b.vehicle_count });
          prev.b = data.side_b.status;
        }
        if (ne.length) setEvents(ev => [...ne.reverse(), ...ev].slice(0, 50));
      } catch {
        setConnected(false);
      }
    };

    poll();
    const id = setInterval(poll, 500);
    return () => clearInterval(id);
  }, []);

  const overall = status?.alert
    ? (status.side_a.status === "close" || status.side_b.status === "close" ? "close" : "far")
    : "clear";
  const hdrCfg = zoneCfg(overall);

  return (
    <div className="app">
      <header className="app-header" style={{ borderBottomColor: `${hdrCfg.color}33` }}>
        <div className="header-left">
          <div className="logo-box" style={{ borderColor: `${hdrCfg.color}44`, background: `${hdrCfg.color}11` }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke={hdrCfg.color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 6l5 5-5 5"/><path d="M23 6l-5 5 5 5"/>
              <circle cx="12" cy="11" r="3"/><line x1="12" y1="2" x2="12" y2="8"/>
            </svg>
          </div>
          <div>
            <h1>SAFE BEND VISION</h1>
            <p className="subtitle">AI-POWERED BLIND CURVE DETECTION · RASPBERRY PI 5</p>
          </div>
        </div>
        <div className="header-right">
          <div className="zone-pill" style={{ background: hdrCfg.bg, borderColor: `${hdrCfg.color}44` }}>
            <span className="zone-dot" style={{
              background: hdrCfg.color,
              boxShadow: `0 0 8px ${hdrCfg.color}`,
              animation: overall !== "clear" ? "blink 1s infinite" : "none"
            }} />
            <span style={{ color: hdrCfg.color, fontWeight: 700, letterSpacing: ".1em", fontSize: ".65rem" }}>
              {hdrCfg.label}
            </span>
          </div>
          <div className="conn-status">
            <span className="conn-dot" style={{ background: connected ? "#22c55e" : "#ef4444" }} />
            <span style={{ color: connected ? "#22c55e" : "#ef4444" }}>
              {connected ? "LIVE" : "OFFLINE"}
            </span>
          </div>
        </div>
      </header>

      {status?.alert && (
        <div className="alert-bar">
          ALERT — VEHICLE DETECTED — WARNING OUTPUT ACTIVE
        </div>
      )}

      <main className="main-grid">
        <SidePanel label="SIDE A" side="a" data={status?.side_a} streamUrl={`${API}/api/stream/a`} />
        <SidePanel label="SIDE B" side="b" data={status?.side_b} streamUrl={`${API}/api/stream/b`} />
      </main>

      <EventLog events={events} />

      <footer className="app-footer">
        Safe Bend Vision · v1.0.0 · P. Pathirana — SUSL · GPIO BCM A=17,27,22 · B=5,6,13
      </footer>
    </div>
  );
}
