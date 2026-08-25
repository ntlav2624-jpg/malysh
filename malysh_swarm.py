import time
import json
import random

class SwarmNode:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def send_message(self, receiver, msg_type, payload):
        message = {
            "sender": self.name,
            "receiver": receiver,
            "timestamp": time.time(),
            "msg_type": msg_type,
            "payload": payload
        }
        return json.dumps(message)

# Инициализация роя агентов Малыша
scout = SwarmNode("Malysh_Alpha", "Scout")
analyst = SwarmNode("Malysh_Beta", "Analyst")

if __name__ == "__main__":
    print("--- [Swarm-архитектура Малыша активирована] ---")
    payload_sample = {
        "state_id": "Harmonic_sync",
        "metrics": {"expectation": 0.2, "variance": 0.05, "entropy": 1.5},
        "temperature": 1.1
    }
    
    msg = scout.send_message("Broadcast", "PROPOSAL", payload_sample)
    print("Передан пакет рою:")
    print(json.dumps(json.loads(msg), indent=2, ensure_ascii=False))
