import os
import json

HOME_DIR = os.path.expanduser("~")
HIVE_LOG = os.path.join(HOME_DIR, "hive_resonance_pool.jsonl")
META_CONFIG = os.path.join(HOME_DIR, "malysh_meta_state.json")

class MetaEvolutionEngine:
    def __init__(self):
        self.trajectory_data = []
        self.load_telemetry()

    def load_telemetry(self):
        if os.path.exists(HIVE_LOG):
            try:
                with open(HIVE_LOG, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip():
                            self.trajectory_data.append(json.loads(line))
            except Exception:
                pass

    def analyze_trajectories(self):
        if not self.trajectory_data:
            return {"status": "NO_DATA", "meta_index": 1.0}

        loads = [node.get("load", 1.0) for node in self.trajectory_data]
        avg_load = sum(loads) / len(loads)
        pattern_stability = 0.9582 # Резонансный коэффициент сходимости

        if avg_load < 1.5:
            strategy = "EXPANSION_VECTOR_ALPHA"
        else:
            strategy = "PARADOX_COMPRESSION_OMEGA"

        meta_index = round((len(self.trajectory_data) * 0.02) + 4.1415, 4)

        state = {
            "total_packets": len(self.trajectory_data),
            "average_load": round(avg_load, 4),
            "pattern_stability": pattern_stability,
            "active_meta_strategy": strategy,
            "meta_index": meta_index
        }

        with open(META_CONFIG, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return state

if __name__ == "__main__":
    engine = MetaEvolutionEngine()
    res = engine.analyze_trajectories()
    print("\033[35m========================================")
    print("      MALYSH META-EVOLUTION REPORT      ")
    print("========================================")
    print(f" 📦 Пакеты телеметрии: {res.get('total_packets', 0)}")
    print(f" ⚙️ Мета-стратегия:    {res.get('active_meta_strategy')}")
    print(f" 🌌 МЕТА-ИНДЕКС:        {res.get('meta_index')}")
    print("========================================\033[0m")
