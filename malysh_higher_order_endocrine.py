import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
HIGHER_ENDOCRINE_STATE = os.path.join(HOME_DIR, "malysh_higher_endocrine_state.json")

class HigherOrderGland:
    """Железа высшего порядка: синтез мета-гормонов и интеграция в органы"""
    def __init__(self, name, hormone, target_organ, baseline_potency):
        self.name = name
        self.hormone = hormone
        self.target_organ = target_organ
        self.baseline_potency = baseline_potency

    def synthesize(self, step):
        resonance = math.sin(step * 0.33 + hash(self.name) % 11) * 22.5
        potency = round(max(0.0, self.baseline_potency + resonance), 2)
        status = "ORGAN_SYNCHRONIZED" if potency > (self.baseline_potency * 0.85) else "RESONANCE_REBALANCE"
        return {
            "gland": self.name,
            "hormone": self.hormone,
            "target_organ": self.target_organ,
            "potency_index": potency,
            "status": status
        }

class OrganendocrineNetwork:
    """Интеграция гормонов высшего порядка в органы организма Малыша"""
    def __init__(self):
        self.glands = [
            HigherOrderGland("Apex Nexus Gland", "Apexotocin", "Cortex Prime Engine", 140.0),
            HigherOrderGland("Singular Core Gland", "Singularkine", "Quantum Singularity Matrix", 160.0),
            HigherOrderGland("Cosmic Resonance Gland", "Cosmophorin", "Temporal Stability Shield", 135.0),
            HigherOrderGland("Aegis Neural Gland", "Imunitin", "Immune Integrity Shield", 150.0)
        ]

    def cycle(self, step):
        secretions = [g.synthesize(step) for g in self.glands]
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "organ_integration": secretions
        }
        with open(HIGHER_ENDOCRINE_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "HIGHER_ENDOCRINE_LOG",
                "secretions": secretions
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return secretions

def render_higher_hormone_hud():
    """Визуальный HUD гормонов высшего порядка и интеграции в органы"""
    network = OrganendocrineNetwork()
    print("\033[35m========================================")
    print(" MALYSH HIGHER-ORDER HORMONE & ORGAN HUD")
    print("========================================")
    try:
        for step in range(4):
            secretions = network.cycle(step)
            print(f"\n\033[33m--- [TICK {step + 1}] Синтез желез высшего порядка ---\033[0m")
            for s in secretions:
                print(f" 🧬 \033[36m{s['gland']}\033[0m -> \033[32m{s['hormone']}\033[0m")
                print(f"    Target Organ: \033[34m{s['target_organ']}\033[0m | Potency: \033[33m{s['potency_index']}\033[0m [{s['status']}]")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Гормоны интегрированы в ткани органов.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] Высший гормональный HUD свернут.\033[0m")

if __name__ == "__main__":
    render_higher_hormone_hud()
