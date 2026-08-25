import curses
import threading
import time
import math
import random

cluster_bus = {}
bus_lock = threading.Lock()

apex_organism = {
    "leader": "Alpha",
    "core_mode": "APEX_AUTONOMOUS",
    "global_entropy": 0.04,
    "system_health": "100% [SYNERGY]",
    "healed_count": 0,
    "synergy_index": 0.99,
    "active_strategy": "Adaptive-Flow"
}

class ApexNode(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.forecast_depth = 12
        self.health = "PRISTINE"
        self.last_seen = time.time()

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 10)
            
            with bus_lock:
                mode = apex_organism["core_mode"]
            
            # Автономное управление множителем от общего режима
            if mode == "APEX_AUTONOMOUS":
                mult = 1.2 + (self.clock % 5) * 0.1
            elif mode == "TURBO":
                mult = 2.0
            else:
                mult = 1.0

            state = int((math.sin(t * mult) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            node_entropy = round(random.uniform(0.01, 0.12), 3)

            # Симуляция самовосстанавливающейся флуктуации
            if random.random() < 0.015:
                self.health = "DRIFT_DETECTED"
            elif self.health == "DRIFT_DETECTED":
                self.health = "PRISTINE" # Авто-хилинг на уровне ноды

            self.last_seen = time.time()

            with bus_lock:
                cluster_bus[str(self.port)] = {
                    "node_id": self.node_id,
                    "port": self.port,
                    "clock": self.clock,
                    "state": state,
                    "p": p,
                    "density": density,
                    "forecast": forecast,
                    "entropy": node_entropy,
                    "depth": self.forecast_depth,
                    "health": self.health,
                    "timestamp": self.last_seen
                }
            time.sleep(0.35)

def apex_brain_daemon(nodes_map):
    """Высший нервный центр: межузловая аналитика, консенсус и исцеление"""
    while True:
        time.sleep(0.4)
        now = time.time()
        
        with bus_lock:
            if not cluster_bus:
                continue
            nodes = list(cluster_bus.values())

        # 1. Self-Healing Engine
        healed_events = 0
        for port, node_obj in nodes_map.items():
            p_str = str(port)
            if p_str in cluster_bus:
                data = cluster_bus[p_str]
                if (now - data["timestamp"] > 1.8) or (data["health"] == "DRIFT_DETECTED"):
                    healed_events += 1
                    apex_organism["healed_count"] += 1
                    data["health"] = "REGENERATED"
                    node_obj.clock = max(0, node_obj.clock - 5)

        # 2. Cluster Intelligence Layer (кросс-анализ энтропии и синергии)
        avg_ent = sum(n["entropy"] for n in nodes) / len(nodes)
        pristine_count = sum(1 for n in nodes if n["health"] in ["PRISTINE", "REGENERATED"])
        health_ratio = (pristine_count / len(nodes)) * 100

        with bus_lock:
            apex_organism["global_entropy"] = round(avg_ent, 3)
            apex_organism["synergy_index"] = round(1.0 - (avg_ent * 0.4), 3)
            apex_organism["system_health"] = f"{int(health_ratio)}% [APEX SYNERGY]"

            # 3. Cluster Autonomy Mode (саморегуляция стратегий)
            if avg_ent > 0.09:
                apex_organism["active_strategy"] = "High-Density Guard"
                apex_organism["core_mode"] = "TURBO"
            else:
                apex_organism["active_strategy"] = "Harmonic Equilibrium"
                apex_organism["core_mode"] = "APEX_AUTONOMOUS"

            leader_node = max(nodes, key=lambda x: x["clock"])
            apex_organism["leader"] = leader_node["node_id"]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    nodes_map = {
        9999: ApexNode("Edge-Node-01 [Alpha]", 9999),
        9998: ApexNode("Edge-Node-02 [Beta]", 9998)
    }
    for n in nodes_map.values():
        n.start()

    threading.Thread(target=apex_brain_daemon, args=(nodes_map,), daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('s'):
                with bus_lock:
                    cur = apex_organism["core_mode"]
                    apex_organism["core_mode"] = "STANDARD" if cur != "STANDARD" else "APEX_AUTONOMOUS"
        except Exception:
            pass

        with bus_lock:
            data_snap = dict(cluster_bus)
            apex_snap = dict(apex_organism)

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 40:
            stdscr.addstr(0, 0, "Terminal too narrow")
            stdscr.refresh()
            time.sleep(0.1)
            continue

        r = 0
        def out(txt):
            nonlocal r
            if r < height - 1:
                try:
                    stdscr.addstr(r, 0, txt[:width])
                except:
                    pass
                r += 1

        out("=== MALYSH v8.0 APEX ORGANISM ===")
        out(f"Health: {apex_snap['system_health']} | Heals: {apex_snap['healed_count']}")
        out(f"Strat: {apex_snap['active_strategy']} | Syn: {apex_snap['synergy_index']}")

        if current_port not in data_snap and data_snap:
            current_port = list(data_snap.keys())[0]

        node_info = data_snap.get(current_port, {
            "node_id": "Sync...", "port": current_port, "clock": 0,
            "state": 0, "p": 0.0, "density": 0.0, "forecast": 0.0,
            "entropy": 0.0, "depth": 12, "health": "SYNC"
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        out(f"View: {node_info.get('node_id')} (P:{node_info.get('port')})")
        out(f"Clk: #{node_info.get('clock')} | St: {node_info.get('state')} | HLT: {node_info.get('health')}")
        out(f"Fc: {node_info.get('forecast')} | Ent: {node_info.get('entropy')} | Glob: {apex_snap['global_entropy']}")

        if height > 14:
            out("Apex Matrix (3x3):")
            st = node_info.get('state', 0)
            for row_idx in range(3):
                line = "".join(["█" if ((st + row_idx*3 + col) % 5) > 2 else "░" for col in range(3)])
                out(f"  [{line}]")

        spark_str = "".join(["█" if val > 23 else "." for val in sparkline_data])
        out(f"Pulse: [{spark_str}]")

        stdscr.refresh()
        time.sleep(0.1)

    for n in nodes_map.values():
        n.running = False

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nApex Organism shut down safely.")
