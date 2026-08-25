import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV8:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = [x, y, z, t]
        self.state = 0
        self.energy = 100.0
        self.temperature = 25.0
        self.neighbors = {} # target_id -> weight

    def tensor_physics_step(self, val):
        # Полноценная 4D тензорная эволюция координаты T
        self.xyzt[3] = (self.xyzt[3] + 1) % 16
        
        # Термодинамика и энтропийный потенциал
        if self.energy > 8.0 and self.temperature < 95.0:
            self.energy -= 4.0
            self.temperature += 2.2
            valenc = (self.xyzt[2] + (self.xyzt[3] % 4)) % 4
            self.state = Base4Operator.apply(self.state, val, valenc)
        else:
            # Охлаждение, сброс энтропии и регенерация
            self.energy = min(100.0, self.energy + 35.0)
            self.temperature = max(20.0, self.temperature - 10.0)
        return self.state

class EngineV8:
    def __init__(self, size=1000, wal="malysh_v8_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        self.initialize_grid()

    def initialize_grid(self):
        # Инициализация полного 4D тензорного пространства XYZT
        for i in range(self.size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = (i // 1000) % 16
            self.nodes[i] = NodeV8(i, x, y, z, t)
            
        # Построение адаптивных весовых связей графа
        for i in range(self.size):
            for off in [1, 10, 100]:
                nb = (i + off) % self.size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.3)
                self.nodes[i].neighbors[nb] = weight

    def recover_from_wal(self):
        """Инженерный модуль восстановления состояния из WAL"""
        if not os.path.exists(self.wal_file):
            print(f"[ENGINE V8] WAL файл {self.wal_file} не найден. Запуск с чистого листа.")
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
            print(f"[ENGINE V8] Успешное восстановление из WAL! Тик возобновлен с отметки: {self.tick}")
            return True
        except Exception as e:
            print(f"[ENGINE V8] Ошибка восстановления WAL: {e}. Сброс инициализации.")
            return False

    def route_and_sync(self, nid, val):
        node = self.nodes[nid]
        res = node.tensor_physics_step(val)
        
        # Активная маршрутизация потоков по графу
        routed = []
        for nb, weight in node.neighbors.items():
            target = self.nodes[nb]
            if weight > 1.15 and target.energy > 12.0 and target.temperature < 90.0:
                routed.append(nb)
                node.neighbors[nb] = min(3.8, weight + 0.06)
                target.energy = max(0.0, target.energy - 1.8)
        return nid, res, routed

    def render_spherical_orbital_3d(self, ax, ay, az, alpha, beta, gamma):
        print(f"\n[ENGINE V8 | Tick: {self.tick} | 4D Tensor Focus -> X:{ax} Y:{ay} Z:{az} | Spherical Angles A:{alpha:.2f} B:{beta:.2f} G:{gamma:.2f}]")
        
        # Трехмерная матрица сферной проекции орбитальной камеры (Multi-axis rotation)
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        cg, sg = math.cos(gamma), math.sin(gamma)

        for z_slice in range(3):
            print(f"=== Z-Layer {z_slice} [Spherical Orbital Matrix] ===")
            grid = [["." for _ in range(10)] for _ in range(10)]
            
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    # Полноценный трехмерный поворот координат камеры
                    rx = int(round(gx * (ca * cb) - gy * (sa * cg) + gz * sg)) % 10
                    ry = int(round(gx * (sa * cb) + gy * (ca * cg) - gz * sb)) % 10
                    
                    if gx == ax and gy == ay:
                        grid[ry][rx] = "O" # Фокус истинной логарифмической спирали
                    elif n.temperature > 70.0:
                        grid[ry][rx] = "!" # Критический перегрев ядра
                    elif n.energy > 75.0:
                        grid[ry][rx] = "#"  # Высокий потенциал
                    elif n.energy > 35.0:
                        grid[ry][rx] = "x"  # Активный поток
            for row in grid:
                print(" ".join(row))

    def run_nexus(self, stream, attempt_recovery=True):
        if attempt_recovery:
            self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # 1. Истинная экспоненциально-логарифмическая спираль
            angle = self.tick * 0.32
            radius = 0.55 * math.exp(0.075 * angle)
            ax = int(abs(radius * math.cos(angle)) * 5) % 10
            ay = int(abs(radius * math.sin(angle)) * 5) % 10
            az = self.tick % 3
            
            # 2. Выборка активных узлов фокуса
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:28]
            if not active:
                active = list(self.nodes.keys())[:20]

            # 3. Конкурентный многопоточный конвейер вычислений
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.route_and_sync, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # 4. Визуализация сферы орбитальной камеры каждые 2 такта
            if self.tick % 2 == 0:
                alpha = self.tick * 0.18
                beta = self.tick * 0.12
                gamma = self.tick * 0.08
                self.render_spherical_orbital_3d(ax, ay, az, alpha, beta, gamma)

        # 5. Запись абсолютного гипер-слепка в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy, "temp": n.temperature, "xyzt": n.xyzt} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V8] Гипер-нексус цикл завершен. Тактов: {self.tick}. Полный тензорный слепок зафиксирован в WAL.")

if __name__ == "__main__":
    engine = EngineV8()
    # Запускаем серию тактов (при повторном запуске система подхватит WAL автоматически)
    engine.run_nexus([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3, 1, 2, 0, 3, 2, 1, 0])
