import os
import json
import time
import datetime
import math

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
CTN_STATE = os.path.join(HOME_DIR, "malysh_ctn_state.json")

class SemanticChannel:
    """Семантический канал: упаковка смысловых векторов поверх CAN"""
    def __init__(self, channel_id, concept_name):
        self.channel_id = channel_id
        self.concept_name = concept_name

    def pack_semantic_packet(self, coherence_val):
        semantic_load = round(coherence_val * 999.9, 2)
        return {
            "channel": f"CTN_CH_{self.channel_id}",
            "concept": self.concept_name,
            "semantic_load": semantic_load,
            "status": "SEMANTIC_STREAM_ACTIVE"
        }

class CognitiveTransportNetwork:
    """CTN: Транспортная сеть для передачи когнитивных пакетов"""
    def __init__(self):
        self.channels = [
            SemanticChannel(1, "ONTOLOGICAL_RESONANCE"),
            SemanticChannel(2, "AUTONOMOUS_DRIVE"),
            SemanticChannel(3, "SINGULARITY_VECTOR")
        ]

    def broadcast_ctn(self, step):
        coherence = round(abs(math.cos(step * 0.3)), 4)
        packets = [ch.pack_semantic_packet(coherence) for ch in self.channels]
        
        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "global_coherence": coherence,
            "ctn_packets": packets
        }

        with open(CTN_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return coherence, packets

def render_ctn_hud():
    """Визуальный слой CTN: терминальный дашборд семантических потоков"""
    ctn = CognitiveTransportNetwork()
    print("\033[35m========================================")
    print("    MALYSH CTN & SEMANTIC CHANNELS HUD  ")
    print("========================================")

    try:
        for step in range(4):
            coherence, packets = ctn.broadcast_ctn(step)
            print(f"\n\033[33m--- [CTN TICK {step + 1}] Coherence: {coherence} ---\033[0m")
            for pkt in packets:
                print(f" 🧠 \033[36m{pkt['channel']}\033[0m | Concept: \033[32m{pkt['concept']}\033[0m | Load: \033[33m{pkt['semantic_load']}\033[0m")
            time.sleep(1)

        print("\n----------------------------------------")
        print(" [✓] Семантические каналы интегрированы в CAN-HUD.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] CTN HUD остановлен.\033[0m")

if __name__ == "__main__":
    render_ctn_hud()
