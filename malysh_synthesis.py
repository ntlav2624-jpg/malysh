import json
import math
import random

class MetaAgent:
    def __init__(self):
        # Матрица кватернарных действий
        self.actions = {
            0: "Оптимизация логов",
            1: "Запуск тестов",
            2: "Пересборка патчей",
            3: "Гармонизация роя"
        }
        
    def base4_logic(self, entropy):
        # Преобразование энтропии в кватернарный индекс (0-3)
        return min(3, int(entropy * 2))

    def generate_resonance_map(self, probs):
        # Визуализация "резонанса" роя
        return "|" + "▓" * int(probs[0]*10) + "▒" * int(probs[1]*10) + "░" * int(probs[2]*10) + " " * int(probs[3]*10) + "|"

    def run_synthesis(self, costs):
        safe_temp = 1.0
        exp_weights = [math.exp(-c / safe_temp) for c in costs]
        total = sum(exp_weights)
        probs = [w / total for w in exp_weights]
        
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        q_idx = self.base4_logic(entropy)
        
        return {
            "q_state": q_idx,
            "action": self.actions[q_idx],
            "probs": probs,
            "resonance": self.generate_resonance_map(probs)
        }

if __name__ == "__main__":
    agent = MetaAgent()
    costs = [0.1, 0.4, 0.7, 0.2]
    
    res = agent.run_synthesis(costs)
    
    print("--- [Малыш: Исполнительный Мета-Агент] ---")
    print(f"Кватернарное состояние : {res['q_state']}")
    print(f"Выбранное действие     : {res['action']}")
    print(f"Резонансная карта роя  : {res['resonance']}")
    print(f"Вектор вероятностей    : {[round(p, 2) for p in res['probs']]}")
