# AI-Assisted Network Intrusion Detection System (NIDS)

A real-time network intrusion detection system that monitors live network traffic,
detects suspicious activity, and displays threats on a professional dashboard.

---

## What This System Does

- Captures live network packets using Scapy
- Detects 4 types of attacks using real behavioral analysis:
  - **Port Scan** — attacker probing multiple ports to find vulnerabilities
  - **DoS Flood** — attacker sending massive traffic to crash services
  - **SYN Flood** — attacker sending incomplete connection requests to exhaust resources
  - **Sensitive Port Probe** — attacker targeting SSH, RDP, SMB ports
- Shows each threat with explanation, confidence score, and recommended action
- Operator can Block or Ignore each threat from the dashboard

---

## Requirements

- Kali Linux (or any Linux with Python 3)
- Python 3
- Internet connection (for first-time install only)

---

## Installation (Run Once)

Open terminal and run:

```bash
pip3 install streamlit scapy scikit-learn pandas --break-system-packages
```

---

## How To Run

### Step 1 — Start the Dashboard
```bash
cd ~/nids
streamlit run app.py
```
Open browser and go to: **http://localhost:8501**

### Step 2 — Start the Capture Engine (new terminal)
```bash
cd ~/nids
sudo python3 capture.py
```

### Step 3 — Run Attack Simulator for Demo (new terminal)
```bash
cd ~/nids
python3 attack_simulator.py
```

---

## How To Use the Dashboard

1. Open browser at http://localhost:8501
2. Click **Start Capture** button
3. Run the attack simulator in another terminal
4. Watch threats appear live on the dashboard
5. Click **Block** to block a suspicious IP
6. Click **Ignore** to mark an IP as safe
7. Click **Stop Capture** to end the session
8. Click **Clear Alerts** to reset the dashboard

---

## Project Files

| File | Purpose |
|------|---------|
| app.py | Web dashboard — the user interface |
| capture.py | Packet capture and threat detection engine |
| attack_simulator.py | Controlled attack simulator for demo |
| README.md | This file |

---

## Detection Logic

| Attack | How Detected |
|--------|-------------|
| Port Scan | Same IP hits 15+ different ports in 10 seconds |
| DoS Flood | Same IP sends 200+ packets in 5 seconds |
| SYN Flood | Same IP sends 50+ SYN packets without completing handshake |
| Sensitive Port Probe | Any connection attempt to ports 22, 23, 445, 3389, 135 |

---

*Built for educational and research purposes in a controlled environment.*
