import math
import random

class Project7PredictorG:
    def __init__(self, dimensions=7):
        self.dim = dimensions
        self.r7_weights = [1.0 / (i + 1) for i in range(self.dim)]
        self.history = []

    def _resonance_transform(self, history_window):
        if not history_window:
            return [0.0] * self.dim
            
        phase_vectors = [0.0] * self.dim
        for idx, val in enumerate(history_window):
            for d in range(self.dim):
                frequency = (d + 1) * 0.61803398875
                phase_vectors[d] += val * math.sin(idx * frequency) * self.r7_weights[d]
                
        return phase_vectors

    def predict(self, sequence):
        self.history = sequence
        window_size = min(len(sequence), 14)
        window = sequence[-window_size:]
        
        r7_state = self._resonance_transform(window)
        
        resonance_sum = sum(r7_state)
        base_trend = window[-1] if window else 0.0
        
        raw_prediction = base_trend + math.tanh(resonance_sum) * (window[-1] - window[-2] if len(window) > 1 else 1.0)
        
        return raw_prediction, r7_state

    def update_weights(self, error, r7_state):
        learning_rate = 0.01
        for d in range(self.dim):
            self.r7_weights[d] += learning_rate * error * r7_state[d]
            self.r7_weights[d] = max(0.01, min(10.0, self.r7_weights[d]))

if __name__ == "__main__":
    predictor = Project7PredictorG()
    stream = [10, 12, 11, 15, 14, 18, 17]
    print(f"Входная последовательность: {stream}")
    
    predicted_val, r7_field = predictor.predict(stream)
    print(f"Спрогнозированное значение (x_t+1): {predicted_val:.4f}")
    print(f"Состояние пространства R_7: {[round(w, 3) for w in r7_field]}")
    
    actual_next = 21
    error = actual_next - predicted_val
    predictor.update_weights(error, r7_field)
    print(f"Ошибка шага: {error:.4f}. Веса R_7 обновлены.")
