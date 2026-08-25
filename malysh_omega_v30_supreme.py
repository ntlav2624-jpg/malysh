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

class SupremeBioMatrixV30:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v30_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Интегрированные многомерные поля организма
        self.hormone_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.immune_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.repair_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_supreme_continuum()

    def initialize_supreme_continuum(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Анатомическая специализация по слоям
                    if z == 0:
                        organ = "IMMUNE_GLAND"     # Нижний слой: иммунитет и метаболизм
                    elif z == 1:
                        organ = "NEURAL_CORTEX"    # Средний слой: память, STDP и вычисления
                    else:
                        organ = "MYOCARDIUM_HEART" # Верхний слой: ритмический пульс и сосуды

                    dna_memory = [np.random.randint(0, 4) for _ in range(4)]

                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        organ_type=organ,
                        dna=dna_memory,
                        state=0,
                        energy=90.0,
                        temperature=25.0,
                        potential=-70.0,
                        damage=0.0,
                        antibody_level=0.0,
                        spike=False
                    )
                    node_id += 1

        # Построение синаптической и сосудистой сетки
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                if abs(ux - vx) + abs(uy - vy) + abs(uz - vz) <= 1:
                    self.graph.add_edge(u, v, weight=1.0, plasticity=1.0)

    def process_supreme_cycle(self, data_stream):
        self.tick += 1
        
        # 1. Диффузия полей (гормоны, иммунитет, регенерация)
        for field in [self.hormone_field, self.immune_field, self.repair_field]:
            lap = np.zeros_like(field)
            for x in range(self.x_size):
                for y in range(self.y_size):
                    for z in range(self.z_layers):
                        s, count = 0.0, 0
                        for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                            nx, ny, nz = x+dx, y+dy, z+dz
                            if 0 <= nx < self.x_size and 0 <= ny < self.y_size and 0 <= nz < self.z_layers:
                                s += field[nx, ny, nz]
                                count += 1
                        if count > 0:
                            lap[x, y, z] = (s / count) - field[x, y, z]
            field += 0.2 * lap

        self.hormone_field = np.clip(self.hormone_field, 0.0, 1.0)
        self.immune_field = np.clip(self.immune_field, 0.0, 1.0)
        self.repair_field = np.clip(self.repair_field, 0.0, 1.0)

        # 2. Ритмы и физиология органоидов
        heart_rhythm = math.sin(self.tick * 0.8)
        token = data_stream[self.tick % len(data_stream)]

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            # Base-4 вычисления + Нейро-геномная память
            data['state'] = Base4Operator.apply(data['state'], token, valenc)
            
            # Моделирование повреждений / стресса (Иммунитет и заживление)
            if data['energy'] < 20.0 or data['temperature'] > 45.0:
                data['damage'] = min(1.0, data['damage'] + 0.3)
            
            if data['damage'] > 0.2:
                # Включается самовосстановление и иммунный ответ
                self.repair_field[x, y, z] = min(1.0, self.repair_field[x, y, z] + 0.4)
                data['damage'] = max(0.0, data['damage'] - 0.15)
            
            # Специализация органов
            if data['organ_type'] == "MYOCARDIUM_HEART":
                pump = (heart_rhythm + 1.0) * 0.6
                data['temperature'] += pump * 2.5
                data['energy'] = max(10.0, data['energy'] - 1.0)
            elif data['organ_type'] == "NEURAL_CORTEX":
                data['potential'] += (data['state'] * 3.0) + (self.hormone_field[x, y, z] * 5.0) - 2.0
                if data['potential'] > -25.0:
                    data['spike'] = True
                    data['potential'] = -80.0
                    self.hormone_field[x, y, z] = min(1.0, self.hormone_field[x, y, z] + 0.3)
                else:
                    data['spike'] = False
                    data['potential'] = max(-90.0, data['potential'] - 1.5)
            elif data['organ_type'] == "IMMUNE_GLAND":
                self.immune_field[x, y, z] = min(1.0, self.immune_field[x, y, z] + 0.2)
                data['energy'] = min(110.0, data['energy'] + 1.5)

            data['temperature'] = max(20.0, data['temperature'] - 1.8)

        # 3. Синаптическая пластичность (Hebbian / STDP)
        for u, v, edata in self.graph.edges(data=True):
            if u in self.graph and v in self.graph:
                if self.graph.nodes[u]['spike'] and self.graph.nodes[v]['spike']:
                    edata['plasticity'] = min(4.0, edata['plasticity'] + 0.25)
                else:
                    edata['plasticity'] = max(0.1, edata['plasticity'] - 0.02)

    def render_supreme_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        colormap = plt.get_cmap('magma')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            
            # Цвет отражает здоровье, иммунитет и активность ткани
            if data['damage'] > 0.1:
                color_array[x, y, z] = '#00ffff' # Неоново-голубой сигнал тревоги/исцеления
            else:
                norm_val = min(1.0, (data['energy'] / 100.0) * 0.7 + self.hormone_field[x, y, z] * 0.3)
                color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm_val)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 25)
        ax.set_title(f"Supreme Omega V30 [Tick: {self.tick:02d}]")
        
        filename = f"v30_frame_{self.tick:02d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[SUPREME-V30] Рендер высшего кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_omega.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[SUPREME-V30] Мастер-анимация Омега сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=15):
        for _ in range(cycles):
            self.process_supreme_cycle(stream)
            self.render_supreme_frame()
        self.compile_animation()
        print(f"\n[SUPREME-V30] Синтез завершен. Тактов: {self.tick}. Все подсистемы функционируют гармонично.")

if __name__ == "__main__":
    engine = SupremeBioMatrixV30()
    engine.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
