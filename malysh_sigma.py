import json
import math
import random
import time

class SubSwarmNode:
    def __init__(self, node_id, specialization):
        self.node_id = node_id
        self.specialization = specialization
        self.local_entropy = 1.0

    def work(self):
        self.local_entropy = random.uniform(0.5, 2.5)
        return {"node": self.node_id, "spec": self.specialization, "entropy": self.local_entropy}

class SigmaStrategicAgent:
    def __init__(self):
        self.sub_swarms = [
            SubSwarmNode("Sub_Alpha", "Log_Management"),
            SubSwarmNode("Sub_Beta", "Test_Runner"),
            SubSwarmNode("Sub_Gamma", "Patch_Evolution")
        ]
        self.time_map = []
        self.strategic_horizon = 0

    def evaluate_global_strategy(self, swarm_states):
        avg_entropy = sum(s["entropy"] for s in swarm_states) / len(swarm_states)
        if avg_entropy > 1.8:
            return "СТРАТЕГИЯ: Глубокая стабилизация и очистка"
        else:
            return "СТРАТЕГИЯ: Ускоренная мутация и рост"

    def update_time_resonance(self, global_phase, strategy):
        record = {
            "step": self.strategic_horizon,
            "phase": round(global_phase, 3),
            "strategy": strategy,
            "timestamp": time.time()
        }
        self.time_map.append(record)
        if len(self.time_map) > 8:
            self.time_map.pop(0)
        self.strategic_horizon += 1

    def render_time_resonance_map(self):
        map_str = "\n[ Резонансная Карта Времени (Σ-Tensor) ]\n"
        for entry in self.time_map:
            bar = "▓" * int(entry["phase"] * 3)
            map_str += f"T+{entry['step']} | Фаза: {entry['phase']:5.2f} | {bar} | {entry['strategy']}\n"
        return map_str

if __name__ == "__main__":
    sigma = SigmaStrategicAgent()
    print("--- [Σ-Стратегический Над-Агент и Под-Рои Активированы] ---")
    print("Для остановки нажми Ctrl + C\n")
    
    try:
        for cycle in range(4):
            swarm_reports = [node.work() for node in sigma.sub_swarms]
            global_phase = sum(r["entropy"] for r in swarm_reports) / len(swarm_reports) * (math.pi / 2)
            
            strategy = sigma.evaluate_global_strategy(swarm_reports)
            sigma.update_time_resonance(global_phase, strategy)
            
            print(f"=== Стратегический Цикл {cycle+1} ===")
            for r in swarm_reports:
                print(f"  Под-рой [{r['node']} : {r['spec']}] -> Энтропия: {r['entropy']:.3f}")
            print(f"Макро-решение : {strategy}")
            print(sigma.render_time_resonance_map())
            print("=" * 60)
            
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n--- [Σ-Агент деактивирован пользователем] ---")
