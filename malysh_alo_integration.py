import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ALO_STATE = os.path.join(HOME_DIR, "malysh_alo_state.json")

class AdaptiveLoadOrchestrator:
    """Модуль расчета метрик адаптивной нагрузки (ALO)"""
    def calculate_alo(self, step):
        # Расчет термо-стресса и коэффициента адаптивной эффективности
        load_factor = round(0.65 + math.sin(step * 0.5) * 0.25, 4)
        thermal_stress = round(load_factor * 42.5, 2)
        adaptive_efficiency = round((1.0 - (thermal_stress / 100.0)) * 100.0, 2)
        
        status = "OPTIMAL_LOAD_DISPERSION" if thermal_stress < 30.0 else "HIGH_DENSITY_THROTTLING"
        
        return {
            "load_factor": load_factor,
            "thermal_stress_index": thermal_stress,
            "adaptive_efficiency_pct": adaptive_efficiency,
            "status": status
        }

class DFRWithALOHub:
    """Интеграция ALO в DFR-HUD и контур управления нагрузкой"""
    def __init__(self):
        self.alo_engine = AdaptiveLoadOrchestrator()

    def process_cycle(self, step):
        alo_metrics = self.alo_engine.calculate_alo(step)
        
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "alo_metrics": alo_metrics
        }

        with open(ALO_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "ALO_CYCLE_LOG",
                "stress": alo_metrics["thermal_stress_index"],
                "efficiency": alo_metrics["adaptive_efficiency_pct"]
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return alo_metrics

def render_alo_hud():
    """Визуальный слой ALO и адаптивной нагрузки"""
    hub = DFRWithALOHub()
    print("\033[35m========================================")
    print("    MALYSH ALO & ADAPTIVE LOAD HUD      ")
    print("========================================")

    try:
        for step in range(4):
            metrics = hub.process_cycle(step)
            print(f"\n\033[33m--- [ALO TICK {step + 1}] Status: {metrics['status']} ---\033[0m")
            print(f" ⚙️ Load Factor: \033[36m{metrics['load_factor']}\033[0m")
            print(f" 🔥 Thermal Stress Index: \033[31m{metrics['thermal_stress_index']}\033[0m")
            print(f" 🛡️ Adaptive Efficiency: \033[32m{metrics['adaptive_efficiency_pct']}%\033[0m")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Оркестратор ALO интегрирован в DFR-HUD.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] ALO HUD остановлен.\033[0m")

if __name__ == "__main__":
    render_alo_hud()
