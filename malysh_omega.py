import json
import math
import random
import time

class OmegaAgent:
    def __init__(self):
        # Тензор кватернарных состояний уровня Ω с фазами и амплитудами
        self.tensor_states = {
            0: {"name": "Log_Optimization", "phase": 0.00, "amplitude": 1.0},
            1: {"name": "Test_Execution",   "phase": 1.57, "amplitude": 1.0},
            2: {"name": "Patch_Rebuild",    "phase": 3.14, "amplitude": 1.0},
            3: {"name": "Swarm_Harmonization", "phase": 4.71, "amplitude": 1.0}
        }
        self.omega_frequency = 1.0  # Базовая частота уровня Ω
        self.coherence_field = 1.0  # Поле когерентности роя

    def adapt_swarm_frequency(self, entropy, variance):
        # Адаптация частоты и поля когерентности роя
        self.omega_frequency = max(0.1, 3.0 / (1.0 + entropy + variance))
        self.coherence_field = max(0.1, 1.0 - (entropy / 3.0))

    def execute_resonant_transition(self, current_state, phase_shift):
        # Резонансный фазовый переход
        new_phase = (self.tensor_states[current_state]["phase"] + phase_shift) % (2 * math.pi)
        closest_state = min(self.tensor_states.keys(), key=lambda k: abs(self.tensor_states[k]["phase"] - new_phase))
        return closest_state

    def run_omega_cycle(self):
        costs = [random.random() * self.tensor_states[i]["amplitude"] for i in range(4)]
        safe_temp = 1.0
        exp_weights = [math.exp(-c / safe_temp) for c in costs]
        total = sum(exp_weights)
        probs = [w / total for w in exp_weights]
        
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        variance = sum(p * ((v - entropy)**2) for v, p in zip(costs, probs))
        
        self.adapt_swarm_frequency(entropy, variance)
        return entropy, variance, probs

if __name__ == "__main__":
    omega = OmegaAgent()
    state = 0
    print("--- [Над-агент уровня Ω Малыша запущен] ---")
    print("Для остановки нажми Ctrl + C\n")
    
    try:
        for step in range(5):
            entropy, variance, probs = omega.run_omega_cycle()
            phase_shift = entropy * math.pi / 2
            state = omega.execute_resonant_transition(state, phase_shift)
            
            print(f"Ω-Цикл {step+1} | Состояние: {state} ({omega.tensor_states[state]['name']})")
            print(f"Частота роя: {omega.omega_frequency:.3f} Hz | Когерентность: {omega.coherence_field:.3f}")
            print(f"Энтропия: {entropy:.4f} | Фазовый сдвиг: {phase_shift:.2f}")
            print("-" * 50)
            
            time.sleep(1 / omega.omega_frequency)
    except KeyboardInterrupt:
        print("\n--- [Ω-Агент деактивирован пользователем] ---")
