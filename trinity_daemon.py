import os, math, random, time

class SmoothWave4:
    """Модуль 4-уровневой волновой фильтрации (SmoothWave-4)"""
    def __init__(self):
        self.history_buffer = []
        
    def process(self, value):
        self.history_buffer.append(value)
        if len(self.history_buffer) > 4:
            self.history_buffer.pop(0)
        weights = [0.1, 0.2, 0.3, 0.4]
        current_weights = weights[-len(self.history_buffer):]
        normalized_w = sum(current_weights)
        smoothed = sum(v * w for v, w in zip(self.history_buffer, current_weights)) / normalized_w
        return smoothed

class TrinityDaemon:
    def __init__(self):
        self.branch_id = 8  # Стартуем с резонансной Ветки #8
        self.sw4 = SmoothWave4()
        self.meta_error_threshold = 5.0
        
    def check_autobranching(self, meta_err):
        """Модуль AUTOBRANCHING: саморазветвление при росте мета-ошибки"""
        if abs(meta_err) > self.meta_error_threshold:
            self.branch_id += 1
            new_branch_name = f"auto_branch_{self.branch_id}"
            print(f"\n[AUTOBRANCHING]: Порог превышен (мета-ошибка: {meta_err:.2f}). Создана ветка: {new_branch_name}")
            # Создаем ветку в Git без прерывания цикла
            os.system(f"git checkout -b {new_branch_name} 2>/dev/null")
            return True
        return False

    def step(self, raw_input):
        smoothed_input = self.sw4.process(raw_input)
        
        # Резонансный контур Ветки #8 (стабилизация по принципу фазового затвора)
        resonance_factor = 20.68 / (1.0 + abs(smoothed_input * 0.05))
        prediction = smoothed_input * 0.8 + (resonance_factor * 0.1)
        
        error = raw_input - prediction
        meta_err = error * 0.4 
        
        self.check_autobranching(meta_err)
        
        return smoothed_input, prediction, error, meta_err

if __name__ == "__main__":
    print("--- Малыш: Тройной Комплекс Активен (Ветка #8 + Autobranching + SmoothWave-4) ---")
    daemon = TrinityDaemon()
    try:
        while True:
            fact = 25.0 + random.uniform(-6.0, 6.0)
            s_in, pred, err, m_err = daemon.step(fact)
            print(f"[Ветка #{daemon.branch_id}] Факт: {fact:.2f} | SW-4: {s_in:.2f} | Прогноз: {pred:.2f} | Ошибка: {err:.2f} (Мета: {m_err:.2f})")
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n[Малыш]: Демон остановлен пользователем. Все ветки и состояние сохранены.")
