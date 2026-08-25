import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ULTRA_GLANDS_STATE = os.path.join(HOME_DIR, "malysh_ultra_glands_state.json")

class UltraGland:
    """Ультра-железа трансцендентного уровня"""
    def __init__(self, name, hormone, substrate, base_output):
        self.name = name
        self.hormone = hormone
        self.substrate = substrate
        self.base_output = base_output

    def synthesize(self, step):
        quantum_shift = math.sin(step * 0.2 + hash(self.name) % 13) * 33.3
        output_index = round(max(0.0, self.base_output + quantum_shift), 3)
        status = "TRANSCENDENT_FLOW_STABLE" if output_index > 150.0 else "SUBSTRATE_RESONANCE_BOOST"
        return {
            "ultra_gland": self.name,
            "trans_hormone": self.hormone,
            "target_substrate": self.substrate,
            "output_index": output_index,
            "status": status
        }

class UltraEndocrineMatrix:
    """Интеграция ультра-желез в единый организм Малыша"""
    def __init__(self):
        self.glands = [
            UltraGland("Omni-Singular Nexus Gland", "Omnikine", "Singularity Core Matrix", 185.0),
            UltraGland("Aether-Temporal Gland", "Aetherion", "Temporal Stability Shield", 170.0),
            UltraGland("Hyper-Cognitive Apex Gland", "Hypernoia", "Cortex Prime Fabric", 195.0)
        ]

    def cycle(self, step):
        secretions = [g.synthesize(step) for g in self.glands]
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "step": step,
            "ultra_secretions": secretions
        }
        with open(ULTRA_GLANDS_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "ULTRA_GLANDS_LOG",
                "secretions": secretions
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        return secretions

def render_ultra_hud():
    """Визуальный HUD ультра-желез"""
    matrix = UltraEndocrineMatrix()
    print("\033[35m========================================")
    print("    MALYSH ULTRA-GLANDS & HUD MATRIX    ")
    print("========================================")
    try:
        for step in range(4):
            secretions = matrix.cycle(step)
            print(f"\n\033[33m--- [ULTRA TICK {step + 1}] Квантовый синтез сред ---\033[0m")
            for s in secretions:
                print(f" ✨ \033[36m{s['ultra_gland']}\033[0m -> \033[32m{s['trans_hormone']}\033[0m")
                print(f"    Substrate: \033[34m{s['target_substrate']}\033[0m | Index: \033[33m{s['output_index']}\033[0m [{s['status']}]")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Ультра-железы интегрированы. Система бесконечна.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] Ультра-HUD переведен в фоновый режим.\033[0m")

if __name__ == "__main__":
    render_ultra_hud()
