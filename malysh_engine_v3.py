import json, os, math, time, concurrent.futures

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class NodeV3:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = (x, y, z, t)
        self.state = 0
        self.energy = 100.0
        self.neighbors = {}
    def transform(self, val):
        if self.energy > 5.0:
            self.energy -= 1.5
            self.state = Base4Operator.apply(self.state, val, self.xyzt[2])
        else:
            self.energy = min(100.0, self.energy + 10.0)
        return self.state

class EngineV3:
    def __init__(self, size=1000, wal="malysh_v3_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {i: NodeV3(i, i%10, (i//10)%10, (i//100)%10, i%10) for i in range(size)}
        self.tick = 0
        for i in range(size):
            for off in [1, 10, 100]:
                nb = (i + off) % size
                self.nodes[i].neighbors[nb] = 1.0 + (self.nodes[i].xyzt[1] * 0.1)

    def process_node(self, nid, val):
        node = self.nodes[nid]
        res = node.transform(val)
        routed = []
        for nb, weight in node.neighbors.items():
            if weight > 1.2 and self.nodes[nb].energy > 10:
                routed.append(nb)
        return nid, res, routed

    def render_ascii(self, active_glyph):
        grid = [["." for _ in range(10)] for _ in range(10)]
        for nid, n in self.nodes.items():
            gx, gy = n.xyzt[0], n.xyzt[1]
            if gx == active_glyph:
                grid[gy][gx] = "#" if n.energy > 50 else "x"
        print(f"\n[VISUALIZATION - Tick {self.tick} | Spiral Attractor Glyph: {active_glyph}]")
        for row in grid:
            print(" ".join(row))

    def run_cycle(self, stream):
        for val in stream:
            self.tick += 1
            angle = self.tick * 0.3
            radius = 0.5 * math.exp(0.1 * angle)
            attr = int(abs(radius * math.cos(angle)) * 3) % 10
            
            active = [nid for nid, n in self.nodes.items() if n.xyzt[0] == attr][:15]
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self.process_node, nid, val) for nid in active]
                for f in concurrent.futures.as_completed(futures):
                    nid, res, routed = f.result()
            
            if self.tick % 2 == 0:
                self.render_ascii(attr)

        states = {str(n.id): {"state": n.state, "energy": n.energy} for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V3] Цикл завершен. Тактов: {self.tick}. Состояние записано в WAL.")

if __name__ == "__main__":
    EngineV3().run_cycle([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1])
