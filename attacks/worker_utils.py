import os, sys, time, socket, random, nmap, json, threading, concurrent.futures
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

console = Console()
CACHE_DIR = Path("scan_results")
CACHE_FILE = CACHE_DIR / "targets_cache.json"
CACHE_VALID_HOURS = 24

stop_event = threading.Event()
stats = {'sent': 0, 'success': 0, 'failed': 0, 'start_time': time.time(), 'lock': threading.Lock()}

def increment(key, amount=1):
    with stats['lock']: stats[key] += amount

def get_stats():
    with stats['lock']:
        elapsed = time.time() - stats['start_time']
        return {'sent': stats['sent'], 'success': stats['success'], 'failed': stats['failed'], 'elapsed': elapsed, 'rps': stats['sent'] / elapsed if elapsed > 0 else 0}

def resolve_target(target):
    for prefix in ['https://', 'http://']:
        if target.startswith(prefix): target = target[len(prefix):]
    target = target.split('/')[0].split(':')[0]
    try:
        return socket.getaddrinfo(target, None, socket.AF_INET, socket.SOCK_STREAM)[0][4][0]
    except:
        return None

def load_cache():
    if not CACHE_FILE.exists(): return {}
    try:
        with open(CACHE_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_cache(cache_data):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, 'w') as f: json.dump(cache_data, f, indent=2)

def get_cached_scan(target_ip):
    cache = load_cache()
    if target_ip in cache:
        entry = cache[target_ip]
        scan_time = datetime.fromisoformat(entry['timestamp'])
        if datetime.now() - scan_time < timedelta(hours=CACHE_VALID_HOURS):
            console.print(f"[green]✅ کش معتبر برای {target_ip}[/green]")
            return entry['ports']
    return None

def update_cache(target_ip, target_host, open_ports):
    cache = load_cache()
    cache[target_ip] = {'host': target_host, 'timestamp': datetime.now().isoformat(), 'ports': open_ports}
    save_cache(cache)
    os.system(f"git add {CACHE_FILE} && git commit -m 'Update cache for {target_host}' && git push 2>/dev/null || true")

COMMON_HTTP_PORTS = [80, 443, 8080, 8443, 3000, 8000, 9000, 5000, 4000, 4443]

def check_port(ip, port, timeout=0.3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return port if result == 0 else None
    except:
        return None

def fast_http_scan(ip):
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_port = {executor.submit(check_port, ip, port): port for port in COMMON_HTTP_PORTS}
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            try:
                res = future.result()
                if res is not None:
                    open_ports.append({'port': res, 'service': 'http' if res in (80,8080,8000,3000,5000,4000) else 'https'})
            except: pass
    return open_ports

def deep_scan_ports(ip):
    nm = nmap.PortScanner()
    nm.scan(hosts=ip, arguments=f'-sT -sV -p 1-20000 --min-rate 10000 --max-retries 0')
    open_ports = []
    if ip in nm.all_hosts():
        for proto in nm[ip].all_protocols():
            for port in sorted(nm[ip][proto].keys()):
                if nm[ip][proto][port]['state'] == 'open':
                    service = nm[ip][proto][port]['name']
                    open_ports.append({'port': port, 'service': service})
    return open_ports

def discover_ports(ip, attack_type):
    if attack_type.startswith('l7'):
        ports = fast_http_scan(ip)
        if ports: return ports
        console.print("[yellow]⚠️ رفتن به Nmap...[/yellow]")
    return deep_scan_ports(ip)

def stats_display():
    s = get_stats()
    table = Table(show_header=False, box=None, padding=(0,2))
    table.add_column("متریک", style="cyan"); table.add_column("مقدار", style="bold white")
    table.add_row("📤 ارسالی", f"{s['sent']:,}")
    table.add_row("✅ موفق", f"[green]{s['success']:,}[/green]")
    table.add_row("❌ ناموفق", f"[red]{s['failed']:,}[/red]")
    success_rate = (s['success']/(s['sent'] or 1))*100
    table.add_row("🎯 نرخ موفقیت", f"[bold yellow]{success_rate:.1f}%[/bold yellow]")
    table.add_row("⚡ RPS", f"{s['rps']:.0f}")
    table.add_row("⏱️ زمان", f"{s['elapsed']:.1f}s")
    return Panel(table, title="[bold green]🔥 آمار زنده[/bold green]", border_style="green")
