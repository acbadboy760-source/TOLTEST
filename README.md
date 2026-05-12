# 🛡️ Ultimate DDoS Simulation Toolkit (God Mode)

**⚠️ IMPORTANT LEGAL NOTICE**
This tool is designed **solely for educational purposes, authorized penetration testing, and stress-testing your own infrastructure in isolated environments.** Using this tool against any system without explicit written permission from the owner is **illegal** and may result in severe legal consequences. The developer assumes no responsibility for any misuse or damage caused.

---

## ✨ Features
- **11 Attack Vectors**: L7 (HTTP/1.1, HTTP/2, Mixed, R.U.D.Y., Cache Bypass, Range Header, HTTP Desync) & L4 (SYN, ACK, UDP, ICMP)
- **God Mode Worker**: Aggressive request patterns with random payloads, dynamic paths, and real-world User-Agent rotation
- **Supersonic 2-Phase Port Scan**: High-priority HTTP ports first, then deep Nmap probe
- **Smart Caching**: Stores scan results locally to avoid rescanning the same target
- **Live Attack Dashboard**: Built with `rich` – shows total sent, success/fail ratio, RPS, and elapsed time
- **Automatic Reports**: Exports a plain-text summary after each run
- **100% Serverless & Free**: Powered by GitHub Actions on public repositories

---

## 🚀 How to Use (Step-by-Step)

### Step 1: Fork this Repository
Click the **"Fork"** button at the top right of this page to copy the project to your own GitHub account.

### Step 2: Open the Actions Tab
In your forked repository, navigate to the **"Actions"** tab at the top.

### Step 3: Run the Workflow
- On the left sidebar, click **"Ultimate DDoS Simulation Toolkit"**.
- Click the gray **"Run workflow"** dropdown button on the right side.
- Fill in the parameters (see below) and click the green **"Run workflow"** button.

### Step 4: Wait and Watch
The workflow will start. Click on the running job to view the **live attack dashboard**.

### Step 5: Read the Report
After completion, an `attack_report.txt` file will be automatically saved in the root of your repository.

---

## ⚙️ Workflow Inputs
| Parameter | Description | Default |
|-----------|-------------|---------|
| `attack` | Type of attack (see options below) | `l7_mixed_flood` |
| `target` | URL or IP address of the target (only your own!) | *required* |
| `port` | Target port (`auto` for automatic scan) | `auto` |
| `duration` | Attack duration in seconds | `120` |
| `threads` | Number of concurrent worker threads | `300` |

### Available Attack Modes
- `l7_http_flood`
- `l7_http2_flood`
- `l7_mixed_flood` (recommended for stress testing)
- `l7_rudy_flood`
- `l7_cache_bypass`
- `l7_range_flood`
- `l7_desync_flood`
- `l4_syn_flood`
- `l4_ack_flood`
- `l4_udp_flood`
- `l4_icmp_flood`

---

## 📊 Understanding the Live Dashboard
🔥 LIVE ATTACK STATS
📤 Total Sent: 125,430
✅ Success: 98.7%
❌ Failed: 1.3%
⚡ Avg. RPS: 3,200
⏱️ Elapsed: 38.2s
- **Success Rate** shows how many requests got a valid response from the target.
- **RPS** (Requests Per Second) measures the raw power of the attack.

---

## 📜 License & Security Policy
- **[MIT License](LICENSE)** – You are free to use it for any legal purpose, but the original disclaimer must be kept.
- **[Security Policy](SECURITY.md)** – Please read before use. Abuse will not be tolerated.
