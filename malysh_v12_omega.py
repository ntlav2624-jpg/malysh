import curses
import threading
import time
import math
import random
import json
import os

cluster_bus = {}
bus_lock = threading.Lock()
WAL_FILE = "malysh_omega_wal.log"

omega_core = {
    "leader": "Omega-Prime",
    "paradigm": "KMBP_COGNITIVE_SYNTHESIS",
    "global_entropy": 0.015,
    "system_status": "100% [OMEGA OMNI-SYNERGY]",
    "total_wal_records": 0,
    "total_heals": 0,
    "active_strategy": "Omni-Resonance",
    "evolution_tier": "TRANSCENDENT",
    "synaptic_field": 0.99
}

class OmegaNode(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.quaternary_memory = []
        self.synapse_weight = 1.0
        self.forecast_depth = 20
        self.health = "OMEGA_PRISTINE"
        self.last_seen = time.time()

    def write_wal(self, record):
        try:
            with open(WAL_FILE, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 5)
            
            with bus_lock:
                strat = omega_core["active_strategy"]

            # Мульти-модальная математика волны на основе текущей стратегии
            if strat == "Omni-Resonance":
                mod = 1.4 + math.sin(self.clock * 0.07) * 0.3
            elif strat == "Adaptive Quaternary":
                mod = 1.8 if (self.clock % 8 > 4) else 1.1
            else: # Deep Synapse
                mod = 1.5 + (self.clock % 5) * 0.1

            base4_val = int((math.sin(t * mod) + 1) * 1.5) % 4
            state = int((math.sin(t * mod) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            entropy = round(random.uniform(0.001, 0.05), 3)

            # Накопление кватернарно-когнитивной памяти
            self.quaternary_memory.append({"b4": base4_val, "state": state, "entropy": entropy})
            if len(self.quaternary_memory) > 50:
                self.quaternary_memory.pop(0)

            self.synapse_weight = round(1.0 - (entropy * 0.4), 4)

            # Проактивное самоисцеление при микро-дрейфе
            if random.random() < 0.007:
                self.health = "RE-CALIBRATING"
            elif self.health == "RE-CALIBRATING":
                self.health = "OMEGA_PRISTINE"

            record = {
                "node_id": self.node_id,
                "port": self.port,
                "clock": self.clock,
                "base4": base4_val,
                "state": state,
                "p": p,
                "density": density,
                "forecast": forecast,
                "entropy": entropy,
                "synapse": self.synapse_weight,
                "health": self.health,
                "timestamp": time.time()
            }

            self.write_wal(record)
            self.last_seen = time.time()

            with bus_lock:
                cluster_bus[str(self.port)] = record
                omega_core["total_wal_records"] += 1

            time.sleep(0.35)

def omega_brain_daemon(nodes_map):
    """Высший омни-мозг: консенсус, регенерация WAL и когнитивная автономия"""
    while True:
        time.sleep(0.4)
        now = time.time()
        
        with bus_lock:
            if not cluster_bus:
                continue
            nodes = list(cluster_bus.values())

        # 1. Self-Healing & Regeneration Engine
        for port, node_obj in nodes_map.items():
            p_str = str(port)
            if p_str in cluster_bus:
                data = cluster_bus[p_str]
                if (now - data["timestamp"] > 1.6) or (data["health"] == "RE-CALIBRATING"):
                    data["health"] = "REGENERATED"
                    node_obj.clock = max(0, node_obj.clock - 2)
                    omega_core["total_heals"] += 1

        # 2. Cluster Intelligence & Synaptic Layer
        avg_ent = sum(n["entropy"] for n in nodes) / len(nodes)
        avg_syn = sum(n["synapse"] for n in nodes) / len(nodes)
        pristine_cnt = sum(1 for n in nodes if n["health"] in ["OMEGA_PRISTINE", "REGENERATED"])
        health_ratio = int((pristine_cnt / len(nodes)) * 100)
        
        b4_stream = "-".join([str(n["base4"]) for n in nodes])

        with bus_lock:
            omega_core["global_entropy"] = round(avg_ent, 3)
            omega_core["synaptic_field"] = round(avg_syn, 3)
            omega_core["system_status"] = f"{health_ratio}% [OMEGA OMNI-SYNERGY]"

            # 3. Cluster Autonomy Mode (Эмерджентное переключение стратегий)
            cycles = omega_core.get("cycles", 0) + 1
            omega_core["cycles"] = cycles
            
            if cycles % 60 < 20:
                omega_core["active_strategy"] = "Omni-Resonance"
            elif cycles % 60 < 40:
                omega_core["active_strategy"] = "Adaptive Quaternary"
            else:
                omega_core["active_strategy"] = "Deep Synapse"

            leader_node = max(nodes, key=lambda x: x["clock"])
            omega_core["leader"] = leader_node["node_id"]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    if os.path.exists(WAL_FILE):
        open(WAL_FILE, "w").close()

    nodes_map = {
        9999: OmegaNode("Omega-Alpha [Core-I]", 9999),
        9998: OmegaNode("Omega-Beta [Core-II]", 9998)
    }
    for n in nodes_map.values():
        n.start()

    threading.Thread(target=omega_brain_daemon, args=(nodes_map,), daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('o'):
                with bus_lock:
                    strategies = ["Omni-Resonance", "Adaptive Quaternary", "Deep Synapse"]
                    curr = omega_core["active_strategy"]
                    omega_core["active_strategy"] = strategies[(strategies.index(curr) + 1) % len(strategies)]
        except Exception:
            pass

        with bus_lock:
            data_snap = dict(cluster_bus)
            omega_snap = dict(omega_core)

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

        out("=== MALYSH v12.0 OMEGA APEX ===")
        out(f"Status: {omega_snap['system_status']} | Heals: {omega_snap['total_heals']}")
        out(f"Strategy: {omega_snap['active_strategy']} [o: switch]")
        out(f"WAL: {omega_snap['total_wal_records']} | Synapse: {omega_snap['synaptic_field']}")

        if current_port not in data_snap and data_snap:
            current_port = list(data_snap.keys())[0]

        node_info = data_snap.get(current_port, {
            "node_id": "Sync...", "port": current_port, "clock": 0,
            "base4": 0, "state": 0, "p": 0.0, "density": 0.0, 
            "forecast": 0.0, "entropy": 0.0, "synapse": 1.0, "health": "SYNC"
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        out(f"View: {node_info.get('node_id')} (Port {node_info.get('port')})")
        out(f"Clk: #{node_info.get('clock')} | B4: {node_info.get('base4')} | St: {node_info.get('state')}")
        out(f"Fc: {node_info.get('forecast')} | Ent: {node_info.get('entropy')} | HLT: {node_info.get('health')}")

        if height > 15:
            out("Omega Bio-Matrix (3x3):")
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
        print("\nOmega Apex Organism shut down safely. All systems persistent.")
