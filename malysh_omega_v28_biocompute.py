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

class MalyshBioComputeV28:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v28_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Информационные и биологические поля
        self.compute_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.hormone_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_biocompute_matrix()

    def initialize_biocompute_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        tissue, organ = "LOGIC_EPITHELIUM", "ALU_CORE"
                    elif z == 1:
                        tissue, organ = "NEURAL_PARENCHYMA", "SYNAPSE_NODE"
                    else:
                        tissue, organ = "VASCULAR_CORE", "PULSE_HEART"

                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        tissue_layer=tissue,
                        organ_type=organ,
                        state=0,
                        energy=90.0,
                        temperature=25.0,
                        entropy=0.0,
                        spike=False
                    )
                    node_id += 1

        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                if abs(ux - vx) + abs(uy - vy) + abs(uz - vz) <= 1:
                    self.graph.add_edge(u, v, weight=1.0, data_flux=0.0)

    def process_biocompute_cycle(self, val):
        self.tick += 1
        
        # 1. Расчет вычислительного поля и Base-4 состояний
        states = []
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + self.tick) % 4
            data['state'] = Base4Operator.apply(data['state'], val, valenc)
            states.append(data['state'])

        # Расчет локальной энтропии матрицы
        unique, counts = np.unique(states, return_counts=True)
        probs = counts / len(states)
        global_entropy = -np.sum(probs * np.log2(probs + 1e-9))

        # 2. Интеграция вычислений в биологию тканей
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            # Вычислительная нагрузка нагревает узел и генерирует энтропию
            data['entropy'] = global_entropy
            data['temperature'] += (data['state'] * 0.8) + (global_entropy * 0.5)
            data['energy'] = max(10.0, data['energy'] - 1.0)
            
            if data['organ_type'] == "ALU_CORE":
                data['energy'] = min(120.0, data['energy'] + 2.0)
            elif data['organ_type'] == "SYNAPSE_NODE":
                if data['state'] == 3:
                    data['spike'] = True
                    data['temperature'] += 4.0
                else:
                    data['spike'] = False
            
            data['temperature'] = max(20.0, data['temperature'] - 1.5)

    def render_biocompute_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        colormap = plt.get_cmap('coolwarm')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm_val = min(1.0, data['temperature'] / 50.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm_val)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 25)
        ax.set_title(f"Bio-Compute V28 [Tick: {self.tick:02d}]")
        
        filename = f"v28_frame_{self.tick:02d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[BIO-COMPUTE] Рендер тактового кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_biocompute_matrix.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=350, loop=0)
        print(f"[BIO-COMPUTE] Мастер-анимация сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream):
        for val in stream:
            self.process_biocompute_cycle(val)
            self.render_biocompute_frame()
        self.compile_animation()
        print(f"\n[BIO-COMPUTE] Вычислительный цикл завершен. Тактов: {self.tick}. Узлов: {self.graph.number_of_nodes()}")

if __name__ == "__main__":
    engine = MalyshBioComputeV28()
    engine.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2])
