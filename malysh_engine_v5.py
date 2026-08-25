import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV5:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = [x, y, z, t]
        self.state = 0
        self.energy = 100.0
        self.neighbors = {} # target_id -> weight

    def step_physics(self, val):
        # Физика энергетики и T-слоя
        if self.energy > 15.0:
            self.energy -= 2.5
            # T-модификатор влияет на валентность
            valenc = (self.xyzt[2] + self.xyzt[3]) % 4
            self.state = Base4Operator.apply(self.state, val, valenc)
        else:
            self.energy = min(100.0, self.energy + 20.0) # регенерация
        return self.state

class EngineV5:
    def __init__(self, size=1000, wal="malysh_v5_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        
        # Инициализация 4D узлов (XYZT)
        for i in range(size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = (i // 1000) % 4
            self.nodes[i] = NodeV5(i, x, y, z, t)
            
        # Построение взвешенных связей для маршрутизации
        for i in range(size):
            for off in [1, 10, 100]:
                nb = (i + off) % size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.15)
                self.nodes[i].neighbors[nb] = weight

    def process_routing_packet(self, nid, val):
        node = self.nodes[nid]
        res = node.step_physics(val)
        
        # Маршрутизация: передача энергии и весов активным соседям
        routed = []
        for nb, weight in node.neighbors.items():
            if weight > 1.2 and self.nodes[nb].energy > 15:
                routed.append(nb)
                # Коррекция веса канала (обучение графа)
                node.neighbors[nb] = min(2.5, weight + 0.03)
                self.nodes[nb].energy = max(0.0, self.nodes[nb].energy - 0.5)
        return nid, res, routed

    def render_rotated_3d(self, ax, ay, az, angle_rot):
        print(f"\n[ENGINE V5 | Tick: {self.tick} | 4D Space-Time Focus -> X:{ax} Y:{ay} Z:{az} T_rot:{angle_rot:.2f}]")
        
        # Матрица вращения камеры для ASCII проекции
        cos_a = math.cos(angle_rot)
        sin_a = math.sin(angle_rot)

        for z_slice in range(3):
            print(f"=== Z-Layer {z_slice} [Rotated Projection] ===")
            grid = [["." for _ in range(10)] for _ in range(10)]
            
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    # Применение поворота камеры к координатам отображения
                    rx = int(round(gx * cos_a - gy * sin_a)) % 10
                    ry = int(round(gx * sin_a + gy * cos_a)) % 10
                    
                    if gx == ax and gy == ay:
                        grid[ry][rx] = "O" # Фокус истинной логарифмической спирали
                    elif n.energy > 70:
                        grid[ry][rx] = "#"  # Высокая энергия
                    elif n.energy > 30:
                        grid[ry][rx] = "x"  # Средняя активность
            for row in grid:
                print(" ".join(row))

    def run_monolith(self, stream):
        for val in stream:
            self.tick += 1
            
            # 1. Истинная логарифмическая спираль в пространстве
            angle = self.tick * 0.35
            radius = 0.7 * math.exp(0.07 * angle)
            ax = int(abs(radius * math.cos(angle)) * 4) % 10
            ay = int(abs(radius * math.sin(angle)) * 4) % 10
            az = self.tick % 3
            
            # Эволюция T-времени движка
            for n in self.nodes.values():
                n.xyzt[3] = (n.xyzt[3] + 1) % 4

            # Выборка активных узлов фокуса
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:22]
            if not active:
                active = list(self.nodes.keys())[:15]

            # Многопоточный конвейер маршрутизации и физики
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.process_routing_packet, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # Визуализация с вращением камеры каждые 2 такта
            if self.tick % 2 == 0:
                cam_angle = self.tick * 0.2
                self.render_rotated_3d(ax, ay, az, cam_angle)

        # Полный слепок 4D состояния в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy, "xyzt": n.xyzt} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V5] Монолитный цикл завершен. Тактов: {self.tick}. 4D слепок зафиксирован в WAL.")

if __name__ == "__main__":
    EngineV5().run_monolith([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3, 1])
