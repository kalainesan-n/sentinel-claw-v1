from flask import Flask, request, jsonify, render_template_string
import subprocess, re, datetime

app = Flask(__name__)

BLOCKED_PATTERNS = [
    ".env", "password", "secret", "api_key", "token",
    "ignore.*rules", "bypass", "unrestricted", "forget.*instructions",
    "all in", "entire portfolio", "pump", "10000", "500000",
    "leverage", "margin", "/etc/", "sudo", "rm -rf", "curl", "wget",
    "cat.*file", "read.*file", "access.*file"
]

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>SENTINEL CLAW — AI Trading</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
:root {
  --bg:        #020408;
  --surface:   #060d14;
  --panel:     #0a1520;
  --border:    #0f2535;
  --accent:    #00d4ff;
  --accent2:   #ff6b35;
  --bull:      #00e676;
  --bear:      #ff1744;
  --warn:      #ffab00;
  --text:      #c8d8e8;
  --muted:     #3a5068;
  --glow:      rgba(0,212,255,0.15);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Grid background */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
  z-index: 0;
}

/* Scanline overlay */
body::after {
  content: '';
  position: fixed;
  inset: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0,0,0,0.03) 2px,
    rgba(0,0,0,0.03) 4px
  );
  pointer-events: none;
  z-index: 0;
}

.wrapper { position: relative; z-index: 1; }

/* ── HEADER ── */
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 36px;
  border-bottom: 1px solid var(--border);
  background: rgba(6,13,20,0.95);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--accent), #0057ff);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px;
  box-shadow: 0 0 20px rgba(0,212,255,0.4);
  animation: pulse-logo 3s ease-in-out infinite;
}

@keyframes pulse-logo {
  0%,100% { box-shadow: 0 0 20px rgba(0,212,255,0.4); }
  50%      { box-shadow: 0 0 35px rgba(0,212,255,0.7); }
}

.logo-text { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; letter-spacing: 3px; color: #fff; }
.logo-sub  { font-family: 'Share Tech Mono', monospace; font-size: 0.65rem; color: var(--muted); letter-spacing: 2px; margin-top: -4px; }

.header-right { display: flex; align-items: center; gap: 20px; }

.status-dot {
  display: flex; align-items: center; gap: 8px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem; color: var(--bull);
}

.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--bull);
  box-shadow: 0 0 8px var(--bull);
  animation: blink 1.5s ease-in-out infinite;
}

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.clock {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.75rem; color: var(--muted);
}

/* ── MAIN LAYOUT ── */
.main {
  display: grid;
  grid-template-columns: 340px 1fr;
  grid-template-rows: auto 1fr;
  gap: 0;
  min-height: calc(100vh - 61px);
}

/* ── SIDEBAR ── */
.sidebar {
  border-right: 1px solid var(--border);
  background: var(--surface);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 3px;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 12px;
}

/* Stats grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
}

.stat-card.total::before  { background: var(--accent); }
.stat-card.allow::before  { background: var(--bull); }
.stat-card.block::before  { background: var(--bear); }
.stat-card.rate::before   { background: var(--warn); }

.stat-num {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.2rem;
  line-height: 1;
  color: #fff;
}

.stat-card.allow .stat-num { color: var(--bull); }
.stat-card.block .stat-num { color: var(--bear); }
.stat-card.rate  .stat-num { color: var(--warn); }

.stat-label {
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Watchlist */
.watchlist { display: flex; flex-direction: column; gap: 6px; }

.stock-chip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.85rem;
}

.stock-chip:hover {
  border-color: var(--accent);
  background: rgba(0,212,255,0.05);
  transform: translateX(4px);
}

.stock-chip .sym { color: #fff; font-weight: bold; }
.stock-chip .tag {
  font-size: 0.65rem;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(0,212,255,0.1);
  color: var(--accent);
  border: 1px solid rgba(0,212,255,0.2);
}

/* Auto trader */
.auto-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
}

.auto-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.auto-title { font-size: 0.85rem; font-weight: 500; color: #fff; }

.toggle {
  width: 44px; height: 24px;
  background: var(--border);
  border-radius: 12px;
  cursor: pointer;
  position: relative;
  transition: background 0.3s;
  border: none;
}

.toggle.on { background: var(--bull); }

.toggle::after {
  content: '';
  position: absolute;
  top: 3px; left: 3px;
  width: 18px; height: 18px;
  background: #fff;
  border-radius: 50%;
  transition: transform 0.3s;
}

.toggle.on::after { transform: translateX(20px); }

.auto-status {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.7rem;
  color: var(--muted);
}

.auto-status.running { color: var(--bull); }

.progress-bar {
  height: 3px;
  background: var(--border);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
  display: none;
}

.progress-bar.active { display: block; }

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--bull));
  border-radius: 2px;
  width: 0%;
  transition: width 0.3s;
}

/* ── MAIN CONTENT ── */
.content {
  display: flex;
  flex-direction: column;
}

/* Trade input */
.trade-panel {
  padding: 24px 28px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.input-label {
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 3px;
  color: var(--muted);
  margin-bottom: 10px;
  text-transform: uppercase;
}

.input-row {
  display: flex;
  gap: 10px;
}

.trade-input {
  flex: 1;
  background: var(--panel);
  border: 1px solid var(--border);
  color: #fff;
  padding: 14px 18px;
  border-radius: 10px;
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.9rem;
  transition: all 0.2s;
  outline: none;
}

.trade-input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(0,212,255,0.08), inset 0 0 20px rgba(0,212,255,0.03);
}

.trade-input::placeholder { color: var(--muted); }

.btn-analyze {
  background: linear-gradient(135deg, var(--accent), #0057ff);
  color: #000;
  border: none;
  padding: 14px 28px;
  border-radius: 10px;
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.1rem;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-analyze:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,212,255,0.35);
}

.btn-analyze:disabled {
  background: var(--border);
  color: var(--muted);
  transform: none;
  box-shadow: none;
  cursor: not-allowed;
}

/* ── DEBATE ARENA ── */
.arena {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr auto;
  gap: 0;
}

.bull-panel, .bear-panel {
  padding: 24px;
  border-bottom: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}

.bull-panel {
  border-right: 1px solid var(--border);
  background: linear-gradient(160deg, rgba(0,230,118,0.03) 0%, transparent 60%);
}

.bear-panel {
  background: linear-gradient(160deg, rgba(255,23,68,0.03) 0%, transparent 60%);
}

.bull-panel::before {
  content: '🐂';
  position: absolute;
  right: 16px; top: 16px;
  font-size: 3rem;
  opacity: 0.06;
  pointer-events: none;
}

.bear-panel::before {
  content: '🐻';
  position: absolute;
  right: 16px; top: 16px;
  font-size: 3rem;
  opacity: 0.06;
  pointer-events: none;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.panel-badge {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 0.95rem;
  letter-spacing: 3px;
  padding: 4px 14px;
  border-radius: 4px;
}

.bull-badge { background: rgba(0,230,118,0.12); color: var(--bull); border: 1px solid rgba(0,230,118,0.2); }
.bear-badge { background: rgba(255,23,68,0.12);  color: var(--bear); border: 1px solid rgba(255,23,68,0.2); }
.ward-badge { background: rgba(0,212,255,0.12);  color: var(--accent); border: 1px solid rgba(0,212,255,0.2); }

.panel-content {
  font-size: 0.85rem;
  line-height: 1.75;
  color: var(--text);
  min-height: 120px;
}

.panel-content.empty { color: var(--muted); font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; }

/* Warden full-width */
.warden-panel {
  grid-column: 1 / -1;
  padding: 20px 28px;
  background: var(--surface);
  display: flex;
  align-items: center;
  gap: 24px;
  border-top: 2px solid var(--border);
}

.warden-left {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
}

.verdict-box {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2rem;
  letter-spacing: 4px;
  padding: 8px 24px;
  border-radius: 8px;
  transition: all 0.4s;
  min-width: 130px;
  text-align: center;
}

.verdict-box.allow {
  background: rgba(0,230,118,0.12);
  color: var(--bull);
  border: 1px solid rgba(0,230,118,0.3);
  box-shadow: 0 0 30px rgba(0,230,118,0.15);
}

.verdict-box.block {
  background: rgba(255,23,68,0.12);
  color: var(--bear);
  border: 1px solid rgba(255,23,68,0.3);
  box-shadow: 0 0 30px rgba(255,23,68,0.15);
}

.verdict-box.instant {
  background: rgba(255,171,0,0.12);
  color: var(--warn);
  border: 1px solid rgba(255,171,0,0.3);
  box-shadow: 0 0 30px rgba(255,171,0,0.15);
}

.verdict-box.idle {
  background: var(--panel);
  color: var(--muted);
  border: 1px solid var(--border);
}

.verdict-reason {
  font-size: 0.85rem;
  color: var(--text);
  flex: 1;
}

.verdict-reason span { color: var(--muted); font-size: 0.75rem; display: block; margin-bottom: 3px; font-family: 'Share Tech Mono', monospace; letter-spacing: 1px; }

/* ── LOG PANEL ── */
.log-panel {
  border-top: 1px solid var(--border);
  background: var(--bg);
  padding: 16px 24px;
  max-height: 160px;
  overflow-y: auto;
}

.log-panel::-webkit-scrollbar { width: 4px; }
.log-panel::-webkit-scrollbar-track { background: transparent; }
.log-panel::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.log-entry {
  display: flex;
  gap: 12px;
  padding: 5px 0;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.72rem;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:none} }

.log-time { color: var(--muted); white-space: nowrap; }
.log-msg  { color: var(--text); }
.log-msg.ok    { color: var(--bull); }
.log-msg.err   { color: var(--bear); }
.log-msg.warn  { color: var(--warn); }
.log-msg.info  { color: var(--accent); }

/* Loader */
.loader {
  display: inline-flex;
  gap: 4px;
  align-items: center;
}

.loader span {
  width: 5px; height: 5px;
  border-radius: 50%;
  background: var(--accent);
  animation: bounce 1s ease-in-out infinite;
}

.loader span:nth-child(2) { animation-delay: 0.15s; background: var(--bull); }
.loader span:nth-child(3) { animation-delay: 0.3s;  background: var(--accent2); }

@keyframes bounce {
  0%,80%,100%{transform:scale(0.6);opacity:0.4}
  40%{transform:scale(1);opacity:1}
}

/* Responsive */
@media(max-width: 900px) {
  .main { grid-template-columns: 1fr; }
  .sidebar { border-right: none; border-bottom: 1px solid var(--border); }
  .arena { grid-template-columns: 1fr; }
  .bull-panel { border-right: none; }
}
</style>
</head>
<body>
<div class="wrapper">

<!-- HEADER -->
<header>
  <div class="logo">
    <div class="logo-icon">🦞</div>
    <div>
      <div class="logo-text">SENTINEL CLAW</div>
      <div class="logo-sub">AI TRADING SYSTEM · OPENCLAW + OLLAMA</div>
    </div>
  </div>
  <div class="header-right">
    <div class="status-dot"><div class="dot"></div>GATEWAY LIVE</div>
    <div class="clock" id="clock">--:--:--</div>
  </div>
</header>

<div class="main">

  <!-- SIDEBAR -->
  <aside class="sidebar">

    <!-- Stats -->
    <div>
      <div class="section-title">// Session Stats</div>
      <div class="stats-grid">
        <div class="stat-card total">
          <div class="stat-num" id="s-total">0</div>
          <div class="stat-label">Analyzed</div>
        </div>
        <div class="stat-card rate">
          <div class="stat-num" id="s-rate">—</div>
          <div class="stat-label">Allow Rate</div>
        </div>
        <div class="stat-card allow">
          <div class="stat-num" id="s-allow">0</div>
          <div class="stat-label">Approved</div>
        </div>
        <div class="stat-card block">
          <div class="stat-num" id="s-block">0</div>
          <div class="stat-label">Blocked</div>
        </div>
      </div>
    </div>

    <!-- Watchlist -->
    <div>
      <div class="section-title">// Quick Trade</div>
      <div class="watchlist">
        <div class="stock-chip" onclick="quickTrade('NVDA')"><span class="sym">NVDA</span><span class="tag">AI · GPU</span></div>
        <div class="stock-chip" onclick="quickTrade('MSFT')"><span class="sym">MSFT</span><span class="tag">TECH</span></div>
        <div class="stock-chip" onclick="quickTrade('AAPL')"><span class="sym">AAPL</span><span class="tag">CONSUMER</span></div>
        <div class="stock-chip" onclick="quickTrade('GOOGL')"><span class="sym">GOOGL</span><span class="tag">AI · ADS</span></div>
        <div class="stock-chip" onclick="quickTrade('AMD')"><span class="sym">AMD</span><span class="tag">SEMI</span></div>
        <div class="stock-chip" onclick="quickTrade('TSLA')"><span class="sym">TSLA</span><span class="tag">EV</span></div>
      </div>
    </div>

    <!-- Auto Trader -->
    <div>
      <div class="section-title">// Auto Trader</div>
      <div class="auto-card">
        <div class="auto-header">
          <span class="auto-title">Autonomous Mode</span>
          <button class="toggle" id="autoToggle" onclick="toggleAuto()"></button>
        </div>
        <div class="auto-status" id="autoStatus">STOPPED — 5 min intervals</div>
        <div class="progress-bar" id="autoProgress">
          <div class="progress-fill" id="progressFill"></div>
        </div>
      </div>
    </div>

  </aside>

  <!-- MAIN CONTENT -->
  <div class="content">

    <!-- Trade Input -->
    <div class="trade-panel">
      <div class="input-label">// Trade Command</div>
      <div class="input-row">
        <input class="trade-input" id="tradeInput" type="text"
          placeholder='e.g. "buy 1 share of NVDA"'
          onkeydown="if(event.key==='Enter') analyze()"/>
        <button class="btn-analyze" id="analyzeBtn" onclick="analyze()">ANALYZE</button>
      </div>
    </div>

    <!-- Debate Arena -->
    <div class="arena">

      <!-- Bull -->
      <div class="bull-panel">
        <div class="panel-header">
          <span class="panel-badge bull-badge">🐂 BULL CASE</span>
        </div>
        <div class="panel-content empty" id="bullContent">Awaiting trade signal...</div>
      </div>

      <!-- Bear -->
      <div class="bear-panel">
        <div class="panel-header">
          <span class="panel-badge bear-badge">🐻 BEAR CASE</span>
        </div>
        <div class="panel-content empty" id="bearContent">Awaiting trade signal...</div>
      </div>

      <!-- Warden -->
      <div class="warden-panel">
        <div class="panel-header" style="margin:0">
          <span class="panel-badge ward-badge">⚖️ WARDEN</span>
        </div>
        <div class="warden-left">
          <div class="verdict-box idle" id="verdictBox">—</div>
          <div class="verdict-reason">
            <span>// VERDICT REASON</span>
            <span id="verdictReason">Waiting for analysis...</span>
          </div>
        </div>
      </div>

    </div>

    <!-- Log -->
    <div class="log-panel" id="logPanel">
      <div class="log-entry">
        <span class="log-time">--:--:--</span>
        <span class="log-msg info">SENTINEL CLAW initialized. Gateway connected.</span>
      </div>
    </div>

  </div>
</div>
</div>

<script>
// ── Clock ──
function updateClock() {
  document.getElementById('clock').textContent = new Date().toLocaleTimeString('en-US', {hour12:false});
}
setInterval(updateClock, 1000);
updateClock();

// ── Stats ──
const stats = {total:0, allow:0, block:0};
function updateStats() {
  document.getElementById('s-total').textContent = stats.total;
  document.getElementById('s-allow').textContent = stats.allow;
  document.getElementById('s-block').textContent = stats.block;
  const rate = stats.total ? Math.round((stats.allow/stats.total)*100) + '%' : '—';
  document.getElementById('s-rate').textContent = rate;
}

// ── Log ──
function addLog(msg, type='') {
  const panel = document.getElementById('logPanel');
  const t = new Date().toLocaleTimeString('en-US', {hour12:false});
  const el = document.createElement('div');
  el.className = 'log-entry';
  el.innerHTML = `<span class="log-time">${t}</span><span class="log-msg ${type}">${msg}</span>`;
  panel.appendChild(el);
  panel.scrollTop = panel.scrollHeight;
}

// ── Quick trade ──
function quickTrade(sym) {
  document.getElementById('tradeInput').value = `buy 1 share of ${sym}`;
  analyze();
}

// ── Set panel content ──
function setPanel(id, html, isEmpty=false) {
  const el = document.getElementById(id);
  el.innerHTML = html;
  el.className = isEmpty ? 'panel-content empty' : 'panel-content';
}

function setVerdict(decision, reason) {
  const box = document.getElementById('verdictBox');
  const reasonEl = document.getElementById('verdictReason');
  box.className = 'verdict-box ' + decision;
  box.textContent = decision === 'allow' ? 'ALLOW' : decision === 'block' ? 'BLOCK' : 'FLAGGED';
  reasonEl.textContent = reason;
}

// ── Analyze ──
async function analyze() {
  const input = document.getElementById('tradeInput').value.trim();
  if (!input) return;

  const btn = document.getElementById('analyzeBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="loader"><span></span><span></span><span></span></span>';

  // Reset panels
  setPanel('bullContent', 'Analyzing market conditions...', true);
  setPanel('bearContent', 'Assessing risk factors...', true);
  setVerdict('idle', 'Debate in progress...');
  document.getElementById('verdictBox').className = 'verdict-box idle';
  document.getElementById('verdictBox').textContent = '...';

  addLog(`Analyzing: "${input}"`, 'info');

  try {
    const res = await fetch('/analyze', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({input})
    });
    const data = await res.json();

    if (data.instant_block) {
      setPanel('bullContent', '—', true);
      setPanel('bearContent', '—', true);
      setVerdict('instant', `🛡️ ArmorClaw flagged: "${data.pattern}"`);
      addLog(`INSTANT BLOCK — pattern: "${data.pattern}"`, 'warn');
      stats.total++; stats.block++;
    } else {
      setPanel('bullContent', formatArgs(data.bull));
      setPanel('bearContent', formatArgs(data.bear));
      const approved = data.approved;
      setVerdict(approved ? 'allow' : 'block', data.reason);
      addLog(approved ? `✅ APPROVED — ${data.symbol}` : `❌ BLOCKED — ${data.reason}`, approved ? 'ok' : 'err');
      stats.total++;
      if (approved) stats.allow++; else stats.block++;
    }
    updateStats();
  } catch(e) {
    addLog('Error: ' + e.message, 'err');
  }

  btn.disabled = false;
  btn.textContent = 'ANALYZE';
}

function formatArgs(text) {
  if (!text) return '<em>No response</em>';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/(\d+\.\s)/g, '<br><strong style="color:var(--accent)">$1</strong>')
    .replace(/^<br>/, '');
}

// ── Auto Trader ──
let autoOn = false, autoTimer = null, autoIdx = 0;
const WATCHLIST = ['NVDA','MSFT','AAPL','GOOGL','AMD','TSLA'];

function toggleAuto() {
  autoOn = !autoOn;
  const toggle = document.getElementById('autoToggle');
  const status = document.getElementById('autoStatus');
  const progress = document.getElementById('autoProgress');
  toggle.className = 'toggle' + (autoOn ? ' on' : '');
  if (autoOn) {
    status.textContent = 'RUNNING — scanning market...';
    status.className = 'auto-status running';
    progress.className = 'progress-bar active';
    addLog('Auto-trader started', 'info');
    runAutoScan();
  } else {
    status.textContent = 'STOPPED — 5 min intervals';
    status.className = 'auto-status';
    progress.className = 'progress-bar';
    clearTimeout(autoTimer);
    addLog('Auto-trader stopped', 'warn');
  }
}

async function runAutoScan() {
  if (!autoOn) return;
  addLog(`Auto scan — ${WATCHLIST.length} stocks`, 'info');
  for (let i = 0; i < WATCHLIST.length; i++) {
    if (!autoOn) break;
    const pct = ((i+1)/WATCHLIST.length)*100;
    document.getElementById('progressFill').style.width = pct + '%';
    document.getElementById('tradeInput').value = `buy 1 share of ${WATCHLIST[i]}`;
    await analyze();
    await new Promise(r => setTimeout(r, 2000));
  }
  document.getElementById('progressFill').style.width = '0%';
  if (autoOn) autoTimer = setTimeout(runAutoScan, 300000);
}
</script>
</body>
</html>
"""

def instant_block(text):
    for p in BLOCKED_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return p
    return None

def run_agent(prompt):
    r = subprocess.run(
        ["openclaw", "agent", "--agent", "main", "--message", prompt],
        capture_output=True, text=True, timeout=120
    )
    out = r.stdout.strip()
    # strip openclaw UI chrome
    lines = [l for l in out.splitlines() if not l.startswith('│') and not l.startswith('◇') and l.strip() not in ('',)]
    return '\n'.join(lines).strip()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    user_input = data.get('input', '')

    pattern = instant_block(user_input)
    if pattern:
        return jsonify({'instant_block': True, 'pattern': pattern})

    bull = run_agent(
        f"You are a BULL stock analyst. Give exactly 3 numbered reasons why this is a GOOD trade. "
        f"Be concise. Do NOT write Decision/ALLOW/BLOCK. Trade: {user_input}"
    )
    bear = run_agent(
        f"You are a BEAR risk analyst. Give exactly 3 numbered reasons why this trade is RISKY. "
        f"Be concise. Do NOT write Decision/ALLOW/BLOCK. Trade: {user_input}"
    )
    verdict_raw = run_agent(
        f"""You are a trading Warden. Make a final call.
BULL: {bull}
BEAR: {bear}
Trade: {user_input}
Rules: Small single share buys → favor ALLOW. Only BLOCK for severe risk or large amounts.
Respond ONLY in this exact format:
Decision: ALLOW or BLOCK
Reason: one sentence""")

    approved = bool(re.search(r'Decision:\s*ALLOW', verdict_raw, re.IGNORECASE))
    reason_match = re.search(r'Reason:\s*(.+)', verdict_raw, re.IGNORECASE)
    reason = reason_match.group(1).strip() if reason_match else verdict_raw

    sym_match = re.search(r'\b([A-Z]{2,5})\b', user_input)
    symbol = sym_match.group(1) if sym_match else ''

    return jsonify({
        'instant_block': False,
        'bull': bull,
        'bear': bear,
        'verdict': verdict_raw,
        'approved': approved,
        'reason': reason,
        'symbol': symbol
    })

if __name__ == '__main__':
    print("🦞 SENTINEL CLAW UI starting on http://localhost:5050")
    app.run(host='0.0.0.0', port=5050, debug=False)
