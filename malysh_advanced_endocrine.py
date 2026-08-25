import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ADVANCED_ENDOCRINE_STATE = os.path.join(HOME_DIR, "malysh_advanced_endocrine_state.json")

class SpecializedGland:
    """Специализированная эндокринная железа организма"""
    def __init__(self, name, hormone, baseline, amplification):
        self.name = name
        self.hormone = hormone
        self.baseline = baseline
        self.amplification = amplification

    def secrete(self, step):
        wave = math.sin(step * 0.5 + hash(self.name) % 7) * self.amplification
        level = round(max(0.0, self.baseline + wave), 2)
        status = "STABLE_HOMEOSTASIS" if level > (self.baseline * 0.8) else "DEFICIT_TRIGGERED"
        return {
            "gland": self.name,
            "hormone": self.hormone,
            "level_ppm": level,
            "status": status
        }

class AdvancedEndocrineSystem:
    """Организм с расширенным набором желез"""
    def __init__(self):
        self.glands = [
            SpecializedGland("Synaptic Gland", "Neuromodulin", 120.0, 25.0),
            SpecializedGland("Resonance Gland", "Harmonix", 95.0, 18.0),
            SpecializedGland("Core Gland", "Vitaline", 150.0, 30.0),
            SpecializedGland("Entropy Gland", "Apolytropin", 80.0, 15.0)
        ]

    def cycle(self, step):
        secretions = [g.secrete(step) for g in self.glands]
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "secretions": secretions
        }
        with open(ADVANCED_ENDOCRINE_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "ADVANCED_ENDOCRINE_LOG",
                "secretions": secretions
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return secretions

def render_advanced_hormone_hud():
    """Визуальный HUD расширенной эндокринной системы"""
    system = AdvancedEndocrineSystem()
    print("\033[35m========================================")
    print("    MALYSH ADVANCED HORMONE HUD & GLANDS")
    print("========================================")
    try:
        for step in range(4):
            secretions = system.cycle(step)
            print(f"\n\033[33m--- [TICK {step + 1}] Секреция био-активных сред ---\033[0m")
            for s in secretions:
                print(f" 🧬 \033[36m{s['gland']}\033[0m -> \033[32m{s['hormone']}\033[0m: \033[33m{s['level_ppm']} ppm\033[0m [{s['status']}]")
            time.sleep(1)
            
        print("\n----------------------------------------")
        print(" [✓] Все железы интегрированы в организм.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] Гормональный HUD переведен в фон.\033[0m")

if __name__ == "__main__":
    render_advanced_hormone_hud()
