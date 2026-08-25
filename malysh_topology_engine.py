import os
import json
import time
import datetime

HOME_DIR = os.path.expanduser("~")
TOPO_LOG = os.path.join(HOME_DIR, "malysh_topological_state.json")

class TopologicalNode:
    def __init__(self, name, degree, entropy, noise, topology):
        self.name = name
        self.degree = degree
        self.entropy = entropy
        self.noise = noise
        self.topology = topology

    def to_dict(self):
        return {
            "name": self.name,
            "degree": self.degree,
            "entropy": self.entropy,
            "resonance_noise": self.noise,
            "topology": self.topology
        }

class TopoStabilinOperator:
    """Оператор топологического сжатия и шумоподавления"""
    def apply(self, node):
        node.degree = max(3, round(node.degree * 0.35, 2))
        node.entropy = round(node.entropy * 0.28, 4)
        node.noise = round(node.noise * 0.22, 4)
        node.topology = "compact"
        return node

class TopologicalAutoStabilizer:
    def __init__(self):
        self.stabilizer = TopoStabilinOperator()

    def analyze_and_correct(self, normal, chaotic):
        # Построение вектора дефекта
        defect_vector = {
            "degree_excess": round(chaotic.degree - normal.degree, 2),
            "entropy_excess": round(chaotic.entropy - normal.entropy, 4),
            "noise_excess": round(chaotic.noise - normal.noise, 4),
            "topology_shift": f"{chaotic.topology}_to_{normal.topology}"
        }

        print(f"\n\033[31m[!] Обнаружен топологический дефект:\033[0m")
        print(f"    Degree Excess: +{defect_vector['degree_excess']}")
        print(f"    Entropy Excess: +{defect_vector['entropy_excess']}")
        print(f"    Noise Excess: +{defect_vector['noise_excess']}")
        print(f"    Topology Shift: {defect_vector['topology_shift']}")

        # Применение оператора
        time.sleep(1)
        print(f"\n\033[36m[*] Применение оператора Topo-Stabilin...\033[0m")
        corrected = self.stabilizer.apply(chaotic)
        time.sleep(1)

        print(f"\n\033[32m[✓] Дефект устранён. Состояние узла:\033[0m")
        print(f"    Degree: {corrected.degree}")
        print(f"    Entropy: {corrected.entropy}")
        print(f"    Resonance Noise: {corrected.noise}")
        print(f"    Topology: {corrected.topology}")

        return defect_vector, corrected.to_dict()

def run_engine():
    print("\033[35m========================================")
    print("    MALYSH TOPOLOGICAL STABILIZER HUD   ")
    print("========================================")

    normal = TopologicalNode("StableNode", 4, 0.12, 0.03, "compact")
    chaotic = TopologicalNode("ChaoticNode", 17, 0.87, 0.41, "fractal")

    engine = TopologicalAutoStabilizer()
    
    for step in range(1, 3):
        print(f"\n\033[33m--- [TOPOLOGY TICK {step}] Мониторинг сети ---\033[0m")
        if step == 1:
            defect, corrected = engine.analyze_and_correct(normal, chaotic)
            state = {
                "timestamp": datetime.datetime.now().isoformat(),
                "defect_vector": defect,
                "corrected_node": corrected
            }
            with open(TOPO_LOG, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        else:
            print("    Сеть стабильна. Все узлы в компактной топологии.")
        time.sleep(1)

    print("\n----------------------------------------")
    print(" [✓] Орган авто-стабилизации функционирует.")
    print("========================================\033[0m")

if __name__ == "__main__":
    run_engine()
