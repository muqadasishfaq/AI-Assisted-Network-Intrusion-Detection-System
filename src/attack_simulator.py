"""
NIDS Attack Simulator
Simulates controlled attacks on localhost (127.0.0.1) for demo purposes.
All traffic stays inside your machine — nothing goes to the internet.
"""
import socket, time, random

TARGET = "127.0.0.1"

def port_scan():
    print("\n[1/4] Running Port Scan simulation...")
    for port in [21,22,23,25,53,80,443,445,3306,3389,8080,8443,9000,9090,4444,5900]:
        try:
            s = socket.socket()
            s.settimeout(0.3)
            s.connect_ex((TARGET, port))
            s.close()
        except: pass
        time.sleep(0.05)
    print("      Port Scan complete.")

def sensitive_probe():
    print("\n[2/4] Running Sensitive Port Probe simulation...")
    for port in [22, 3389, 445, 23]:
        try:
            s = socket.socket()
            s.settimeout(0.3)
            s.connect_ex((TARGET, port))
            s.close()
        except: pass
        time.sleep(0.3)
    print("      Sensitive Probe complete.")

def syn_flood():
    print("\n[3/4] Running SYN Flood simulation...")
    for _ in range(55):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.05)
            s.connect_ex((TARGET, 80))
            s.close()
        except: pass
        time.sleep(0.02)
    print("      SYN Flood complete.")

def dos_flood():
    print("\n[4/4] Running DoS Flood simulation...")
    for _ in range(210):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"X"*512, (TARGET, random.randint(1024,9000)))
            s.close()
        except: pass
    print("      DoS Flood complete.")

if __name__ == "__main__":
    print("="*60)
    print("  NIDS Attack Simulator — Controlled Demo Mode")
    print("  Target: 127.0.0.1 (localhost only)")
    print("="*60)
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    sensitive_probe()
    time.sleep(1)
    port_scan()
    time.sleep(1)
    syn_flood()
    time.sleep(1)
    dos_flood()
    print("\n" + "="*60)
    print("  All simulations complete. Check your dashboard.")
    print("="*60)
