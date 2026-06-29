from scapy.all import sniff, IP, TCP, UDP
import json
import time
from datetime import datetime
from collections import defaultdict

# ── detection thresholds ──────────────────────────────────────────────────────
WINDOW     = 10   # seconds
DOS_WINDOW = 5
DOS_LIMIT  = 200  # packets in DOS_WINDOW to trigger DoS
PORT_LIMIT = 15   # distinct ports in WINDOW to trigger port scan
SYN_LIMIT  = 50   # SYN packets in WINDOW to trigger SYN flood

# ── per-IP tracking tables ────────────────────────────────────────────────────
port_tracker   = defaultdict(set)
packet_counter = defaultdict(list)
syn_counter    = defaultdict(list)

def classify(src_ip, dst_port, flags, protocol):
    now    = time.time()
    alerts = []

    # track packets
    packet_counter[src_ip].append(now)
    packet_counter[src_ip] = [t for t in packet_counter[src_ip] if now - t < WINDOW]
    port_tracker[src_ip].add(dst_port)

    unique_ports  = len(port_tracker[src_ip])
    recent_count  = len(packet_counter[src_ip])

    # ── Port Scan ─────────────────────────────────────────────────────────────
    if unique_ports >= PORT_LIMIT:
        alerts.append({
            "attack_type":    "PORT SCAN",
            "severity":       "HIGH",
            "reason":         f"This IP has probed {unique_ports} different ports in {WINDOW} seconds. "
                              f"Normal devices connect to 1–2 ports. This is automated reconnaissance.",
            "confidence":     f"{min(99, 70 + unique_ports)}%",
            "recommendation": "Block this IP immediately. Port scanning is the first step of a larger attack."
        })

    # ── DoS Flood ─────────────────────────────────────────────────────────────
    recent_dos = [t for t in packet_counter[src_ip] if now - t < DOS_WINDOW]
    if len(recent_dos) >= DOS_LIMIT:
        alerts.append({
            "attack_type":    "DoS FLOOD",
            "severity":       "HIGH",
            "reason":         f"This IP sent {len(recent_dos)} packets in {DOS_WINDOW} seconds. "
                              f"That is {len(recent_dos)//DOS_WINDOW}x above normal traffic rate.",
            "confidence":     "95%",
            "recommendation": "Block this IP. High-volume floods can crash services and cause downtime."
        })

    # ── SYN Flood ─────────────────────────────────────────────────────────────
    if protocol == "TCP" and flags:
        flag_str = str(flags)
        if "S" in flag_str and "A" not in flag_str:
            syn_counter[src_ip].append(now)
            syn_counter[src_ip] = [t for t in syn_counter[src_ip] if now - t < WINDOW]
            if len(syn_counter[src_ip]) >= SYN_LIMIT:
                alerts.append({
                    "attack_type":    "SYN FLOOD",
                    "severity":       "HIGH",
                    "reason":         f"This IP sent {len(syn_counter[src_ip])} SYN packets without "
                                      f"completing handshakes. This exhausts server connection resources.",
                    "confidence":     "92%",
                    "recommendation": "Block immediately. Enable SYN cookies on your firewall."
                })

    # ── Sensitive Port Probe ──────────────────────────────────────────────────
    sensitive = {22:"SSH", 23:"Telnet", 445:"SMB File Sharing",
                 3389:"Remote Desktop (RDP)", 135:"Windows RPC"}
    if dst_port in sensitive and unique_ports < PORT_LIMIT:
        alerts.append({
            "attack_type":    "SENSITIVE PORT PROBE",
            "severity":       "MEDIUM",
            "reason":         f"Connection attempt to port {dst_port} ({sensitive[dst_port]}). "
                              f"This port is a common target for credential attacks and exploitation.",
            "confidence":     "65%",
            "recommendation": f"Monitor this IP. If attempts continue, block it. "
                              f"Ensure {sensitive[dst_port]} is password-protected."
        })

    return alerts


def process_packet(packet):
    if IP not in packet:
        return

    src_ip   = packet[IP].src
    dst_ip   = packet[IP].dst
    protocol = "TCP" if TCP in packet else "UDP" if UDP in packet else "OTHER"
    dst_port = 0
    flags    = None

    if TCP in packet:
        dst_port = packet[TCP].dport
        flags    = packet[TCP].flags
    elif UDP in packet:
        dst_port = packet[UDP].dport

    for det in classify(src_ip, dst_port, flags, protocol):
        alert = {
            "time":           datetime.now().strftime("%H:%M:%S"),
            "src_ip":         src_ip,
            "dst_ip":         dst_ip,
            "protocol":       protocol,
            "dst_port":       dst_port,
            "attack_type":    det["attack_type"],
            "severity":       det["severity"],
            "reason":         det["reason"],
            "confidence":     det["confidence"],
            "recommendation": det["recommendation"]
        }
        with open("alerts.json","a") as f:
            f.write(json.dumps(alert) + "\n")
        print(f"[{alert['severity']}] {alert['attack_type']} from {src_ip} — port {dst_port}")


if __name__ == "__main__":
    print("="*60)
    print("  NIDS Capture Engine — Listening on loopback...")
    print("="*60)
    sniff(prn=process_packet, store=0, iface="lo", filter="host 127.0.0.1")
