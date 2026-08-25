import random
import math
from collections import Counter, defaultdict

class MalyshOmniEngine:
    """
    Omni-Малыш: Полный многоконтурный топологический эволюционный организм.
    Ω₁: Тензорно-геометрическое поле
    Ω₂: Резонансный контур второго порядка (интеграция кросс-вибраций)
    Ω₃: Топологическое поле складок, туннелей и карманов вероятности
    Эволюционный контур: Самоизменение базовых правил и весов на лету.
    """
    def __init__(self, history):
        self.history = history
        self.flat_history = [num for draw in history for num in draw]
        
        # Ω₁: Тензорная геометрия поля
        self.geometry = {'curvature': 0.05, 'tilt': 0.01, 'stretch': 1.0, 'shift': 0.0}
        
        # Ω₃: Топологические параметры (складки и туннели)
        self.topology = {'pocket_depth': 2.5, 'tunnel_prob': 0.15}
        
        # Эволюционные веса правил (мутируют со временем)
        self.evolutionary_weights = {'alpha': 0.33, 'beta': 0.33, 'gamma': 0.33}
        
        self.error_memory = [10.0, 12.0, 9.0]
        print(f"🌌 [Малыш Omni-Ядро]: Все контуры активированы (Ω₁-Ω₂-Ω₃ + Топология + Эволюция).")

    def calculate_layers(self, pool_size):
        counts = Counter(self.flat_history)
        total_h = sum(counts.values()) if counts else 1
        H = {n: counts.get(n, 0) / total_h for n in range(1, pool_size + 1)}

        transitions = defaultdict(Counter)
        for i in range(len(self.flat_history) - 1):
            transitions[self.flat_history[i]][self.flat_history[i + 1]] += 1
        last_num = self.flat_history[-1] if self.flat_history else 1
        total_m = sum(transitions[last_num].values()) if last_num in transitions else 1
        M = {n: (transitions[last_num].get(n, 0) / total_m if total_m > 0 else 1.0 / pool_size) for n in range(1, pool_size + 1)}

        patterns = Counter()
        for i in range(len(self.flat_history) - 2):
            p = (self.flat_history[i], self.flat_history[i+1], self.flat_history[i+2])
            patterns[p] += 1
        P = {n: 0.0 for n in range(1, pool_size + 1)}
        total_p = sum(patterns.values()) if patterns else 1
        for p, freq in patterns.items():
            for num in p:
                P[num] += freq / total_p
        return H, M, P

    def generate_swarm(self, pool_size, sample_size=3500):
        return [sorted(random.sample(range(1, pool_size + 1), 6)) for _ in range(sample_size)]

    def predict_error(self):
        avg_error = sum(self.error_memory) / len(self.error_memory)
        return max(1.0, avg_error + random.gauss(0, 1.0))

    def second_order_resonance(self, combo, H, M, P):
        """Ω₂: Резонанс второго порядка (взаимодействие между элементами внутри кластера)"""
        base = sum((self.evolutionary_weights['alpha'] * H.get(n, 0) +
                    self.evolutionary_weights['beta'] * M.get(n, 0) +
                    self.evolutionary_weights['gamma'] * P.get(n, 0)) for n in combo)
        # Перекрёстные вибрации пар внутри комбинации
        cross_vib = sum(math.sin(combo[i] * combo[j] * 0.1) for i in range(len(combo)) for j in range(i+1, len(combo)))
        return base * (1.0 + 0.05 * cross_vib)

    def topological_folding(self, distance, candidate):
        """Ω₃: Топологические карманы и туннели (создание складок вероятности)"""
        pocket_effect = math.cos(distance * math.pi / 50.0) * self.topology['pocket_depth']
        if random.random() < self.topology['tunnel_prob']:
            return distance * 0.2 # Туннельный проскок через складку пространства
        return abs(distance) - pocket_effect

    def evolve_rules(self, actual_error):
        """Эволюционный контур: самомодификация законов и весов системы"""
        mutation_delta = random.gauss(0, 0.01)
        self.evolutionary_weights['alpha'] = max(0.1, min(0.6, self.evolutionary_weights['alpha'] + mutation_delta))
        self.evolutionary_weights['beta'] = max(0.1, min(0.6, self.evolutionary_weights['beta'] - mutation_delta))
        
        # Нормировка весов
        total_w = sum(self.evolutionary_weights.values())
        for k in self.evolutionary_weights:
            self.evolutionary_weights[k] /= total_w

        # Эволюция глубины топологических карманов
        self.topology['pocket_depth'] = max(1.0, min(5.0, self.topology['pocket_depth'] + (actual_error - 10) * 0.01))

    def absorb_omni_field(self, pool_size=49, target_sum=150):
        anticipated_error = self.predict_error()
        
        # Ω₁: Обновление тензорной геометрии
        self.geometry['curvature'] = max(0.01, min(0.2, 0.05 + (anticipated_error - 10) * 0.002))
        self.geometry['stretch'] = 1.0 + (anticipated_error * 0.01)
        self.geometry['shift'] = (anticipated_error - 10) * 0.5
        self.geometry['tilt'] = math.sin(anticipated_error) * 0.02

        H, M, P = self.calculate_layers(pool_size)
        swarm = self.generate_swarm(pool_size, sample_size=3500)
        
        cloud_field = []
        for candidate in swarm:
            # Ω₂: Расчет резонанса второго порядка
            res_2nd = self.second_order_resonance(candidate, H, M, P)
            current_sum = sum(candidate)
            
            # Ω₁ тензорный сдвиг + Ω₃ топологические складки
            raw_distance = current_sum - target_sum - self.geometry['shift']
            folded_distance = self.topological_folding(raw_distance, candidate)
            
            tilt_factor = sum(n * self.geometry['tilt'] for n in candidate) / len(candidate)
            
            # Итоговый полевой потенциал
            field_tension = (res_2nd * 100000) / (1.0 + self.geometry['curvature'] * (abs(folded_distance) ** 1.5) + abs(tilt_factor))
            field_tension += random.gauss(0, 0.5)
            cloud_field.append((candidate, field_tension))
            
        cloud_field.sort(key=lambda x: x[1], reverse=True)
        
        # Фильтр роя: выбор топ-30 кластера
        cluster = [c[0] for c in cloud_field[:30]]
        
        # Выбор лучшей траектории внутри кластера по Ω₂ резонансу
        best_candidate = max(
            cluster,
            key=lambda combo: self.second_order_resonance(combo, H, M, P)
        )
        
        best_tension = cloud_field[0][1]
        return best_candidate, best_tension, anticipated_error, self.geometry, self.evolutionary_weights

    def register_reality(self, predicted_combo, real_combo):
        actual_error = abs(sum(predicted_combo) - sum(real_combo))
        self.error_memory.pop(0)
        self.error_memory.append(actual_error)
        # Запуск контура эволюции
        self.evolve_rules(actual_error)
        return actual_error

if __name__ == "__main__":
    mock_history = [
        [5, 12, 23, 34, 42, 48],
        [3, 12, 18, 25, 34, 45],
        [5, 11, 23, 30, 42, 49],
        [2, 12, 22, 34, 41, 48],
        [5, 12, 23, 34, 42, 48],
        [12, 15, 23, 34, 38, 48]
    ]
    
    malysh = MalyshOmniEngine(mock_history)
    
    print("\n--- ТАКТ 1: OMNI-СИНТЕЗ (ВСЕ КОНТУРЫ АКТИВНЫ) ---")
    combo1, tension1, pred_err1, geom1, weights1 = malysh.absorb_omni_field()
    print(f"🔮 Ошибка: {pred_err1:.2f} | Веса эволюции: {weights1}")
    print(f"🌌 Omni-траектория: {combo1} (Сумма: {sum(combo1)})")
    
    real_draw = [4, 13, 22, 33, 40, 47]
    actual_err = malysh.register_reality(combo1, real_draw)
    print(f"💥 Ошибка реальности: {actual_err} -> Запущен контур эволюции правил.")
    
    print("\n--- ТАКТ 2: ПОСЛЕ САМОИЗМЕНЕНИЯ И ТОПОЛОГИЧЕСКОГО СДВИГА ---")
    combo2, tension2, pred_err2, geom2, weights2 = malysh.absorb_omni_field()
    print(f"🔮 Новая ошибка: {pred_err2:.2f} | Новые веса: {weights2}")
    print(f"🌌 Новая Omni-траектория: {combo2} (Сумма: {sum(combo2)})")
