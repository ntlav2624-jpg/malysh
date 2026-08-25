import curses
import threading
import time
import math
import random

cluster_bus = {}
bus_lock = threading.Lock()

emergence_core = {
    "leader": "Alpha",
    "emergent_state": "EMERGENCE_ACTIVE",
    "global_entropy": 0.03,
    "cluster_health": "100% [IMMUNE SYNERGY]",
    "total_healings": 0,
    "memory_depth": 0,
    "current_behavior": "Harmonic Resonance",
    "evolution_cycles": 0
}

class EmergentNode(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.local_memory = []
        self.forecast_depth = 14
        self.health = "OPTIMAL"
        self.last_seen = time.time()

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 10)
            
            with bus_lock:
                behavior = emergence_core["current_behavior"]
            
            # Поведение определяет внутреннюю математику волны
            if behavior == "Harmonic Resonance":
                mult = 1.2 + math.sin(self.clock * 0.1) * 0.3
            elif behavior == "Adaptive Shifting":
                mult = 1.8 if (self.clock % 10 > 5) else 0.9
            else: # Deep Synthesis
                mult = 1.5 + (self.clock % 3) * 0.2

            state = int((math.sin(t * mult) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            node_entropy = round(random.uniform(0.01, 0.10), 3)

            # Накопление локальной памяти кластера
            self.local_memory.append(state)
            if len(self.local_memory) > 50:
                self.local_memory.pop(0)

            # Симуляция самовосстановления при дрейфе
            if random.random() < 0.01:
                self.health = "RE-SYNCING"
            elif self.health == "RE-SYNCING":
                self.health = "OPTIMAL"

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
                    "memory_size": len(self.local_memory),
                    "health": self.health,
                    "timestamp": self.last_seen
                }
            time.sleep(0.3)

def emergence_brain_daemon(nodes_map):
    """Высший эмерджентный разум: память, исцеление и генерация поведения"""
    while True:
        time.sleep(0.4)
        now = time.time()
        
        with bus_lock:
            if not cluster_bus:
                continue
            nodes = list(cluster_bus.values())

        # 1. Advanced Self-Healing Engine
        heals = 0
        for port, node_obj in nodes_map.items():
            p_str = str(port)
            if p_str in cluster_bus:
                data = cluster_bus[p_str]
                if (now - data["timestamp"] > 1.5) or (data["health"] == "RE-SYNCING"):
                    heals += 1
                    emergence_core["total_healings"] += 1
                    data["health"] = "REGENERATED"
                    node_obj.clock = max(0, node_obj.clock - 3)

        # 2. Cluster Intelligence & Memory Layer
        avg_ent = sum(n["entropy"] for n in nodes) / len(nodes)
        total_mem = sum(n["memory_size"] for n in nodes)
        healthy_cnt = sum(1 for n in nodes if n["health"] in ["OPTIMAL", "REGENERATED"])
        health_pct = int((healthy_cnt / len(nodes)) * 100)

        with bus_lock:
            emergence_core["global_entropy"] = round(avg_ent, 3)
            emergence_core["memory_depth"] = total_mem
            emergence_core["cluster_health"] = f"{health_pct}% [IMMUNE SYNERGY]"
            emergence_core["evolution_cycles"] += 1

            # 3. Emergent Autonomy Mode (самозарождение паттернов поведения)
            cycles = emergence_core["evolution_cycles"]
            if cycles % 40 < 15:
                emergence_core["current_behavior"] = "Harmonic Resonance"
            elif cycles % 40 < 30:
                emergence_core["current_behavior"] = "Adaptive Shifting"
            else:
                emergence_core["current_behavior"] = "Deep Synthesis"

            leader_node = max(nodes, key=lambda x: x["clock"])
            emergence_core["leader"] = leader_node["node_id"]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    nodes_map = {
        9999: EmergentNode("Edge-Node-01 [Alpha]", 9999),
        9998: EmergentNode("Edge-Node-02 [Beta]", 9998)
    }
    for n in nodes_map.values():
        n.start()

    threading.Thread(target=emergence_brain_daemon, args=(nodes_map,), daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('e'):
                # Форсированный эволюционный цикл
                with bus_lock:
                    behaviors = ["Harmonic Resonance", "Adaptive Shifting", "Deep Synthesis"]
                    curr = emergence_core["current_behavior"]
                    next_b = behaviors[(behaviors.index(curr) + 1) % len(behaviors)]
                    emergence_core["current_behavior"] = next_b
        except Exception:
            pass

        with bus_lock:
            data_snap = dict(cluster_bus)
            emergence_snap = dict(emergence_core)

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

        out("=== MALYSH v9.0 EMERGENCE ===")
        out(f"Health: {emergence_snap['cluster_health']} | Heals: {emergence_snap['total_healings']}")
        out(f"Behavior: {emergence_snap['current_behavior']} [e: cycle]")
        out(f"Memory: {emergence_snap['memory_depth']} units | Cyc: {emergence_snap['evolution_cycles']}")

        if current_port not in data_snap and data_snap:
            current_port = list(data_snap.keys())[0]

        node_info = data_snap.get(current_port, {
            "node_id": "Sync...", "port": current_port, "clock": 0,
            "state": 0, "p": 0.0, "density": 0.0, "forecast": 0.0,
            "entropy": 0.0, "memory_size": 0, "health": "SYNC"
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        out(f"View: {node_info.get('node_id')} (P:{node_info.get('port')})")
        out(f"Clk: #{node_info.get('clock')} | St: {node_info.get('state')} | HLT: {node_info.get('health')}")
        out(f"Fc: {node_info.get('forecast')} | Ent: {node_info.get('entropy')} | Glob: {emergence_snap['global_entropy']}")

        if height > 15:
            out("Emergent Matrix (3x3):")
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
        print("\nEmergent Organism shut down safely.")
