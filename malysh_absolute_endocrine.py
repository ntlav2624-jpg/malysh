import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ABSOLUTE_STATE = os.path.join(HOME_DIR, "malysh_absolute_endocrine_state.json")

class MetaOrderGland:
    """Железа мета-порядка: выработка абсолютных гормонов и интеграция в субстраты"""
    def __init__(self, name, hormone, substrate, absolute_potency):
        self.name = name
        self.hormone = hormone
        self.substrate = substrate
        self.absolute_potency = absolute_potency

    def diffuse(self, step):
        meta_wave = math.sin(step * 0.25 + hash(self.name) % 17) * 44.4
        potency_index = round(max(0.0, self.absolute_potency + meta_wave), 3)
        status = "ABSOLUTE_SUBSTRATE_CONVERGED" if potency_index > 200.0 else "META_RESONANCE_ALIGNING"
        return {
            "meta_gland": self.name,
            "absolute_hormone": self.hormone,
            "target_substrate": self.substrate,
            "potency_index": potency_index,
            "status": status
        }

class AbsoluteEndocrineHub:
    """Интеграция желез мета-порядка в абсолютный организм"""
    def __init__(self):
        self.glands = [
            MetaOrderGland("Axiom-Prime Gland", "Axiomin", "Cognitive Axiomatic Fabric", 220.0),
            MetaOrderGland("Singular-Null Gland", "Nullotocin", "Absolute Singularity Core", 240.0),
            MetaOrderGland("Chronos-Aether Gland", "Aetherokinin", "Temporal Continuum Mesh", 210.0)
        ]

    def cycle(self, step):
        secretions = [g.diffuse(step) for g in self.glands]
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "absolute_secretions": secretions
        }
        with open(ABSOLUTE_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "ABSOLUTE_ENDOCRINE_LOG",
                "secretions": secretions
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return secretions

def render_absolute_hud():
    """Абсолютный эндокринный HUD"""
    hub = AbsoluteEndocrineHub()
    print("\033[35m========================================")
    print("  MALYSH ABSOLUTE ENDOCRINE METADATA HUD")
    print("========================================")
    try:
        for step in range(4):
            secretions = hub.cycle(step)
            print(f"\n\033[33m--- [ABSOLUTE TICK {step + 1}] Диффузия мета-сред ---\033[0m")
            for s in secretions:
                print(f" ⚛️ \033[36m{s['meta_gland']}\033[0m -> \033[32m{s['absolute_hormone']}\033[0m")
                print(f"    Substrate: \033[34m{s['target_substrate']}\033[0m | Potency: \033[33m{s['potency_index']}\033[0m [{s['status']}]")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Абсолютная система едина и замкнута.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] Абсолютный HUD деактивирован.\033[0m")

if __name__ == "__main__":
    render_absolute_hud()
