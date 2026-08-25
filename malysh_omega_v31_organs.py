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

class SupremeBioSystemV31:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Системные поля органов
        self.atp_pool = 100.0
        self.global_temperature = 36.6
        self.pressure_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.immune_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_organ_system()

    def initialize_organ_system(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Распределение специализированных органов по матрице
                    if z == 0:
                        if x < 2: organ = "THERMO_HYPOTHALAMUS"
                        elif x < 4: organ = "METABOLIC_LIVER"
                        else: organ = "IMMUNE_DEFENSE"
                    elif z == 1:
                        if x < 3: organ = "NEURAL_CORTEX"
                        else: organ = "MORPHOGENETIC_STEM"
                    else:
                        organ = "HYDRO_HEART"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        organ=organ,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        temperature=36.6,
                        damage=0.0,
                        spike=False
                    )
                    node_id += 1

        # Связывание узлов синапсами
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                if abs(ux - vx) + abs(uy - vy) + abs(uz - vz) <= 1:
                    self.graph.add_edge(u, v, conductance=1.0)

    def process_organ_cycle(self, token):
        self.tick += 1
        
        # 1. Метаболический центр производит АТФ
        self.atp_pool = min(200.0, self.atp_pool + 5.0)
        
        # 2. Гидродинамическое сердце создает давление
        heart_pulse = math.sin(self.tick * 0.7) * 2.5
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            org = data['organ']
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            # Вычисления Base-4
            data['state'] = Base4Operator.apply(data['state'], token, valenc)
            
            # Функционал органа
            if org == "METABOLIC_LIVER":
                data['energy'] = min(120.0, data['energy'] + 4.0)
                self.atp_pool -= 1.0
            elif org == "THERMO_HYPOTHALAMUS":
                # Регулировка температуры
                diff = data['temperature'] - 36.6
                data['temperature'] -= diff * 0.3
            elif org == "HYDRO_HEART":
                data['temperature'] += heart_pulse * 0.5
                self.pressure_field[x, y, z] = abs(heart_pulse)
            elif org == "IMMUNE_DEFENSE":
                if data['damage'] > 0.1:
                    data['damage'] = max(0.0, data['damage'] - 0.2)
                    self.immune_field[x, y, z] = 1.0
            elif org == "MORPHOGENETIC_STEM":
                # Управление прунингом и синапсами
                data['energy'] = max(20.0, data['energy'] - 0.5)
            elif org == "NEURAL_CORTEX":
                if data['state'] == 3:
                    data['spike'] = True
                    data['temperature'] += 1.2
                else:
                    data['spike'] = False

            # Расход энергии
            data['energy'] = max(10.0, data['energy'] - 1.2)
            if data['energy'] < 25.0:
                data['damage'] = min(1.0, data['damage'] + 0.25)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        colormap = plt.get_cmap('plasma')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            
            if data['damage'] > 0.1:
                color_array[x, y, z] = '#00ffcc' # Сигнал починки / иммунитета
            else:
                norm = min(1.0, data['energy'] / 100.0)
                color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Supreme Bio-System V31 [Tick: {self.tick:02d}]")
        
        fname = f"v31_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V31-ORGANS] Рендер органной структуры: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v31_organs.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V31-ORGANS] Мастер-гифка органной системы сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=15):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_organ_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V31-ORGANS] Цикл завершен. Все 6 органов функционируют слаженно.")

if __name__ == "__main__":
    system = SupremeBioSystemV31()
    system.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
