import time, json
class EcoNode:
    def __init__(self, n, x, y, z, t):
        self.id = n
        self.xyzt = (x, y, z, t)
        self.state = 0
    def transform(self, b):
        self.state = (b + self.xyzt[0] + self.xyzt[2]) % 4
        return self.state
class EcoSphere:
    def __init__(self):
        self.nodes = {i: EcoNode(i, i%10, (i//10)%10, (i//100)%10, i%10) for i in range(1000)}
    def run(self, stream):
        log = []
        for s, val in enumerate(stream):
            g = s % 10
            active = [n for n in self.nodes.values() if n.xyzt[0] == g][:5]
            res = [(n.id, n.transform(val)) for n in active]
            log.append({"step": s, "glyph": g, "res": res})
        with open("malysh_wal.log", "a") as f:
            f.write(json.dumps({"time": time.time(), "data": log}) + "\n")
        print("[CORE] Спираль замкнута. WAL-лог записан.")
if __name__ == "__main__":
    EcoSphere().run([0, 3, 2, 1, 3, 0, 2, 1, 3, 3])
