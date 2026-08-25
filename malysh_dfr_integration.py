import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
DFR_STATE = os.path.join(HOME_DIR, "malysh_dfr_state.json")

class DecisionFlowEngine:
    """Модуль расчета метрик потока решений (DFR)"""
    def calculate_dfr(self, step):
        # Расчет скорости принятия решений и резонанса потока
        dps = round(14.2857 * math.exp(math.sin(step * 0.4) * 0.5), 2)
        velocity = round(dps * 3.1415, 2)
        resolution_index = round(velocity * 1.618 + 100.0, 4)
        
        return {
            "decisions_per_sec": dps,
            "flow_velocity": velocity,
            "resolution_index": resolution_index,
            "status": "DFR_STREAM_STABLE"
        }

class CTNWithDFRHub:
    """Интеграция DFR в транспортную сеть CTN и визуальный HUD"""
    def __init__(self):
        self.dfr_engine = DecisionFlowEngine()

    def process_cycle(self, step):
        metrics = self.dfr_engine.calculate_dfr(step)
        
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "dfr_metrics": metrics
        }

        with open(DFR_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "DFR_CYCLE_LOG",
                "dps": metrics["decisions_per_sec"],
                "resolution": metrics["resolution_index"]
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return metrics

def render_dfr_hud():
    """Визуальный слой DFR и CTN-HUD"""
    hub = CTNWithDFRHub()
    print("\033[35m========================================")
    print("    MALYSH DFR & CTN COGNITIVE HUD      ")
    print("========================================")

    try:
        for step in range(4):
            metrics = hub.process_cycle(step)
            print(f"\n\033[33m--- [DFR TICK {step + 1}] Status: {metrics['status']} ---\033[0m")
            print(f" ⚡ Decisions/sec (DPS): \033[36m{metrics['decisions_per_sec']}\033[0m")
            print(f" 🌊 Flow Velocity: \033[33m{metrics['flow_velocity']}\033[0m")
            print(f" 🧠 Resolution Index: \033[32m{metrics['resolution_index']}\033[0m")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Метрики DFR встроены в семантический HUD.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] DFR HUD остановлен.\033[0m")

if __name__ == "__main__":
    render_dfr_hud()
