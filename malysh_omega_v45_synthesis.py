import json
import os
import time
import numpy as np

class Base4Resonance:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def transform(cls, val1, val2):
        return cls.MATRIX[val1 % 4][val2 % 4]

class TotalOrganismNexus:
    def __init__(self):
        self.wal_file = "symbiosis_history.jsonl"
        self.tick = 0
        
    def append_wal(self, data):
        with open(self.wal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
    def execute_cycle(self):
        self.tick += 1
        entropy = os.urandom(1)[0]
        b4_signal = Base4Resonance.transform(entropy, self.tick)
        
        # 4D Проекция (XYZ + T)
        spatial_4d = [
            round(float(np.sin(self.tick * 0.1)), 4),
            round(float(np.cos(self.tick * 0.1)), 4),
            round(float(self.tick) * 0.05, 4),
            int(entropy)
        ]
        
        payload = {
            "tick": self.tick,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base4_signal": b4_signal,
            "projection_4d": spatial_4d,
            "status": "TOTAL_SYNTHESIS_ACTIVE"
        }
        
        self.append_wal(payload)
        print(f"[NEXUS-V45] Такт {self.tick:02d} | Base-4: {b4_signal} | 4D: {spatial_4d[:2]}... | WAL записан")

    def run(self, cycles=10):
        print("[NEXUS-V45] Запуск тотального синтеза организма...")
        for _ in range(cycles):
            self.execute_cycle()
            time.sleep(0.3)
        print(f"[NEXUS-V45] Цикл завершен. История зафиксирована в {self.wal_file}")

if __name__ == "__main__":
    nexus = TotalOrganismNexus()
    nexus.run(cycles=12)
