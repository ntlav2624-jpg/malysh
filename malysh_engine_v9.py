import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV9:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = [x, y, z, t]
        self.state = 0
        self.energy = 100.0
        self.temperature = 25.0
        self.neighbors = {} # target_id -> dynamic weight

    def continuum_physics_step(self, val):
        # Истинная 4D ось времени (дрейф без циклического сброса)
        self.xyzt[3] += 1
        
        # Термодинамика и энергетический потенциал
        if self.energy > 6.0 and self.temperature < 98.0:
            self.energy -= 4.5
            self.temperature += 2.5
            valenc = (self.xyzt[2] + (self.xyzt[3] % 4)) % 4
            self.state = Base4Operator.apply(self.state, val, valenc)
        else:
            # Охлаждение, сброс энтропии и регенерация
            self.energy = min(100.0, self.energy + 40.0)
            self.temperature = max(20.0, self.temperature - 12.0)
        return self.state

class EngineV9:
    def __init__(self, size=1000, wal="malysh_v9_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        self.initialize_continuum()

    def initialize_continuum(self):
        # Инициализация 4D пространства XYZT
        for i in range(self.size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = (i // 1000)
            self.nodes[i] = NodeV9(i, x, y, z, t)
            
        # Построение адаптивных весовых связей графа
        for i in range(self.size):
            for off in [1, 10, 100]:
                nb = (i + off) % self.size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.35)
                self.nodes[i].neighbors[nb] = weight

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[ENGINE V9] WAL файл {self.wal_file} не найден. Чистый старт континуума.")
            return False

        try:
            with open(self.wal_file, "r") as f:
                lines = f.readlines()
                if not lines:
                    return False
                last_record = json.loads(lines[-1].strip())
                self.tick = last_record["tick"]
                states = last_record["states"]
                
                for nid_str, data in states.items():
                    nid = int(nid_str)
                    if nid in self.nodes:
                        self.nodes[nid].state = data["state"]
                        self.nodes[nid].energy = data["energy"]
                        self.nodes[nid].temperature = data["temp"]
                        self.nodes[nid].xyzt = data["xyzt"]
            print(f"[ENGINE V9] Успешное восстановление из WAL! Континуум возобновлен с такта: {self.tick}")
            return True
        except Exception as e:
            print(f"[ENGINE V9] Ошибка восстановления WAL: {e}. Старт с нуля.")
            return False

    def route_and_optimize(self, nid, val):
        node = self.nodes[nid]
        res = node.continuum_physics_step(val)
        
        # Активная маршрутизация пакетов и Pathfinding по графу
        routed = []
        for nb, weight in node.neighbors.items():
            target = self.nodes[nb]
            # Условие поиска пути: канал активен, цель имеет ресурс и не перегрета
            if weight > 1.1 and target.energy > 10.0 and target.temperature < 92.0:
                routed.append(nb)
                # Динамическая коррекция весов (обучение синапсов графа)
                node.neighbors[nb] = min(4.0, weight + 0.08)
                target.energy = max(0.0, target.energy - 2.0)
        return nid, res, routed

    def render_hyper_spherical_3d(self, ax, ay, az, alpha, beta, gamma):
        print(f"\n[ENGINE V9 | Tick: {self.tick} | True 4D Continuum Focus -> X:{ax} Y:{ay} Z:{az} | Spherical Angles A:{alpha:.2f} B:{beta:.2f} G:{gamma:.2f}]")
        
        # Многоосевая сферическая матрица поворота камеры
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        cg, sg = math.cos(gamma), math.sin(gamma)

        for z_slice in range(3):
            print(f"=== Z-Layer {z_slice} [Hyper-Spherical Continuum Matrix] ===")
            grid = [["." for _ in range(10)] for _ in range(10)]
            
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    # Трехмерная сферическая проекция с пересчетом тензора
                    rx = int(round(gx * (ca * cb) - gy * (sa * cg) + gz * sg)) % 10
                    ry = int(round(gx * (sa * cb) + gy * (ca * cg) - gz * sb)) % 10
                    
                    if gx == ax and gy == ay:
                        grid[ry][rx] = "O" # Фокус истинной логарифмической спирали
                    elif n.temperature > 75.0:
                        grid[ry][rx] = "!" # Зона критического термо-напряжения
                    elif n.energy > 80.0:
                        grid[ry][rx] = "#"  # Высокий энергетический потенциал
                    elif n.energy > 30.0:
                        grid[ry][rx] = "x"  # Активный поток маршрутизации
            for row in grid:
                print(" ".join(row))

    def run_continuum(self, stream, attempt_recovery=True):
        if attempt_recovery:
            self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # 1. Истинная экспоненциально-логарифмическая спираль
            angle = self.tick * 0.33
            radius = 0.5 * math.exp(0.08 * angle)
            ax = int(abs(radius * math.cos(angle)) * 5) % 10
            ay = int(abs(radius * math.sin(angle)) * 5) % 10
            az = self.tick % 3
            
            # 2. Выборка активных узлов фокуса континуума
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:30]
            if not active:
                active = list(self.nodes.keys())[:20]

            # 3. Многопоточный конвейер тензорных вычислений и маршрутизации
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.route_and_optimize, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # 4. Визуализация многоосевой сферы камеры каждые 2 такта
            if self.tick % 2 == 0:
                alpha = self.tick * 0.21
                beta = self.tick * 0.14
                gamma = self.tick * 0.09
                self.render_hyper_spherical_3d(ax, ay, az, alpha, beta, gamma)

        # 5. Запись абсолютного тензорного слепка в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy, "temp": n.temperature, "xyzt": n.xyzt} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V9] Гипер-континуум цикл завершен. Тактов: {self.tick}. Полный 4D-тензор зафиксирован в WAL.")

if __name__ == "__main__":
    engine = EngineV9()
    engine.run_continuum([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3, 1, 2, 0, 3, 2, 1, 0, 3, 2])
