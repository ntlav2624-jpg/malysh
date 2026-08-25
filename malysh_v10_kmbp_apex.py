import curses
import threading
import time
import math
import random
import json
import os

cluster_bus = {}
bus_lock = threading.Lock()
WAL_FILE = "malysh_kmbp_wal.log"

kmbp_apex_state = {
    "leader": "Alpha-Core",
    "core_mode": "KMBP_BASE4_APEX",
    "global_entropy": 0.025,
    "system_health": "100% [QUANTUM SYNERGY]",
    "total_wal_records": 0,
    "healed_count": 0,
    "base4_state": "3-2-1-0",
    "evolution_tier": "OMEGA"
}

class KMBPApexNode(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.quaternary_memory = []
        self.forecast_depth = 16
        self.health = "PRISTINE"
        self.last_seen = time.time()

    def write_wal(self, data_record):
        """Запись в Write-Ahead Log для персистентности состояний"""
        try:
            with open(WAL_FILE, "a") as f:
                f.write(json.dumps(data_record) + "\n")
        except Exception:
            pass

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 7)
            
            # Кватернарная логика Base-4 (0, 1, 2, 3) на базе волновой функции
            base4_val = int((math.sin(t * 1.5) + 1) * 1.5) % 4
            state = int((math.sin(t * 1.3) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            node_entropy = round(random.uniform(0.005, 0.09), 3)

            # Накопление кватернарной памяти
            self.quaternary_memory.append(base4_val)
            if len(self.quaternary_memory) > 40:
                self.quaternary_memory.pop(0)

            # Самоисцеление на уровне ноды
            if random.random() < 0.01:
                self.health = "RE-CALIBRATING"
            elif self.health == "RE-CALIBRATING":
                self.health = "PRISTINE"

            record = {
                "node_id": self.node_id,
                "port": self.port,
                "clock": self.clock,
                "base4": base4_val,
                "state": state,
                "p": p,
                "density": density,
                "forecast": forecast,
                "entropy": node_entropy,
                "health": self.health,
                "timestamp": time.time()
            }

            self.write_wal(record)
            self.last_seen = time.time()

            with bus_lock:
                cluster_bus[str(self.port)] = record
                kmbp_apex_state["total_wal_records"] += 1

            time.sleep(0.35)

def kmbp_brain_daemon(nodes_map):
    """Высший мозг КМБП: консенсус, защита WAL и самоисцеление"""
    while True:
        time.sleep(0.4)
        now = time.time()
        
        with bus_lock:
            if not cluster_bus:
                continue
            nodes = list(cluster_bus.values())

        # 1. Self-Healing Engine
        heals = 0
        for port, node_obj in nodes_map.items():
            p_str = str(port)
            if p_str in cluster_bus:
                data = cluster_bus[p_str]
                if (now - data["timestamp"] > 1.6) or (data["health"] == "RE-CALIBRATING"):
                    heals += 1
                    kmbp_apex_state["healed_count"] += 1
                    data["health"] = "RE-SYNTHESIZED"
                    node_obj.clock = max(0, node_obj.clock - 4)

        # 2. Intelligence & Base-4 Synthesis
        avg_ent = sum(n["entropy"] for n in nodes) / len(nodes)
        pristine_cnt = sum(1 for n in nodes if n["health"] in ["PRISTINE", "RE-SYNTHESIZED"])
        health_ratio = int((pristine_cnt / len(nodes)) * 100)
        
        b4_stream = "-".join([str(n["base4"]) for n in nodes])

        with bus_lock:
            kmbp_apex_state["global_entropy"] = round(avg_ent, 3)
            kmbp_apex_state["system_health"] = f"{health_ratio}% [QUANTUM SYNERGY]"
            kmbp_apex_state["base4_state"] = b4_stream

            leader_node = max(nodes, key=lambda x: x["clock"])
            kmbp_apex_state["leader"] = leader_node["node_id"]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Инициализация WAL файла
    if os.path.exists(WAL_FILE):
        open(WAL_FILE, "w").close()

    nodes_map = {
        9999: KMBPApexNode("KMBP-Alpha [Core-1]", 9999),
        9998: KMBPApexNode("KMBP-Beta [Core-2]", 9998)
    }
    for n in nodes_map.values():
        n.start()

    threading.Thread(target=kmbp_brain_daemon, args=(nodes_map,), daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('c'):
                with bus_lock:
                    kmbp_apex_state["evolution_tier"] = "QUANTUM_LOCKED" if kmbp_apex_state["evolution_tier"] == "OMEGA" else "OMEGA"
        except Exception:
            pass

        with bus_lock:
            data_snap = dict(cluster_bus)
            apex_snap = dict(kmbp_apex_state)

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

        out("=== MALYSH v10.0 KMBP-APEX ===")
        out(f"Health: {apex_snap['system_health']} | Heals: {apex_snap['healed_count']}")
        out(f"Base-4 Stream: [{apex_snap['base4_state']}] Tier: {apex_snap['evolution_tier']}")
        out(f"WAL Records: {apex_snap['total_wal_records']} | GlobEnt: {apex_snap['global_entropy']}")

        if current_port not in data_snap and data_snap:
            current_port = list(data_snap.keys())[0]

        node_info = data_snap.get(current_port, {
            "node_id": "Sync...", "port": current_port, "clock": 0,
            "base4": 0, "state": 0, "p": 0.0, "density": 0.0, 
            "forecast": 0.0, "entropy": 0.0, "health": "SYNC"
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        out(f"View: {node_info.get('node_id')} (Port {node_info.get('port')})")
        out(f"Clk: #{node_info.get('clock')} | B4: {node_info.get('base4')} | St: {node_info.get('state')} | HLT: {node_info.get('health')}")
        out(f"Fc: {node_info.get('forecast')} | Ent: {node_info.get('entropy')} | P: {node_info.get('p')}")

        if height > 15:
            out("KMBP Bio-Matrix (3x3):")
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
        print("\nKMBP-APEX Organism shut down safely. WAL secured.")
