import time, json, os, math
class Base4Operator:
    TRANSITION_MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.TRANSITION_MATRIX[cur%4][val%4] + valenc) % 4
class EcoNodeV2:
    def __init__(self, nid, x, y, z, t):
        self.id = nid
        self.xyzt = (x, y, z, t)
        self.state = 0
        self.neighbors = []
    def add_link(self, n_id):
        if n_id not in self.neighbors: self.neighbors.append(n_id)
    def transform(self, val):
        self.state = Base4Operator.apply(self.state, val, self.xyzt[2])
        return self.state
class EcoSphereEngine:
    def __init__(self, size=1000, wal="malysh_v2_wal.log"):
        self.size = size
        self.wal_file = wal
        self.nodes = {}
        self.tick = 0
        if not self._recover():
            for i in range(self.size):
                self.nodes[i] = EcoNodeV2(i, i%10, (i//10)%10, (i//100)%10, i%10)
            for i in range(self.size):
                for off in [1, 10, 100]: self.nodes[i].add_link((i+off)%self.size)
    def _recover(self):
        if not os.path.exists(self.wal_file): return False
        last = None
        with open(self.wal_file) as f:
            for line in f:
                if line.strip():
                    try: last = json.loads(line.strip())
                    except: pass
        if not last or "node_states" not in last: return False
        self.tick = last.get("tick", 0)
        for i in range(self.size):
            self.nodes[i] = EcoNodeV2(i, i%10, (i//10)%10, (i//100)%10, i%10)
            for off in [1, 10, 100]: self.nodes[i].add_link((i+off)%self.size)
        for k, v in last["node_states"].items():
            if int(k) in self.nodes: self.nodes[int(k)].state = v
        return True
    def run(self, stream):
        for val in stream:
            self.tick += 1
            attr = int(abs(math.sin(self.tick * 0.5) * 9))
            active = [n for n in self.nodes.values() if n.xyzt[0] == attr][:6]
            for n in active:
                res = n.transform(val)
                for nb in n.neighbors[:2]:
                    if nb in self.nodes: self.nodes[nb].transform(res)
        states = {str(n.id): n.state for n in self.nodes.values()}
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "node_states": states}) + "\n")
        print(f"[ENGINE] Тактов: {self.tick}. Состояние записано в WAL с воссозданием графа.")
if __name__ == "__main__":
    EcoSphereEngine().run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2])
