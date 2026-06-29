import streamlit as st
import json
import os
import time
from datetime import datetime

st.set_page_config(
    page_title="NIDS — Network Intrusion Detection System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow:wght@400;600;700;900&display=swap');

:root {
  --bg:#060910;--card:#111827;--border:#1f2937;
  --red:#ef4444;--orange:#f97316;--green:#22c55e;--blue:#38bdf8;
  --muted:#6b7280;--text:#f1f5f9;
  --mono:'Share Tech Mono',monospace;--sans:'Barlow',sans-serif;
}
html,body,[data-testid="stAppViewContainer"]{
  background:var(--bg)!important;color:var(--text)!important;
  font-family:var(--sans)!important;
}
[data-testid="stAppViewContainer"]{
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,
  rgba(56,189,248,.015) 2px,rgba(56,189,248,.015) 4px),var(--bg)!important;
}
[data-testid="stHeader"],[data-testid="stToolbar"],footer,#MainMenu{display:none!important;}
section[data-testid="stMain"]>div{padding-top:1.5rem!important;}

.nids-header{display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--border);padding-bottom:1.2rem;margin-bottom:2rem;}
.nids-title{font-family:var(--mono);font-size:1.5rem;letter-spacing:.12em;
  color:var(--blue);text-transform:uppercase;}
.nids-title span{color:var(--red);}
.nids-clock{font-family:var(--mono);font-size:.85rem;color:var(--muted);}
.live-dot{display:inline-block;width:8px;height:8px;border-radius:50%;
  background:var(--green);margin-right:6px;animation:pulse 1.4s infinite;}
@keyframes pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(34,197,94,.5);}
  50%{opacity:.7;box-shadow:0 0 0 6px rgba(34,197,94,0);}}

.about-banner{background:var(--card);border:1px solid var(--border);
  border-left:4px solid var(--blue);border-radius:6px;
  padding:1.2rem 1.5rem;margin-bottom:1.8rem;}
.about-title{font-family:var(--mono);font-size:.75rem;letter-spacing:.15em;
  color:var(--blue);text-transform:uppercase;margin-bottom:.6rem;}
.about-text{font-size:.88rem;color:#94a3b8;line-height:1.7;}

.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);
  gap:1rem;margin-bottom:1.8rem;}
.metric-card{background:var(--card);border:1px solid var(--border);
  border-radius:6px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
.metric-card.blue::before{background:var(--blue);}
.metric-card.red::before{background:var(--red);}
.metric-card.orange::before{background:var(--orange);}
.metric-card.green::before{background:var(--green);}
.metric-label{font-family:var(--mono);font-size:.7rem;letter-spacing:.15em;
  color:var(--muted);text-transform:uppercase;margin-bottom:.5rem;}
.metric-value{font-family:var(--mono);font-size:2.2rem;font-weight:900;line-height:1;}
.metric-card.blue .metric-value{color:var(--blue);}
.metric-card.red .metric-value{color:var(--red);}
.metric-card.orange .metric-value{color:var(--orange);}
.metric-card.green .metric-value{color:var(--green);}

.section-heading{font-family:var(--mono);font-size:.75rem;letter-spacing:.18em;
  color:var(--muted);text-transform:uppercase;border-left:3px solid var(--blue);
  padding-left:.7rem;margin-bottom:1rem;margin-top:1.5rem;}

.alert-row{background:var(--card);border:1px solid var(--border);
  border-radius:6px;padding:1rem 1.2rem;margin-bottom:.6rem;
  display:grid;grid-template-columns:4px 90px 140px 130px 1fr 170px;
  align-items:center;gap:1rem;}
.alert-row:hover{border-color:var(--blue);}
.sev-bar{border-radius:4px;width:4px;height:40px;}
.sev-HIGH{background:var(--red);box-shadow:0 0 8px var(--red);}
.sev-MEDIUM{background:var(--orange);box-shadow:0 0 8px var(--orange);}
.sev-LOW{background:var(--green);box-shadow:0 0 8px var(--green);}
.alert-time{font-family:var(--mono);font-size:.75rem;color:var(--muted);}
.alert-ip{font-family:var(--mono);font-size:.85rem;color:var(--blue);}
.badge{display:inline-block;padding:.15rem .55rem;border-radius:3px;
  font-family:var(--mono);font-size:.7rem;letter-spacing:.08em;font-weight:700;}
.badge-HIGH{background:rgba(239,68,68,.15);color:var(--red);
  border:1px solid rgba(239,68,68,.3);}
.badge-MEDIUM{background:rgba(249,115,22,.15);color:var(--orange);
  border:1px solid rgba(249,115,22,.3);}
.badge-LOW{background:rgba(34,197,94,.15);color:var(--green);
  border:1px solid rgba(34,197,94,.3);}
.attack-type{font-size:.72rem;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;margin-top:.3rem;display:block;}
.type-HIGH{color:var(--red);}
.type-MEDIUM{color:var(--orange);}
.type-LOW{color:var(--green);}
.alert-reason{font-size:.82rem;color:#94a3b8;line-height:1.5;}
.alert-meta{font-family:var(--mono);font-size:.73rem;color:var(--muted);line-height:1.7;}

.status-bar{background:var(--card);border:1px solid var(--border);
  border-radius:6px;padding:.8rem 1.2rem;margin-bottom:1.5rem;}
.status-active{color:var(--green);font-family:var(--mono);font-size:.82rem;}

.empty-state{text-align:center;padding:4rem 2rem;color:var(--muted);
  font-family:var(--mono);font-size:.85rem;letter-spacing:.1em;
  border:1px dashed var(--border);border-radius:6px;}

.blocked-row{background:#1a0a0a;border:1px solid rgba(239,68,68,.3);
  border-radius:6px;padding:.7rem 1.2rem;margin-bottom:.4rem;
  font-family:var(--mono);font-size:.82rem;color:#ef4444;}
</style>
""", unsafe_allow_html=True)

# ── session state ─────────────────────────────────────────────────────────────
if "blocked_ips" not in st.session_state:
    st.session_state.blocked_ips = set()
if "ignored_ips" not in st.session_state:
    st.session_state.ignored_ips = set()

# ── helpers ───────────────────────────────────────────────────────────────────
def load_alerts():
    alerts = []
    if os.path.exists("alerts.json"):
        with open("alerts.json","r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        alerts.append(json.loads(line))
                    except:
                        pass
    return alerts

# ── header ────────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
st.markdown(f"""
<div class="nids-header">
  <div class="nids-title"><span>■</span> NIDS &mdash; Network Intrusion Detection System</div>
  <div class="nids-clock"><span class="live-dot"></span>LIVE &nbsp;|&nbsp; {now_str}</div>
</div>""", unsafe_allow_html=True)

# ── about ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="about-banner">
  <div class="about-title">About This System</div>
  <div class="about-text">
    This is a <strong style="color:#f1f5f9">Network Intrusion Detection System (NIDS)</strong>
    that monitors live network traffic and automatically detects suspicious activity in real time.
    It identifies four attack types —
    <strong style="color:#ef4444">Port Scans</strong>,
    <strong style="color:#ef4444">DoS Floods</strong>,
    <strong style="color:#ef4444">SYN Floods</strong>, and
    <strong style="color:#f97316">Sensitive Port Probes</strong>.
    For each threat detected, the system explains what is happening, why it is dangerous,
    and what action the operator should take.
    Use the <strong style="color:#22c55e">Block</strong> button to block a suspicious IP,
    or <strong style="color:#38bdf8">Ignore</strong> to mark it as safe.
  </div>
</div>""", unsafe_allow_html=True)

# ── status + clear button ─────────────────────────────────────────────────────
col_status, col_clear = st.columns([5, 1])

with col_status:
    st.markdown("""
    <div class="status-bar">
      <span class="status-active">
        ⬤ &nbsp; CAPTURE ENGINE ACTIVE — Monitoring network traffic in real time
      </span>
    </div>""", unsafe_allow_html=True)

with col_clear:
    if st.button("🗑  Clear All Alerts", use_container_width=True):
        if os.path.exists("alerts.json"):
            os.remove("alerts.json")
        st.session_state.blocked_ips = set()
        st.session_state.ignored_ips = set()
        st.rerun()

# ── load data ─────────────────────────────────────────────────────────────────
alerts = load_alerts()
total  = len(alerts)
high   = len([a for a in alerts if a.get("severity") == "HIGH"])
medium = len([a for a in alerts if a.get("severity") == "MEDIUM"])
blocked = len(st.session_state.blocked_ips)

# ── metrics ───────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card blue">
    <div class="metric-label">Total Alerts</div>
    <div class="metric-value">{total}</div>
  </div>
  <div class="metric-card red">
    <div class="metric-label">High Severity</div>
    <div class="metric-value">{high}</div>
  </div>
  <div class="metric-card orange">
    <div class="metric-label">Medium Severity</div>
    <div class="metric-value">{medium}</div>
  </div>
  <div class="metric-card green">
    <div class="metric-label">Blocked IPs</div>
    <div class="metric-value">{blocked}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── live threat feed ──────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Live Threat Feed — Last 20 Events</div>',
            unsafe_allow_html=True)

recent = [a for a in reversed(alerts[-20:])
          if a.get("src_ip") not in st.session_state.ignored_ips]

if not recent:
    st.markdown("""
    <div class="empty-state">
      ⬡ &nbsp; NO ALERTS DETECTED &nbsp; ⬡<br>
      <span style="font-size:.7rem;opacity:.5">
        Run capture.py and attack_simulator.py to generate events
      </span>
    </div>""", unsafe_allow_html=True)
else:
    for i, alert in enumerate(recent):
        sev = alert.get("severity", "LOW")
        ip  = alert.get("src_ip", "unknown")

        st.markdown(f"""
        <div class="alert-row">
          <div class="sev-bar sev-{sev}"></div>
          <div class="alert-time">{alert.get('time','--:--:--')}</div>
          <div class="alert-ip">{ip}</div>
          <div>
            <span class="badge badge-{sev}">{sev}</span>
            <span class="attack-type type-{sev}">{alert.get('attack_type','UNKNOWN')}</span>
          </div>
          <div class="alert-reason">{alert.get('reason','No details.')}</div>
          <div class="alert-meta">
            Confidence: {alert.get('confidence','--')}<br>
            Protocol: {alert.get('protocol','--')}<br>
            Port: {alert.get('dst_port','--')}<br>
            <span style="color:#475569;font-size:.7rem">
              {alert.get('recommendation','')}
            </span>
          </div>
        </div>""", unsafe_allow_html=True)

        c1, c2, _ = st.columns([1, 1, 6])
        if c1.button("🚫 Block", key=f"blk_{i}"):
            st.session_state.blocked_ips.add(ip)
            st.rerun()
        if c2.button("✅ Ignore", key=f"ign_{i}"):
            st.session_state.ignored_ips.add(ip)
            st.rerun()

# ── blocked IPs ───────────────────────────────────────────────────────────────
if st.session_state.blocked_ips:
    st.markdown('<div class="section-heading">Blocked IPs</div>',
                unsafe_allow_html=True)
    for ip in st.session_state.blocked_ips:
        st.markdown(f"""
        <div class="blocked-row">
          🚫 &nbsp; {ip}
          <span style="color:#6b7280;font-size:.7rem"> — Blocked by operator</span>
        </div>""", unsafe_allow_html=True)

# ── auto refresh ──────────────────────────────────────────────────────────────
time.sleep(3)
st.rerun()
