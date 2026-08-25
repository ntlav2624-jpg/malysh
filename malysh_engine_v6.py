import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV6:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = [x, y, z, t]
        self.state = 0
        self.energy = 100.0
        self.temperature = 20.0
        self.neighbors = {} # target_id -> weight

    def thermodynamic_step(self, val):
        # Термодинамика и 4D волновой сдвиг
        if self.energy > 12.0 and self.temperature < 85.0:
            self.energy -= 3.0
            self.temperature += 1.5
            valenc = (self.xyzt[2] + self.xyzt[3]) % 4
            self.state = Base4Operator.apply(self.state, val, valenc)
        else:
            # Охлаждение и регенерация
            self.energy = min(100.0, self.energy + 25.0)
            self.temperature = max(20.0, self.temperature - 5.0)
        return self.state

class EngineV6:
    def __init__(self, size=1000, wal="malysh_v6_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        
        # Инициализация полного пространства XYZT
        for i in range(size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = (i // 1000) % 10
            self.nodes[i] = NodeV6(i, x, y, z, t)
            
        # Построение адаптивных весовых связей графа
        for i in range(size):
            for off in [1, 10, 100]:
                nb = (i + off) % size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.2)
                self.nodes[i].neighbors[nb] = weight

    def route_and_process(self, nid, val):
        node = self.nodes[nid]
        res = node.thermodynamic_step(val)
        
        # Интеллектуальная маршрутизация пакетов по графу
        routed = []
        for nb, weight in node.neighbors.items():
            target = self.nodes[nb]
            if weight > 1.25 and target.energy > 15.0 and target.temperature < 80.0:
                routed.append(nb)
                # Динамическая коррекция весов (обучение связей)
                node.neighbors[nb] = min(3.0, weight + 0.04)
                target.energy = max(0.0, target.energy - 1.0)
        return nid, res, routed

    def render_orbital_3d(self, ax, ay, az, cam_angle):
        print(f"\n[ENGINE V6 | Tick: {self.tick} | True Log-Spiral Focus -> X:{ax} Y:{ay} Z:{az} | CamAngle: {cam_angle:.2f}]")
        
        cos_a = math.cos(cam_angle)
        sin_a = math.sin(cam_angle)

        for z_slice in range(3):
            print(f"=== Z-Layer {z_slice} [Orbital Camera Matrix] ===")
            grid = [["." for _ in range(10)] for _ in range(10)]
            
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    # Орбитальное вращение проекции камеры
                    rx = int(round(gx * cos_a - gy * sin_a)) % 10
                    ry = int(round(gx * sin_a + gy * cos_a)) % 10
                    
                    if gx == ax and gy == ay:
                        grid[ry][rx] = "O" # Фокус экспоненциальной спирали
                    elif n.temperature > 60.0:
                        grid[ry][rx] = "!" # Зона перегрева
                    elif n.energy > 65.0:
                        grid[ry][rx] = "#"  # Высокий потенциал
                    elif n.energy > 25.0:
                        grid[ry][rx] = "x"  # Активный узел
            for row in grid:
                print(" ".join(row))

    def run_hyper_monolith(self, stream):
        for val in stream:
            self.tick += 1
            
            # 1. Истинная экспоненциально-логарифмическая спираль
            angle = self.tick * 0.3
            radius = 0.6 * math.exp(0.09 * angle)
            ax = int(abs(radius * math.cos(angle)) * 5) % 10
            ay = int(abs(radius * math.sin(angle)) * 5) % 10
            az = self.tick % 3
            
            # 2. Эволюция 4D координаты времени T в пространстве
            for n in self.nodes.values():
                n.xyzt[3] = (n.xyzt[3] + 1) % 10

            # 3. Выборка активных узлов фокуса спирали
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:24]
            if not active:
                active = list(self.nodes.keys())[:16]

            # 4. Многопоточный конвейер термодинамики и маршрутизации
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.route_and_process, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # 5. Визуализация с динамической орбитальной камерой каждые 2 такта
            if self.tick % 2 == 0:
                orbital_angle = self.tick * 0.25
                self.render_orbital_3d(ax, ay, az, orbital_angle)

        # 6. Фиксация абсолютного гипер-слепка в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy, "temp": n.temperature, "xyzt": n.xyzt} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V6] Гипер-монолитный цикл завершен. Тактов: {self.tick}. Полный 4D-слепок зафиксирован в WAL.")

if __name__ == "__main__":
    EngineV6().run_hyper_monolith([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3, 1, 2, 0])
