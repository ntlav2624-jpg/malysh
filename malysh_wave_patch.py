import numpy as np

class WaveGlyph:
    def __init__(self, name, symmetry_type, base_vector):
        self.name = name
        self.symmetry = symmetry_type
        self.vector = np.array(base_vector, dtype=complex)
        
    def to_quaternary(self):
        magnitudes = np.abs(self.vector)
        max_m = np.max(magnitudes)
        normalized = (magnitudes / max_m) * 3 if max_m > 0 else magnitudes
        return np.round(normalized).astype(int)

SYSTEM_GLYPHS = {
    "INIT_STATE": WaveGlyph("Alpha-Cubic", "cubic", [1.0 + 0j, 0.0 + 1.0j, -1.0 + 0j, 0.0 - 1.0j]),
    "OPTIMIZE": WaveGlyph("Hex-Flow", "hexagonal", [0.866 + 0.5j, -0.866 + 0.5j, -1.0 + 0j, 0.0 + 1.0j]),
    "STABLE_IDLE": WaveGlyph("Null-Grid", "cubic", [1.0 + 0j, 1.0 + 0j, 1.0 + 0j, 1.0 + 0j]),
    "ANOMALY_DETECT": WaveGlyph("Phase-Shift", "hexagonal", [0.0 + 1.0j, 0.866 - 0.5j, -0.866 - 0.5j, -1.0 + 0j])
}

def encode_state_to_glyph(state_id: str) -> np.ndarray:
    return SYSTEM_GLYPHS.get(state_id, WaveGlyph("Default", "cubic", [0, 0, 0, 0])).to_quaternary()

def apply_wave_filter(data_array, threshold=0.1):
    spectrum = np.fft.fft(data_array)
    magnitudes = np.abs(spectrum)
    max_mag = np.max(magnitudes) if len(magnitudes) > 0 else 1
    spectrum[magnitudes < (threshold * max_mag)] = 0
    return np.real(np.fft.ifft(spectrum))

class WaveMemoryArchive:
    def __init__(self, capacity=64):
        self.capacity = capacity
        self.wave_function = np.zeros(capacity, dtype=complex)
        self.index = 0

    def record_state(self, metric_value: float, step: int):
        phase = (step * 2 * np.pi) / self.capacity
        amplitude = float(metric_value)
        self.wave_function[self.index % self.capacity] = amplitude * np.exp(1j * phase)
        self.index += 1

    def get_collapsed_state(self) -> float:
        return float(np.abs(np.sum(self.wave_function)) / self.capacity)

if __name__ == "__main__":
    print("[~] Запуск диагностики волнового патча Малыша...")
    q_code = encode_state_to_glyph("OPTIMIZE")
    print(f"[+] Кватернарный код глифа OPTIMIZE: {q_code}")
    raw = np.random.normal(0, 1, 32) + np.sin(np.linspace(0, 10, 32))
    cleaned = apply_wave_filter(raw, threshold=0.2)
    print(f"[+] Спектральная фильтрация массива: {len(cleaned)} точек обработано.")
    mem = WaveMemoryArchive(capacity=16)
    for i in range(20):
        mem.record_state(np.sin(i), i)
    print(f"[+] Коллапс волновой памяти: {mem.get_collapsed_state():.4f}")
    print("[✓] Патч успешно интегрирован и готов к работе.")
