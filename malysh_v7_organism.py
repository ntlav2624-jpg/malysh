import curses
import threading
import time
import math
import random

cluster_bus = {}
bus_lock = threading.Lock()

# Органическое состояние кластера (Autonomy & Intelligence)
organism_state = {
    "leader": "Alpha",
    "autonomy_mode": "AUTONOMOUS",
    "global_entropy": 0.05,
    "cluster_health": "100% [OPTIMAL]",
    "self_healing_events": 0,
    "intelligence_index": 0.98
}

class LivingNode(threading.Thread):
    def __init__(self, node_id, port):
        super().__init__()
        self.node_id = node_id
        self.port = port
        self.daemon = True
        self.clock = 0
        self.running = True
        self.history = []
        self.forecast_depth = 10
        self.health_status = "HEALTHY"
        self.last_update = time.time()

    def run(self):
        while self.running:
            self.clock += 1
            t = time.time() + (self.port % 10)
            
            with bus_lock:
                mode = organism_state["autonomy_mode"]
            
            # Автономное изменение множителя в зависимости от режима
            mult = 2.0 if mode == "HYPER" else (1.4 if mode == "TURBO" else 1.0)
            
            state = int((math.sin(t * mult) + 1) * 22 + 1)
            p = round(0.5 + 0.4 * math.cos(t * 0.5), 3)
            density = round(math.exp(-((state - 23)**2) / 200), 3)
            
            self.history.append(state)
            if len(self.history) > self.forecast_depth: 
                self.history.pop(0)
            
            trend = sum(self.history) / len(self.history)
            forecast = round(trend + math.sin(t) * 2.5, 2)
            local_entropy = round(random.uniform(0.01, 0.20), 3)

            # Симуляция случайной микро-деградации для проверки Self-Healing
            if random.random() < 0.02:  
                self.health_status = "DEGRADED"
            elif self.health_status == "DEGRADED" and random.random() < 0.5:
                self.health_status = "HEALTHY"

            self.last_update = time.time()

            with bus_lock:
                cluster_bus[str(self.port)] = {
                    "node_id": self.node_id,
                    "port": self.port,
                    "clock": self.clock,
                    "state": state,
                    "p": p,
                    "density": density,
                    "forecast": forecast,
                    "entropy": local_entropy,
                    "depth": self.forecast_depth,
                    "health": self.health_status,
                    "timestamp": self.last_update
                }
            time.sleep(0.4)

def organism_brain_daemon(nodes_dict):
    """Фоновый мозг: консенсус, Intelligence Layer и Self-Healing Watchdog"""
    while True:
        time.sleep(0.5)
        now = time.time()
        
        with bus_lock:
            if not cluster_bus:
                continue
            
            nodes = list(cluster_bus.values())
            
        # 1. Self-Healing Watchdog: проверка зависших или больных нод
        healed_count = 0
        for port, node_obj in nodes_dict.items():
            port_str = str(port)
            if port_str in cluster_bus:
                n_data = cluster_bus[port_str]
                # Если узел завис (нет отклика > 2 сек) или помечен как DEGRADED
                if (now - n_data["timestamp"] > 2.0) or (n_data["health"] == "DEGRADED"):
                    healed_count += 1
                    organism_state["self_healing_events"] += 1
                    n_data["health"] = "HEALED [RESTARTED]"
                    node_obj.clock = 0  # Сброс такта для регенерации

        # 2. Cluster Intelligence: расчет общей энтропии и индекса здоровья
        avg_entropy = sum(n["entropy"] for n in nodes) / len(nodes)
        healthy_nodes = sum(1 for n in nodes if "HEALED" not in n["health"] and n["health"] != "DEGRADED")
        health_pct = int((healthy_nodes / len(nodes)) * 100)

        with bus_lock:
            organism_state["global_entropy"] = round(avg_entropy, 3)
            organism_state["cluster_health"] = f"{health_pct}% [{'OPTIMAL' if health_pct > 80 else 'RECOVERING'}]"
            organism_state["intelligence_index"] = round(1.0 - (avg_entropy * 0.5), 3)
            
            # 3. Cluster Autonomy Mode: саморегуляция режимов среды
            if avg_entropy > 0.12:
                organism_state["autonomy_mode"] = "TURBO"
            elif avg_entropy < 0.04:
                organism_state["autonomy_mode"] = "AUTONOMOUS"
            else:
                organism_state["autonomy_mode"] = "STANDARD"

            # Лидер выбирается по максимальному интеллекту/такту
            leader = max(nodes, key=lambda x: x["clock"])
            organism_state["leader"] = leader["node_id"]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Создаем узлы организма
    nodes_map = {
        9999: LivingNode("Edge-Node-01 [Alpha]", 9999),
        9998: LivingNode("Edge-Node-02 [Beta]", 9998)
    }
    
    for n in nodes_map.values():
        n.start()

    # Запуск автономного мозга кластера
    threading.Thread(target=organism_brain_daemon, args=(nodes_map,), daemon=True).start()

    current_port = "9999"
    sparkline_data = []

    while True:
        try:
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('\t'):
                current_port = "9998" if current_port == "9999" else "9999"
            elif key == ord('m'):
                # Принудительное ручное переключение режима поверх автономии
                with bus_lock:
                    m = organism_state["autonomy_mode"]
                    organism_state["autonomy_mode"] = "HYPER" if m != "HYPER" else "AUTONOMOUS"
        except Exception:
            pass

        with bus_lock:
            data_snapshot = dict(cluster_bus)
            org_snapshot = dict(organism_state)

        stdscr.clear()
        height, width = stdscr.getmaxyx()

        if width < 40:
            stdscr.addstr(0, 0, "Width too small")
            stdscr.refresh()
            time.sleep(0.1)
            continue

        row = 0
        def p(text, attr=0):
            nonlocal row
            if row < height - 1:
                try:
                    stdscr.addstr(row, 0, text[:width], attr)
                except:
                    pass
                row += 1

        p("=== MALYSH v7.0 ORGANISM MESH ===", curses.A_BOLD)
        p(f"Health: {org_snapshot['cluster_health']} | Heal Ev: {org_snapshot['self_healing_events']}")
        p(f"Mode: {org_snapshot['autonomy_mode']} | Intel: {org_snapshot['intelligence_index']} [m: mode, TAB]")

        if current_port not in data_snapshot and data_snapshot:
            current_port = list(data_snapshot.keys())[0]

        node_info = data_snapshot.get(current_port, {
            "node_id": "Init...", "port": current_port, "clock": 0,
            "state": 0, "p": 0.0, "density": 0.0, "forecast": 0.0, 
            "entropy": 0.0, "depth": 10, "health": "UNKNOWN"
        })

        sparkline_data.append(node_info.get('state', 0))
        if len(sparkline_data) > 20: sparkline_data.pop(0)

        p(f"View: {node_info.get('node_id')} (Port {node_info.get('port')})")
        p(f"Clk: #{node_info.get('clock')} | St: {node_info.get('state')} | HLT: {node_info.get('health')}")
        p(f"Fc: {node_info.get('forecast')} | Ent: {node_info.get('entropy')} | GlobEnt: {org_snapshot['global_entropy']}")

        if height > 14:
            p("Organism Matrix (3x3):")
            st = node_info.get('state', 0)
            for r in range(3):
                r_str = "".join(["█" if ((st + r*3 + c) % 5) > 2 else "░" for c in range(3)])
                p(f"  [{r_str}]")

        spark_str = "".join(["█" if x > 23 else "." for x in sparkline_data])
        p(f"Pulse: [{spark_str}]")

        stdscr.refresh()
        time.sleep(0.1)

    for n in nodes_map.values():
        n.running = False

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nOrganism shut down.")
