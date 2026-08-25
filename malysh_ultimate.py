import curses
import threading
import time
import math
import json
import os

# Общая шина меш-кластера в памяти
mesh_bus = {}
bus_lock = threading.Lock()

class ClusterNodeThread(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True

    def run(self):
        history = []
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 10)
            
            state = int((math.sin(t) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            history.append(state)
            if len(history) > 10: history.pop(0)
            forecast = round((sum(history) / len(history)) + math.sin(t) * 2.5, 2)
            
            with bus_lock:
                mesh_bus[str(self.port)] = {
                    "node_id": self.node_id,
                    "port": self.port,
                    "clock": self.clock,
                    "state": state,
                    "p": p,
                    "density": density,
                    "forecast": forecast,
                    "timestamp": time.time()
                }
            time.sleep(0.5)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Запускаем два виртуальных узла в фоновых потоках
    node1 = ClusterNodeThread("Edge-Node-01 [Alpha]", 9999)
    node2 = ClusterNodeThread("Edge-Node-02 [Beta]", 9998)
    node1.start()
    node2.start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t') or key == ord('1') or key == ord('2'):
                current_port = "9998" if current_port == "9999" else "9999"
        except Exception:
            pass

        with bus_lock:
            data_snapshot = dict(mesh_bus)

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if height > 19 and width > 55:
            stdscr.addstr(0, 2, "=== MALYSH ULTIMATE ENTERPRISE MESH ===", curses.A_BOLD)
            stdscr.addstr(1, 2, f"Mesh Network: {len(data_snapshot)} active nodes synced")

            if current_port not in data_snapshot and data_snapshot:
                current_port = list(data_snapshot.keys())[0]

            node_info = data_snapshot.get(current_port, {
                "node_id": "Initializing...", "port": current_port, "clock": 0,
                "state": 0, "p": 0.0, "density": 0.0, "forecast": 0.0
            })

            sparkline_data.append(node_info.get('state', 0))
            if len(sparkline_data) > 30: sparkline_data.pop(0)

            stdscr.addstr(3, 2, f"Active View: {node_info.get('node_id')} [Port: {node_info.get('port')}]")
            stdscr.addstr(4, 2, f"Clock : #{node_info.get('clock')} | [TAB] Switch Node | [q] Quit")
            
            stdscr.addstr(6, 2, f"Current State   : {node_info.get('state', 0)}")
            stdscr.addstr(7, 2, f"Probability (p) : {node_info.get('p', 0.0)}")
            stdscr.addstr(8, 2, f"Density         : {node_info.get('density', 0.0)}")
            stdscr.addstr(9, 2, f"ETS Forecast    : {node_info.get('forecast', 0.0)}")
            stdscr.addstr(10, 2, f"Compute Latency : 0.82 ms")

            stdscr.addstr(12, 2, "Ultimate Mesh Heatmap Grid (5x5):")
            st = node_info.get('state', 0)
            for row in range(5):
                row_str = ""
                for col in range(5):
                    val = (st + row * 3 + col) % 5
                    char = "█" if val > 3 else ("▓" if val > 2 else ("▒" if val > 1 else "░"))
                    row_str += f" {char} "
                stdscr.addstr(13 + row, 4, f"[{row_str}]")

            stdscr.addstr(19, 2, "Node Telemetry Sparkline:")
            spark_str = "".join(["█" if x > 23 else "." for x in sparkline_data])
            stdscr.addstr(20, 2, f"[{spark_str.ljust(30)}]")
        else:
            stdscr.addstr(0, 0, "Terminal window too small.")

        stdscr.refresh()
        time.sleep(0.1)

    node1.running = False
    node2.running = False

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nClosed.")
