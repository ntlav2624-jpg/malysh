import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, math
from PIL import Image

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class MetaSystemicSuperorganismV32:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Надсистемные глобальные пулы
        self.hormone_level = 0.5
        self.breath_phase = 0.0
        self.toxin_load = 0.1
        self.global_awareness = 0.0
        
        self.initialize_metasystem()

    def initialize_metasystem(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Распределение надорганных систем по матрице
                    if z == 0:
                        if x < 2: metasystem = "ENDOCRINE_REGULATOR"
                        else: metasystem = "EXCRETORY_DETOX"
                    elif z == 1:
                        if x < 2: metasystem = "SENSORY_INPUT"
                        elif x < 4: metasystem = "RESPIRATORY_PULSE"
                        else: metasystem = "REGENERATION_AXOLOTL"
                    else:
                        metasystem = "COGNITIVE_INTEGRATOR"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        system=metasystem,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        vitality=100.0,
                        plasticity=1.0,
                        active_signal=False
                    )
                    node_id += 1

        # Построение связей между узлами
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                if abs(ux - vx) + abs(uy - vy) + abs(uz - vz) <= 1:
                    self.graph.add_edge(u, v, weight=1.0)

    def process_metasystem_cycle(self, token):
        self.tick += 1
        
        # Дыхательный цикл и эндокринный фон
        self.breath_phase = math.sin(self.tick * 0.5)
        self.hormone_level = 0.5 + 0.3 * math.cos(self.tick * 0.3)
        self.toxin_load = max(0.05, self.toxin_load - 0.02 + 0.03 * random_spike_gen(self.tick))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            sys_type = data['system']
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            # Базовые Base-4 вычисления с учетом эндокринного влияния
            data['state'] = Base4Operator.apply(data['state'], token, valenc)
            
            # Работа надорганных систем
            if sys_type == "ENDOCRINE_REGULATOR":
                data['vitality'] = min(120.0, data['vitality'] + self.hormone_level)
            elif sys_type == "RESPIRATORY_PULSE":
                data['vitality'] += self.breath_phase * 2.0
            elif sys_type == "EXCRETORY_DETOX":
                self.toxin_load = max(0.0, self.toxin_load - 0.05)
            elif sys_type == "REGENERATION_AXOLOTL":
                if data['vitality'] < 50.0:
                    data['vitality'] += 15.0 # Автоматическое залечивание тканей
            elif sys_type == "COGNITIVE_INTEGRATOR":
                self.global_awareness = (self.global_awareness * 0.8) + (data['state'] * 0.2)
                data['active_signal'] = True
            
            data['vitality'] = max(10.0, data['vitality'] - 1.0)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        colormap = plt.get_cmap('coolwarm')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['vitality'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Meta-Superorganism V32 [Tick: {self.tick:02d}]")
        
        fname = f"v32_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V32-METASYSTEM] Рендер кадра надсистемы: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v32_metasystem.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V32-METASYSTEM] Мастер-гифка суперорганизма сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=15):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_metasystem_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V32-METASYSTEM] Цикл завершен. Все 6 надорганных систем интегрированы.")

def random_spike_gen(t):
    return 1.0 if t % 4 == 0 else 0.0

if __name__ == "__main__":
    organism = MetaSystemicSuperorganismV32()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
