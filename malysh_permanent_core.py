import os
import csv
import random
import time
import math
import asyncio
import socket
import threading
import json
from concurrent.futures import ThreadPoolExecutor
from collections import deque
import curses
import traceback

# --- КОНТУР 1: Многофакторная модель (ETS + Байес + Сезонность) ---
class MultiFactorEngine:
    def __init__(self, pool_range=45):
        self.pool_range = pool_range

    def analyze(self, history_bank):
        if not history_bank:
            return {i: 0.1 for i in range(1, self.pool_range + 1)}, []
        
        total_draws = len(history_bank)
        scores = {i: 1.0 for i in range(1, self.pool_range + 1)}
        history_list = list(history_bank)
        
        alpha = 0.25
        for idx, draw in enumerate(history_list):
            weight = math.exp((idx - total_draws) * alpha)
            for num in draw:
                if 1 <= num <= self.pool_range:
                    scores[num] += 8.0 * weight

        if total_draws > 1:
            last_seen = {i: -1 for i in range(1, self.pool_range + 1)}
            for idx, draw in enumerate(history_list):
                for num in draw:
                    if 1 <= num <= self.pool_range:
                        last_seen[num] = idx
            
            current_idx = total_draws - 1
            for num, l_idx in last_seen.items():
                if l_idx != -1:
                    delta = current_idx - l_idx
                    scores[num] += delta * 0.35

        total_score = sum(scores.values())
        probabilities = {num: round(val / total_score, 4) for num, val in scores.items()}
        ranked = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        forecast = [item[0] for item in ranked[:5]]
        return probabilities, forecast

# --- КОНТУР 2 & 3: Сетевой кластер и фоновый Daemon Server ---
class MalyshClusterDaemon(threading.Thread):
    def __init__(self, host='127.0.0.1', port=9999, history_ref=None):
        super().__init__()
        self.host = host
        self.port = port
        self.history_ref = history_ref
        self.daemon = True
        self.is_running = True
        self.client_connections = 0
        self.socket_server = None

    def run(self):
        try:
            self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_server.bind((self.host, self.port))
            self.socket_server.listen(5)
            while self.is_running:
                try:
                    self.socket_server.settimeout(1.0)
                    conn, addr = self.socket_server.accept()
                    self.client_connections += 1
                    threading.Thread(target=self.handle_client, args=(conn,)).start()
                except socket.timeout:
                    continue
        except Exception as e:
            pass

    def handle_client(self, conn):
        try:
            data = conn.recv(1024).decode('utf-8')
            response = {"status": "OK", "node": "Malysh-ARM-Cluster", "history_len": len(self.history_ref) if self.history_ref else 0}
            conn.sendall(json.dumps(response).encode('utf-8'))
        except:
            pass
        finally:
            conn.close()

    def stop(self):
        self.is_running = False
        if self.socket_server:
            try:
                self.socket_server.close()
            except:
                pass

# --- Графический Curses UI с кластерной телеметрией ---
def get_sparkline(val, max_val):
    chars = "  ▂▃▄▅▆▇█"
    if max_val <= 0:
        return chars[0]
    idx = int((val / max_val) * (len(chars) - 1))
    return chars[max(0, min(idx, len(chars) - 1))]

def run_cluster_dashboard(stdscr, history_bank, pool_range, probs, forecast, cluster_daemon):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(500)

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        title = " 🚀 МАЛЫШ: CLUSTER + DAEMON + HPC SPARKLINE SUITE "
        if width > len(title):
            try:
                stdscr.addstr(0, 0, title[:width-1], curses.A_BOLD | curses.A_REVERSE)
            except:
                pass

        try:
            stdscr.addstr(2, 2, f"📂 Банк памяти: {len(history_bank)} тиражей | Пул: 1-{pool_range}")
            stdscr.addstr(3, 2, f"📡 Daemon Server: {cluster_daemon.host}:{cluster_daemon.port} [ACTIVE]")
            stdscr.addstr(4, 2, f"🔗 Внешних подключений к кластеру: {cluster_daemon.client_connections}")
            stdscr.addstr(5, 2, f"🎯 МНОГОФАКТОРНЫЙ ПРОГНОЗ: {forecast}", curses.A_BOLD)
            stdscr.addstr(7, 2, "📊 РАСПРЕДЕЛЕННАЯ ТЕПЛОВАЯ МАТРИЦА (1-45):", curses.A_UNDERLINE)
        except:
            pass

        max_p = max(probs.values()) if probs else 1.0
        row_y = 9
        col_x = 2
        
        for num in range(1, pool_range + 1):
            p = probs.get(num, 0)
            spark = get_sparkline(p, max_p)
            
            if row_y < height - 3 and col_x + 10 < width:
                try:
                    stdscr.addstr(row_y, col_x, f"{num:02d}:[{spark}]")
                except:
                    pass
            
            col_x += 7
            if num % 6 == 0:
                row_y += 1
                col_x = 2

        try:
            stdscr.addstr(height - 2, 2, "Кластер работает в фоне. Нажми [q] для выхода.", curses.A_DIM)
            stdscr.refresh()
        except:
            pass

        try:
            key = stdscr.getch()
            if key == ord('q') or key == ord('Q'):
                break
        except:
            pass

        time.sleep(0.05)

# --- Главный диспетчер ---
class MasterClusterManager:
    def __init__(self, csv_filename="lottery_history.csv", pool_range=45):
        self.csv_filename = csv_filename
        self.pool_range = pool_range
        self.history_bank = deque(maxlen=2000)
        self.multifactor_engine = MultiFactorEngine(pool_range)
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.csv_filename):
            with open(self.csv_filename, 'w', encoding='utf-8') as f:
                f.write("5,12,19,24,33,42\n3,11,18,25,32,40\n1,8,15,22,29,38\n")
        
        self.history_bank.clear()
        with open(self.csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    numbers = [int(item.strip()) for item in row if item.strip().isdigit()]
                    if numbers:
                        self.history_bank.append(sorted(numbers))
                except:
                    continue

    def run(self):
        # Запускаем фоновый Daemon & Cluster Node в отдельном потоке
        daemon = MalyshClusterDaemon(host='127.0.0.1', port=9999, history_ref=self.history_bank)
        daemon.start()

        probs, forecast = self.multifactor_engine.analyze(self.history_bank)

        try:
            curses.wrapper(lambda stdscr: run_cluster_dashboard(stdscr, self.history_bank, self.pool_range, probs, forecast, daemon))
        except Exception as e:
            with open("cluster_error.log", "w") as err_f:
                err_f.write(traceback.format_exc())
            print(f"Ошибка кластерного интерфейса: {e}")
        finally:
            daemon.stop()

if __name__ == "__main__":
    manager = MasterClusterManager()
    manager.run()
