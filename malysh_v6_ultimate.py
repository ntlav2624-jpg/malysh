import curses
import threading
import time
import math
import random

cluster_bus = {}
bus_lock = threading.Lock()
global_consensus_state = {"leader": "Alpha", "state": 0, "adaptive_factor": 0.5, "mode": "STANDARD"}

class AutonomousNode(threading.Thread):
    def __init__(self, node_id, port, is_primary=False):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.is_primary = is_primary
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.forecast_depth = 10

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 10)
            
            with bus_lock:
                mode = global_consensus_state["mode"]
            
            multiplier = 1.5 if mode == "TURBO" else 1.0
            
            state = int((math.sin(t * multiplier) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            entropy = round(random.uniform(0.01, 0.15), 3)

            with bus_lock:
                cluster_bus[str(self.port)] = {
                    "node_id": self.node_id,
                    "port": self.port,
                    "clock": self.clock,
                    "state": state,
                    "p": p,
                    "density": density,
                    "forecast": forecast,
                    "entropy": entropy,
                    "depth": self.forecast_depth,
                    "timestamp": time.time()
                }
            time.sleep(0.4)

def consensus_daemon():
    while True:
        time.sleep(0.6)
        with bus_lock:
            if cluster_bus:
                nodes = list(cluster_bus.values())
                leader_node = max(nodes, key=lambda x: x["clock"])
                avg_state = int(sum(n["state"] for n in nodes) / len(nodes))
                
                global_consensus_state["leader"] = leader_node["node_id"]
                global_consensus_state["state"] = avg_state
                global_consensus_state["adaptive_factor"] = round(0.5 + (avg_state % 10) * 0.05, 3)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    node1 = AutonomousNode("Edge-Node-01 [Alpha]", 9999, is_primary=True)
    node2 = AutonomousNode("Edge-Node-02 [Beta]", 9998)
    node1.start()
    node2.start()

    threading.Thread(target=consensus_daemon, daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('t'):
                with bus_lock:
                    current_mode = global_consensus_state["mode"]
                    global_consensus_state["mode"] = "STANDARD" if current_mode == "TURBO" else "TURBO"
            elif key == ord('+'):
                node1.forecast_depth = min(20, node1.forecast_depth + 2)
                node2.forecast_depth = min(20, node2.forecast_depth + 2)
            elif key == ord('-'):
                node1.forecast_depth = max(4, node1.forecast_depth - 2)
                node2.forecast_depth = max(4, node2.forecast_depth - 2)
        except Exception:
            pass

        with bus_lock:
            data_snapshot = dict(cluster_bus)
            consensus_snapshot = dict(global_consensus_state)

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 40:
            stdscr.addstr(0, 0, "Width too small")
            stdscr.refresh()
            time.sleep(0.1)
            continue

        # Компактный рендеринг, идеально помещающийся под клавиатуру
        row_idx = 0
        def safe_add(text, attr=0):
            nonlocal row_idx
            if row_idx < height - 1:
                try:
                    stdscr.addstr(row_idx, 0, text[:width], attr)
                except:
                    pass
                row_idx += 1

        safe_add("=== MALYSH v6.0 MESH ===", curses.A_BOLD)
        safe_add(f"Nodes: {len(data_snapshot)} | Leader: {consensus_snapshot['leader'][:12]}")
        safe_add(f"State: {consensus_snapshot['state']} | Mode: {consensus_snapshot['mode']} [t/+/-, TAB:node]")

        if current_port not in data_snapshot and data_snapshot:
            current_port = list(data_snapshot.keys())[0]

        node_info = data_snapshot.get(current_port, {
            "node_id": "Init...", "port": current_port, "clock": 0,
            "state": 0, "p": 0.0, "density": 0.0, "forecast": 0.0, "entropy": 0.0, "depth": 10
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        safe_add(f"View: {node_info.get('node_id')} (Port {node_info.get('port')})")
        safe_add(f"Clk: #{node_info.get('clock')} | St: {node_info.get('state')} | P: {node_info.get('p')}")
        safe_add(f"Fc: {node_info.get('forecast')} (dp:{node_info.get('depth')}) | Ent: {node_info.get('entropy')}")

        if height > 12:
            safe_add("Heatmap (3x3):")
            st = node_info.get('state', 0)
            for r in range(3):
                r_str = "".join(["█" if ((st + r*3 + c) % 5) > 2 else "░" for c in range(3)])
                safe_add(f"  [{r_str}]")

        spark_str = "".join(["█" if x > 23 else "." for x in sparkline_data])
        safe_add(f"Spark: [{spark_str}]")

        stdscr.refresh()
        time.sleep(0.1)

    node1.running = False
    node2.running = False

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nClosed.")
