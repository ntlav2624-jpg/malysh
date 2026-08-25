import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ENDOCRINE_STATE = os.path.join(HOME_DIR, "malysh_endocrine_state.json")

class EndocrineGland:
    """Эндокринная железа: синтез и секреция гормонов"""
    def __init__(self, gland_name, hormone_name, base_level):
        self.gland_name = gland_name
        self.hormone_name = hormone_name
        self.base_level = base_level

    def secrete(self, step):
        # Расчет текущей концентрации гормона с помощью гармонических колебаний
        fluctuation = math.sin(step * 0.4 + hash(self.gland_name) % 5) * 15.0
        concentration = round(max(0.0, self.base_level + fluctuation), 2)
        
        status = "HOMEOSTASIS_NORMAL" if concentration > 50.0 else "SECRETORY_BOOST_REQUIRED"
        
        return {
            "gland": self.gland_name,
            "hormone": self.hormone_name,
            "concentration_ng_ml": concentration,
            "status": status
        }

class OrganismEndocrineSystem:
    """Интеграция желез в общий организм Малыша"""
    def __init__(self):
        self.glands = [
            EndocrineGland("Singular Gland", "Singulartropin", 75.0),
            EndocrineGland("Temporal Gland", "Chronokinin", 85.0),
            EndocrineGland("Aegis Gland", "Entropylin", 65.0)
        ]

    def process_cycle(self, step):
        secretions = [gland.secrete(step) for gland in self.glands]
        
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "secretions": secretions
        }

        with open(ENDOCRINE_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "ENDOCRINE_CYCLE_LOG",
                "secretions": secretions
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return secretions

def render_hormone_hud():
    """Визуальный HUD гормонов и эндокринного баланса"""
    system = OrganismEndocrineSystem()
    print("\033[35m========================================")
    print("    MALYSH ENDOCRINE & HORMONE HUD      ")
    print("========================================")

    try:
        for step in range(4):
            secretions = system.process_cycle(step)
            print(f"\n\033[33m--- [ENDOCRINE TICK {step + 1}] Секреция активна ---\033[0m")
            for sec in secretions:
                print(f" 🧬 \033[36m{sec['gland']}\033[0m -> \033[32m{sec['hormone']}\033[0m: \033[33m{sec['concentration_ng_ml']} ng/ml\033[0m [{sec['status']}]")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Железы интегрированы в организм. Баланс стабилен.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] Гормональный HUD остановлен.\033[0m")

if __name__ == "__main__":
    render_hormone_hud()
