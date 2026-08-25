import os
import sys
import sqlite3
import socket
import threading
import json
import time
import math

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
NODE_ID = sys.argv[2] if len(sys.argv) > 2 else "Edge-Node-01 [Alpha]"
DB_PATH = f"malysh_cluster_{PORT}.db"
BUS_PATH = "malysh_cluster_bus.json"
HOST = "127.0.0.1"
LOG_FILE = f"engine_{PORT}.log"

def log_msg(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S')} - {msg}\n")

class MalyshUltimateEngine:
    def __init__(self, node_id, port):
        self.node_id = node_id
        self.port = port
        self._init_db()
        self.running = True
        self.history_states = []
        self.cluster_clock = 0

    def _init_db(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL;")
        self.cursor.execute("PRAGMA synchronous=NORMAL;")
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS cluster_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                state_code INTEGER,
                probability REAL,
                density REAL,
                forecast REAL
            )
        """)
        self.conn.commit()

    def log_state(self, state_code, p, density, forecast):
        timestamp = time.time()
        self.cursor.execute(
            "INSERT INTO cluster_logs (timestamp, state_code, probability, density, forecast) VALUES (?, ?, ?, ?, ?)",
            (timestamp, state_code, p, density, forecast)
        )
        self.conn.commit()
        self.cursor.execute("DELETE FROM cluster_logs WHERE id NOT IN (SELECT id FROM cluster_logs ORDER BY id DESC LIMIT 1000)")
        self.conn.commit()

    def _update_mesh_bus(self, state_code, forecast):
        bus_data = {}
        try:
            if os.path.exists(BUS_PATH):
                with open(BUS_PATH, "r") as f:
                    bus_data = json.load(f)
        except Exception:
            pass
        
        bus_data[str(self.port)] = {
            "node_id": self.node_id,
            "clock": self.cluster_clock,
            "state": state_code,
            "forecast": forecast,
            "timestamp": time.time()
        }
        
        try:
            with open(BUS_PATH, "w") as f:
                json.dump(bus_data, f)
        except Exception:
            pass

    def compute_step(self):
        start_time = time.time()
        self.cluster_clock += 1
        t = time.time() + (self.port % 10)
        
        raw_state = (math.sin(t) + 1) * 22 + 1
        state_code = int(raw_state)
        p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
        density = round(math.exp(-((state_code - 23)**2) / 200), 3)
        
        self.history_states.append(state_code)
        if len(self.history_states) > 10:
            self.history_states.pop(0)
        trend = sum(self.history_states) / len(self.history_states)
        forecast_val = round(trend + math.sin(t) * 2.5, 2)

        self.log_state(state_code, p, density, forecast_val)
        self._update_mesh_bus(state_code, forecast_val)
        
        elapsed = (time.time() - start_time) * 1000

        heatmap_grid = [
            round(math.sin(t + i * 0.2) * (p / (density + 0.001)), 2) for i in range(25)
        ]

        return {
            "node_id": self.node_id,
            "port": self.port,
            "cluster_clock": self.cluster_clock,
            "state": state_code,
            "p": p,
            "density": density,
            "forecast": forecast_val,
            "heatmap": heatmap_grid,
            "compute_ms": round(elapsed, 2)
        }

class MalyshMeshDaemon:
    def __init__(self, engine: MalyshUltimateEngine):
        self.engine = engine
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        try:
            self.server_socket.bind((HOST, self.engine.port))
            self.server_socket.listen(5)
            log_msg(f"Mesh Node [{self.engine.node_id}] active on {HOST}:{self.engine.port}")
        except Exception as e:
            log_msg(f"Bind error: {e}")
            return

        while self.engine.running:
            try:
                self.server_socket.settimeout(1.0)
                client_sock, addr = self.server_socket.accept()
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except socket.timeout:
                continue
            except Exception as e:
                log_msg(f"Accept error: {e}")
                break

    def _handle_client(self, client_sock):
        try:
            while self.engine.running:
                data = self.engine.compute_step()
                payload = json.dumps(data) + "\n"
                client_sock.sendall(payload.encode("utf-8"))
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:
            log_msg(f"Client handler error: {e}")
        finally:
            client_sock.close()

if __name__ == "__main__":
    log_msg(f"Starting engine on port {PORT}...")
    engine = MalyshUltimateEngine(NODE_ID, PORT)
    daemon = MalyshMeshDaemon(engine)
    try:
        daemon.start()
    except KeyboardInterrupt:
        log_msg("Shutting down...")
        engine.running = False
