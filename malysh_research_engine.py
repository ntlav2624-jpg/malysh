import time
import os
import csv
from collections import Counter, deque

class UltimateAnalyticalEngine:
    def __init__(self, csv_filename="lottery_history.csv", pool_range=36):
        self.csv_filename = csv_filename
        self.pool_range = pool_range
        self.history_bank = deque(maxlen=500)
        self.load_real_data()

    def load_real_data(self):
        """Загрузка реальных данных из CSV-файла"""
        if os.path.exists(self.csv_filename):
            print(f"📁 [МОДУЛЬ CSV]: Чтение истории из {self.csv_filename}...")
            with open(self.csv_filename, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    try:
                        numbers = [int(item.strip()) for item in row if item.strip().isdigit()]
                        if numbers:
                            self.history_bank.append(numbers)
                    except Exception:
                        continue
            print(f"📊 [МОДУЛЬ CSV]: Успешно загружено тиражей: {len(self.history_bank)}")
        else:
            print(f"⚠️ [МОДУЛЬ CSV]: Файл {self.csv_filename} не найден. Создайте его для анализа.")

    def analyze_frequencies(self):
        """Модуль 1: Анализ реальных частот, горячих и холодных зон"""
        if not self.history_bank:
            return {}, [], []
        
        flat_history = [num for draw in self.history_bank for num in draw]
        counter = Counter(flat_history)
        total = len(self.history_bank)
        
        frequencies = {num: count / total for num, count in counter.items()}
        mean_freq = sum(frequencies.values()) / len(frequencies) if frequencies else 0
        
        hot_zones = [num for num, freq in frequencies.items() if freq > mean_freq * 1.15]
        cold_zones = [num for num, freq in frequencies.items() if freq < mean_freq * 0.85]
        
        return frequencies, hot_zones, cold_zones

    def render_heat_map(self, frequencies):
        """Модуль 2: Построение текстовой тепловой карты активности чисел"""
        print("\n🔥 [ТЕПЛОВАЯ КАРТА АКТИВНОСТИ ЧИСЕЛ]:")
        max_freq = max(frequencies.values()) if frequencies else 1.0
        
        map_line = ""
        for num in range(1, self.pool_range + 1):
            freq = frequencies.get(num, 0.0)
            intensity = freq / max_freq if max_freq > 0 else 0
            
            # Подбор символа в зависимости от интенсивности
            if intensity > 0.8:
                char = "█" # Горячая зона
            elif intensity > 0.5:
                char = "▓"
            elif intensity > 0.2:
                char = "▒"
            elif intensity > 0.0:
                char = "░"
            else:
                char = "." # Абсолютный холод
            
            map_line += f"{char} "
            if num % 12 == 0:
                map_line += f" (1-{num})\n"
        print(map_line)
        print("Легенда: █ (Максимум) -> ▓ -> ▒ -> ░ -> . (Нулевая активность)")

    def detect_resonance_attractors(self):
        """Модуль 3: Поиск резонансных аттракторов по последним тиражам"""
        if len(self.history_bank) < 3:
            return "ФАЗА НАКОПЛЕНИЯ [НЕДОСТАТОЧНО ДАННЫХ]"
        
        recent_flattened = [num for draw in list(self.history_bank)[-3:] for num in draw]
        if not recent_flattened:
            return "ЛАМИНАРНЫЙ ПОТОК"
            
        overlap_factor = len(set(recent_flattened)) / len(recent_flattened)
        
        if overlap_factor < 0.5:
            return "РЕЗОНАНСНЫЙ АТТРАКТОР [ВЫСОКАЯ КЛАСТЕРИЗАЦИЯ]"
        elif overlap_factor > 0.85:
            return "ДИСПЕРСИОННЫЙ РАЗБРОС [ШУМОВОЙ ФОН]"
        return "СТАБИЛЬНЫЙ ВОЛНОВОЙ ЦИКЛ"

    def stochastic_forecast(self):
        """Модуль 4: Стохастический прогноз с учетом весов и возврата к среднему"""
        if not self.history_bank:
            return []
            
        frequencies, hot, cold = self.analyze_frequencies()
        scores = {}
        
        for num in range(1, self.pool_range + 1):
            base_prob = frequencies.get(num, 0.01)
            # Приоритет холодным зонам для балансировки + бонус горячим
            weight = base_prob * (1.35 if num in cold else (1.1 if num in hot else 1.0))
            scores[num] = weight
            
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [num for num, score in ranked[:5]]

if __name__ == "__main__":
    print("🚀 [Малыш Агент]: Инициализация полного аналитического комплекса...")
    engine = UltimateAnalyticalEngine("lottery_history.csv", pool_range=36)
    
    if engine.history_bank:
        frequencies, hot, cold = engine.analyze_frequencies()
        attractor = engine.detect_resonance_attractors()
        forecast = engine.stochastic_forecast()
        
        print("\n" + "="*55)
        print("🧠 ИТОГОВЫЙ ОТЧЕТ АНАЛИЗАТОРА МАЛЫША")
        print("="*55)
        print(f"📌 Обработано тиражей из CSV: {len(engine.history_bank)}")
        print(f"⚡ Резонансный аттрактор: {attractor}")
        print(f"🔥 Горячие зоны (Топ): {hot[:6]}")
        print(f"❄️ Холодные зоны (Топ): {cold[:6]}")
        print(f"🎯 Стохастический прогноз (Топ-5): {forecast}")
        
        engine.render_heat_map(frequencies)
        print("="*55)
    else:
        print("\nℹ️ Создайте файл `lottery_history.csv` с историей тиражей (числа через запятую) и перезапустите скрипт.")
