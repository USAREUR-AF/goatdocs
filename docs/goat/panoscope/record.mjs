// Record a real panoscope session: the view, stats, legend, the WebSocket deltas
// for DURATION seconds, and a few samples per topic. Writes JSON to argv[2].
import { writeFileSync } from "node:fs";
const BASE = "http://127.0.0.1:8080";
const OUT = process.argv[2];
const DURATION = Number(process.argv[3] ?? 60);
const j = async (path, init) => { const r = await fetch(BASE + path, init); return r.ok ? r.json() : { status: r.status }; };
const params = { window_hours: 1, detail: "normal", expand: [], fold_peers: [], collapse_orgs: [], source: "all", infra: "all", test: "hide" };
const view = await j("/api/view", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(params) });
const legend = await j("/api/legend");
const statsStart = await j("/api/stats");
const t0 = Date.now();
const events = [];
await new Promise((resolve) => {
  const ws = new WebSocket("ws://127.0.0.1:8080/ws?snapshot=0");
  ws.onmessage = (m) => {
    const msg = JSON.parse(m.data);
    if (msg.type === "delta") for (const e of msg.events) events.push(e);
  };
  setTimeout(() => { ws.close(); resolve(); }, DURATION * 1000);
});
const statsEnd = await j("/api/stats");
const topics = [...new Set(events.filter((e) => e.topic).map((e) => e.topic))];
const samples = {};
for (const t of topics) samples[t] = await j(`/api/samples?topic=${encodeURIComponent(t)}&limit=3`);
writeFileSync(OUT, JSON.stringify({ recorded_at_ms: t0, duration_s: DURATION, params, view, legend, statsStart, statsEnd, events, samples }, null, 1));
console.log("events", events.length, "topics", topics.length, "view keys", Object.keys(view));
