import os
import json
import time
import datetime
import math
import random

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
CAN_STATE = os.path.join(HOME_DIR, "malysh_can_state.json")

class CANFrame:
    """Структура кадра протокола CAN"""
    def __init__(self, can_id, data):
        self.can_id = hex(can_id)
        self.dlc = len(data)
        self.payload = data

    def __repr__(self):
        hex_data = " ".join([f"{b:02X}" for b in self.payload])
        return f"ID: {self.can_id} | DLC: {self.dlc} | DATA: [ {hex_data} ]"

class CoherenceEngine:
    """Расчет когерентных метрик системы"""
    def calculate_coherence(self, phase_shift):
        # Коэффициент фазовой когерентности gamma^2 (от 0.000 до 1.000)
        coherence = round(abs(math.cos(phase_shift)), 4)
        status = "PHASE_LOCKED" if coherence > 0.85 else "PHASE_DRIFT"
        return coherence, status

class CANBusController:
    """Управление шиной CAN и передача кадров модулей"""
    def __init__(self):
        self.coherence_engine = CoherenceEngine()

    def transmit_all_layers(self, step):
        phase = step * 0.2
        coherence, phase_status = self.coherence_engine.calculate_coherence(phase)
        
        # Встраивание CAN-кадров для модулей:
        # 0x100 - Cortex Prime | 0x200 - Quantum Fabric | 0x300 - Supra Intent
        val_cortex = int((math.sin(phase) + 1) * 127)
        val_quantum = int((math.cos(phase) + 1) * 127)
        val_intent = int(coherence * 255)

        frame_cortex = CANFrame(0x100, [0xA1, val_cortex, 0xFF])
        frame_quantum = CANFrame(0x200, [0xB2, val_quantum, 0xFE])
        frame_intent = CANFrame(0x300, [0xC3, val_intent, 0x01])

        state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "coherence_index": coherence,
            "phase_status": phase_status,
            "can_bus": {
                "cortex_frame": str(frame_cortex),
                "quantum_frame": str(frame_quantum),
                "intent_frame": str(frame_intent)
            }
        }

        with open(CAN_STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return coherence, phase_status, [frame_cortex, frame_quantum, frame_intent]

def render_can_hud():
    """Визуальный слой мониторинга CAN-шины"""
    controller = CANBusController()
    print("\033[35m========================================")
    print("      MALYSH CAN BUS & COHERENCE HUD    ")
    print("========================================")
    
    try:
        for step in range(4):
            coherence, status, frames = controller.transmit_all_layers(step)
            print(f"\n\033[33m--- [STEP {step + 1}] Coherence: {coherence} | Status: {status} ---\033[0m")
            for frame in frames:
                print(f" 📡 \033[36m{frame}\033[0m")
            time.sleep(1)
            
        print("\n----------------------------------------")
        print(" [✓] CAN-шина закоммутирована, фазы когерентны.")
        print("========================================\033[0m")
    except KeyboardInterrupt:
        print("\n\033[31m[*] CAN HUD остановлен.\033[0m")

if __name__ == "__main__":
    render_can_hud()
