import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV7:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = [x, y, z, t]
        self.state = 0
        self.energy = 100.0
        self.temperature = 25.0
        self.neighbors = {} # target_id -> weight

    def physics_and_time_step(self, val):
        # 4D волновой сдвиг координаты T
        self.xyzt[3] = (self.xyzt[3] + 1) % 12
        
        # Термодинамика и энергетический потенциал
        if self.energy > 10.0 and self.temperature < 90.0:
            self.energy -= 3.5
            self.temperature += 2.0
            valenc = (self.xyzt[2] + self.xyzt[3]) % 4
            self.state = Base4Operator.apply(self.state, val, valenc)
        else:
            # Охлаждение и регенерация энергии
            self.energy = min(100.0, self.energy + 30.0)
            self.temperature = max(20.0, self.temperature - 8.0)
        return self.state

class EngineV7:
    def __init__(self, size=1000, wal="malysh_v7_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        
        # Инициализация полного пространства XYZT
        for i in range(size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = (i // 1000) % 12
            self.nodes[i] = NodeV7(i, x, y, z, t)
            
        # Построение адаптивных весовых связей графа
        for i in range(size):
            for off in [1, 10, 100]:
                nb = (i + off) % size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.25)
                self.nodes[i].neighbors[nb] = weight

    def route_packet_and_flux(self, nid, val):
        node = self.nodes[nid]
        res = node.physics_and_time_step(val)
        
        # Интеллектуальная маршрутизация потоков по графу
        routed = []
        for nb, weight in node.neighbors.items():
            target = self.nodes[nb]
            if weight > 1.2 and target.energy > 15.0 and target.temperature < 85.0:
                routed.append(nb)
                # Динамическая коррекция весов каналов (обучение структуры)
                node.neighbors[nb] = min(3.5, weight + 0.05)
                target.energy = max(0.0, target.energy - 1.5)
        return nid, res, routed

    def render_dynamic_orbital_3d(self, ax, ay, az, cam_alpha, cam_beta):
        print(f"\n[ENGINE V7 | Tick: {self.tick} | True Log-Spiral 4D Focus -> X:{ax} Y:{ay} Z:{az} | Alpha:{cam_alpha:.2f} Beta:{cam_beta:.2f}]")
        
        # Сложная матрица динамической орбитальной камеры
        cos_a, sin_a = math.cos(cam_alpha), math.sin(cam_alpha)
        cos_b, sin_b = math.cos(cam_beta), math.sin(cam_beta)

        for z_slice in range(3):
            print(f"=== Z-Layer {z_slice} [Dynamic Orbital Manifold] ===")
            grid = [["." for _ in range(10)] for _ in range(10)]
            
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    # Двухканальное орбитальное вращение проекции
                    rx = int(round(gx * cos_a - gy * sin_a * cos_b)) % 10
                    ry = int(round(gx * sin_a + gy * cos_a * cos_b)) % 10
                    
                    if gx == ax and gy == ay:
                        grid[ry][rx] = "O" # Фокус логарифмической спирали
                    elif n.temperature > 65.0:
                        grid[ry][rx] = "!" # Критический перегрев
                    elif n.energy > 70.0:
                        grid[ry][rx] = "#"  # Высокий потенциал
                    elif n.energy > 30.0:
                        grid[ry][rx] = "x"  # Активный поток
            for row in grid:
                print(" ".join(row))

    def run_ultimate_manifold(self, stream):
        for val in stream:
            self.tick += 1
            
            # 1. Истинная экспоненциально-логарифмическая спираль
            angle = self.tick * 0.35
            radius = 0.5 * math.exp(0.08 * angle)
            ax = int(abs(radius * math.cos(angle)) * 5) % 10
            ay = int(abs(radius * math.sin(angle)) * 5) % 10
            az = self.tick % 3
            
            # 2. Выборка активных узлов фокуса спирали
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:26]
            if not active:
                active = list(self.nodes.keys())[:18]

            # 3. Многопоточный конвейер физики, маршрутизации и 4D-времени
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.route_packet_and_flux, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # 4. Визуализация с динамической орбитальной камерой каждые 2 такта
            if self.tick % 2 == 0:
                alpha = self.tick * 0.2
                beta = self.tick * 0.1
                self.render_dynamic_orbital_3d(ax, ay, az, alpha, beta)

        # 5. Фиксация абсолютного гипер-слепка в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy, "temp": n.temperature, "xyzt": n.xyzt} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V7] Абсолютный гипер-монолитный цикл завершен. Тактов: {self.tick}. Полный 4D слепок зафиксирован в WAL.")

if __name__ == "__main__":
    EngineV7().run_ultimate_manifold([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3, 1, 2, 0, 3, 2])
