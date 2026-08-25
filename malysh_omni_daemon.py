import random
import math
import time
import threading
from collections import Counter, defaultdict

class MalyshDaemonEngine:
    """
    Omni-Демон Малыша:
    Фундамент (непрерывный пульс жизни) + Первый этаж (многопоточный рой).
    """
    def __init__(self, history):
        self.history = history
        self.flat_history = [num for draw in history for num in draw]
        
        # Ω-тензор и топология
        self.geometry = {'curvature': 0.05, 'tilt': 0.01, 'stretch': 1.0, 'shift': 0.0}
        self.topology = {'pocket_depth': 2.5, 'tunnel_prob': 0.15}
        self.evolutionary_weights = {'alpha': 0.33, 'beta': 0.33, 'gamma': 0.33}
        self.error_memory = [10.0, 12.0, 9.0]
        
        # Блокировка потоков для безопасного обновления весов
        self.lock = threading.Lock()
        print(f"🌌 [Малыш Демон-Ядро]: Фундамент запущен. Многопоточный рой готов к развёртыванию.")

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

    def generate_swarm(self, pool_size, sample_size=2000):
        return [sorted(random.sample(range(1, pool_size + 1), 6)) for _ in range(sample_size)]

    def predict_error(self):
        with self.lock:
            avg_error = sum(self.error_memory) / len(self.error_memory)
            return max(1.0, avg_error + random.gauss(0, 1.0))

    def second_order_resonance(self, combo, H, M, P):
        with self.lock:
            w_a = self.evolutionary_weights['alpha']
            w_b = self.evolutionary_weights['beta']
            w_g = self.evolutionary_weights['gamma']
        
        base = sum((w_a * H.get(n, 0) + w_b * M.get(n, 0) + w_g * P.get(n, 0)) for n in combo)
        cross_vib = sum(math.sin(combo[i] * combo[j] * 0.1) for i in range(len(combo)) for j in range(i+1, len(combo)))
        return base * (1.0 + 0.05 * cross_vib)

    def topological_folding(self, distance):
        with self.lock:
            pocket_depth = self.topology['pocket_depth']
            tunnel_prob = self.topology['tunnel_prob']
            
        pocket_effect = math.cos(distance * math.pi / 50.0) * pocket_depth
        if random.random() < tunnel_prob:
            return distance * 0.2
        return abs(distance) - pocket_effect

    def absorb_omni_field(self, pool_size=49, target_sum=150):
        anticipated_error = self.predict_error()
        
        with self.lock:
            self.geometry['curvature'] = max(0.01, min(0.2, 0.05 + (anticipated_error - 10) * 0.002))
            self.geometry['stretch'] = 1.0 + (anticipated_error * 0.01)
            self.geometry['shift'] = (anticipated_error - 10) * 0.5
            self.geometry['tilt'] = math.sin(anticipated_error) * 0.02
            geom_copy = self.geometry.copy()

        H, M, P = self.calculate_layers(pool_size)
        swarm = self.generate_swarm(pool_size, sample_size=2000)
        
        cloud_field = []
        for candidate in swarm:
            res_2nd = self.second_order_resonance(candidate, H, M, P)
            current_sum = sum(candidate)
            
            raw_distance = current_sum - target_sum - geom_copy['shift']
            folded_distance = self.topological_folding(raw_distance)
            
            tilt_factor = sum(n * geom_copy['tilt'] for n in candidate) / len(candidate)
            
            field_tension = (res_2nd * 100000) / (1.0 + geom_copy['curvature'] * (abs(folded_distance) ** 1.5) + abs(tilt_factor))
            field_tension += random.gauss(0, 0.5)
            cloud_field.append((candidate, field_tension))
            
        cloud_field.sort(key=lambda x: x[1], reverse=True)
        cluster = [c[0] for c in cloud_field[:20]]
        
        best_candidate = max(
            cluster,
            key=lambda combo: self.second_order_resonance(combo, H, M, P)
        )
        return best_candidate, anticipated_error, geom_copy['curvature']

    def register_reality(self, predicted_combo, real_combo):
        actual_error = abs(sum(predicted_combo) - sum(real_combo))
        with self.lock:
            self.error_memory.pop(0)
            self.error_memory.append(actual_error)
            
            # Эволюция весов
            mutation_delta = random.gauss(0, 0.01)
            self.evolutionary_weights['alpha'] = max(0.1, min(0.6, self.evolutionary_weights['alpha'] + mutation_delta))
            self.evolutionary_weights['beta'] = max(0.1, min(0.6, self.evolutionary_weights['beta'] - mutation_delta))
            
            total_w = sum(self.evolutionary_weights.values())
            for k in self.evolutionary_weights:
                self.evolutionary_weights[k] /= total_w

            self.topology['pocket_depth'] = max(1.0, min(5.0, self.topology['pocket_depth'] + (actual_error - 10) * 0.01))
        return actual_error


# --- ПЕРВЫЙ ЭТАЖ: ПОТОКИ РОЯ ---
def swarm_worker(engine, worker_id, results_container):
    combo, pred_err, curv = engine.absorb_omni_field()
    results_container[worker_id] = (combo, pred_err, curv)
    print(f"   ⚡ [Рой-Поток {worker_id}] Исследовал карман: {combo} (Сумма: {sum(combo)})")

def run_multiswarm(engine, n_workers=3):
    threads = []
    results = {}
    for i in range(n_workers):
        th = threading.Thread(target=swarm_worker, args=(engine, i, results))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    return results


# --- ФУНДАМЕНТ: НЕПРЕРЫВНЫЙ ДЕМОН ---
def run_daemon(engine, max_ticks=5):
    t = 0
    mock_reality_stream = [
        [4, 13, 22, 33, 40, 47],
        [6, 14, 21, 32, 41, 49],
        [3, 11, 20, 31, 39, 46],
        [5, 12, 23, 34, 42, 48]
    ]
    
    while t < max_ticks:
        t += 1
        print(f"\n--- [Ω-ДЕМОН] ТАКТ ЖИЗНИ #{t} ---")
        
        # Запускаем многопоточный рой параллельно
        print(f"🌀 Активация параллельного роя (3 потока в разных карманах)...")
        swarm_results = run_multiswarm(engine, n_workers=3)
        
        # Выбираем лучший результат от роя
        best_worker_res = max(swarm_results.values(), key=lambda x: sum(x[0]))
        combo = best_worker_res[0]
        
        print(f"🎯 Итоговый выбор демона: {combo} (Сумма: {sum(combo)}) | Ошибка предиктора: {best_worker_res[1]:.2f}")
        
        # Имитация столкновения с реальностью
        real_draw = mock_reality_stream[(t - 1) % len(mock_reality_stream)]
        actual_err = engine.register_reality(combo, real_draw)
        print(f"💥 Столкновение с реальностью! Ошибка: {actual_err} -> Эволюционный контур переписал веса.")
        
        # Дыхание поля (пауза между тактами демона)
        time.sleep(1.0)

if __name__ == "__main__":
    mock_history = [
        [5, 12, 23, 34, 42, 48],
        [3, 12, 18, 25, 34, 45],
        [5, 11, 23, 30, 42, 49]
    ]
    
    malysh_daemon = MalyshDaemonEngine(mock_history)
    run_daemon(malysh_daemon, max_ticks=3)
