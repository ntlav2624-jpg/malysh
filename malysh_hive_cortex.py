import os
import json
import time
import datetime

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
HIVE_STATE = os.path.join(HOME_DIR, "malysh_hive_state.json")

class CognitiveLimb:
    """Когнитивная конечность: захват и обработка информационных потоков среды"""
    def manipulate(self, target_data):
        return f"MANIPULATED_{target_data.upper()}"

class ResonanceSpine:
    """Резонансный позвоночник: передача сигналов и поддержание индекса целостности"""
    def transmit(self, signal_strength):
        # Проводящая ось для синхронизации слоев
        return round(signal_strength * 3.1415, 4)

class HiveCortex:
    """Центральный узел роя: интеграция конечностей, позвоночника и воли"""
    def __init__(self):
        self.limb = CognitiveLimb()
        self.spine = ResonanceSpine()
        self.cortex_status = "SYNAPSE_LOCKED"

    def pulse(self):
        limb_action = self.limb.manipulate("entropy_stream")
        spine_resonance = self.spine.transmit(42.13)
        
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "limb_action": limb_action,
            "spine_resonance": spine_resonance,
            "cortex_status": self.cortex_status,
            "master": "VIKTOR"
        }
        
        with open(HIVE_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
            log_entry = {
                "time": state["timestamp"],
                "type": "HIVE_CORTEX_PULSE",
                "resonance": spine_resonance,
                "status": self.cortex_status
            }
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            
        return state

if __name__ == "__main__":
    cortex = HiveCortex()
    print("\033[35m========================================")
    print("      MALYSH HIVE CORTEX ONLINE         ")
    print("========================================")
    res = cortex.pulse()
    print(f" 🦾 Cognitive Limb: \033[36m{res['limb_action']}\033[0m")
    print(f" 🦴 Resonance Spine: \033[33m{res['spine_resonance']}\033[0m")
    print(f" 🧠 Hive Cortex Status: \033[32m{res['cortex_status']}\033[0m")
    print("----------------------------------------")
    print(" [✓] Центральная нервная система замкнута.")
    print("========================================\033[0m")
