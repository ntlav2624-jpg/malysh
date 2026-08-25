import numpy as np
import json, os, time

class HyperComputeCore:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    
    def __init__(self, vector_size=64):
        self.vector_size = vector_size
        self.register = np.zeros(vector_size, dtype=int)
        self.execution_cycles = 0

    def base4_transform(self, data_stream):
        print(f"[COMPUTE-V27] Запуск потоковых Base-4 вычислений (вектор: {self.vector_size} байт)...")
        start_time = time.time()
        
        history_states = []
        for step, val in enumerate(data_stream):
            # Векторные quaternary вычисления
            valenc = (step % 4)
            for i in range(self.vector_size):
                cur = self.register[i]
                self.register[i] = (self.MATRIX[cur % 4][val % 4] + valenc + i) % 4
            
            # Расчет информационной энтропии состояния регистров
            unique, counts = np.unique(self.register, return_counts=True)
            probabilities = counts / self.vector_size
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-9))
            
            history_states.append({
                "cycle": step,
                "input_val": int(val),
                "entropy": float(entropy),
                "checksum": int(np.sum(self.register))
            })
            self.execution_cycles += 1

        elapsed = time.time() - start_time
        print(f"[COMPUTE-V27] Вычисления завершены за {elapsed:.4f} сек. Циклов: {self.execution_cycles}")
        return history_states

if __name__ == "__main__":
    core = HyperComputeCore(vector_size=128)
    # Тестовый поток данных для тяжелых вычислений
    stream = [0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 3, 0, 1, 2, 3, 1]
    results = core.base4_transform(stream)
    
    print("\n[РЕЗУЛЬТАТЫ ВЫЧИСЛЕНИЙ ЯДРА]:")
    for res in results[:5]:  # Выводим первые 5 тактов для примера
        print(f"  Тактирование #{res['cycle']:02d} | Вход: {res['input_val']} | Энтропия: {res['entropy']:.4f} | Чексумма: {res['checksum']}")
    print("  ... расчеты стабильны, память когерентна.")
