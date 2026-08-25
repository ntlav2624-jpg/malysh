import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV4:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = (x, y, z, t)
        self.state = 0
        self.energy = 100.0
        self.neighbors = {} # id -> weight

    def transform(self, val):
        if self.energy > 10.0:
            self.energy -= 2.0
            self.state = Base4Operator.apply(self.state, val, self.xyzt[2])
        else:
            self.energy = min(100.0, self.energy + 15.0) # регенерация
        return self.state

class EngineV4:
    def __init__(self, size=1000, wal="malysh_v4_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        
        # Инициализация графа с 3D-координатами (X, Y, Z в пределах 0-9)
        for i in range(size):
            x = i % 10
            y = (i // 10) % 10
            z = (i // 100) % 10
            t = i % 4
            self.nodes[i] = NodeV4(i, x, y, z, t)
            
        # Создание взвешенных связей для маршрутизации
        for i in range(size):
            for off in [1, 10, 100]:
                nb = (i + off) % size
                weight = 1.0 + (self.nodes[i].xyzt[2] * 0.2)
                self.nodes[i].neighbors[nb] = weight

    def process_packet(self, nid, val):
        node = self.nodes[nid]
        res = node.transform(val)
        
        # Маршрутизация по весам графа
        routed_targets = []
        for nb, weight in node.neighbors.items():
            if weight > 1.3 and self.nodes[nb].energy > 20:
                routed_targets.append(nb)
                # Динамическая коррекция весов (обучение/диффузия)
                node.neighbors[nb] = min(2.0, weight + 0.05)
        return nid, res, routed_targets

    def render_volumetric_ascii(self, ax, ay, az):
        print(f"\n[ENGINE V4 | Tick: {self.tick} | 3D Attractor Target -> X:{ax} Y:{ay} Z:{az}]")
        # Рендерим срезы по Z для создания 3D-ощущения
        for z_slice in range(3):
            print(f"--- Z-Layer {z_slice} ---")
            grid = [["." for _ in range(10)] for _ in range(10)]
            for nid, n in self.nodes.items():
                gx, gy, gz = n.xyzt[0], n.xyzt[1], n.xyzt[2]
                if gz == z_slice:
                    if gx == ax and gy == ay:
                        grid[gy][gx] = "O" # Фокус аттрактора
                    elif n.energy > 60:
                        grid[gy][gx] = "#"
                    elif n.energy > 20:
                        grid[gy][gx] = "x"
            for row in grid:
                print(" ".join(row))

    def run_simulation(self, stream):
        for val in stream:
            self.tick += 1
            
            # Истинная логарифмическая спираль в 3D пространстве
            angle = self.tick * 0.4
            radius = 0.8 * math.exp(0.08 * angle)
            ax = int(abs(radius * math.cos(angle)) * 5) % 10
            ay = int(abs(radius * math.sin(angle)) * 5) % 10
            az = self.tick % 3 # Сканирование по Z-слоям
            
            # Выборка активных узлов вблизи спирального фокуса
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == ax and n.xyzt[2] == az][:20]
            if not active:
                active = list(self.nodes.keys())[:15]

            # Многопоточная обработка пулом
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.process_packet, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    _, _, _ = f.result()

            # Визуализация каждые 2 такта
            if self.tick % 2 == 0:
                self.render_volumetric_ascii(ax, ay, az)

        # Сохранение полного состояния в WAL
        states = {str(n.id): {"state": n.state, "energy": n.energy} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V4] Цикл завершен. Тактов: {self.tick}. Объемный слепок записан в WAL.")

if __name__ == "__main__":
    EngineV4().run_simulation([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0])
