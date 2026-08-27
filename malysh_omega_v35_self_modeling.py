import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, math
from collections import deque
from PIL import Image

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class SelfModelingSuperorganismV35:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Модель самого себя и прогнозирование
        self.state_history = deque(maxlen=30)
        self.internal_ego_model = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.prediction_error = 0.0
        self.evolutionary_drive = 1.0
        
        self.initialize_self_modeling_matrix()

    def initialize_self_modeling_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        subsystem = "SENSOR_SURFACE"
                    elif z == 1:
                        subsystem = "NEURAL_CORE"
                    else:
                        subsystem = "EGO_SELF_MODEL" # Орган самомоделирования

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        subsystem=subsystem,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        predicted_energy=95.0,
                        model_divergence=0.0
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
                    self.graph.add_edge(u, v, weight=1.0)

    def run_self_modeling_and_prediction(self, token):
        # 1. Прогнозирование собственных состояний (Self-Prediction)
        actual_energy_sum = sum(d['energy'] for _, d in self.graph.nodes(data=True))
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            # Эго-модель предсказывает поведение узла на следующем шаге
            expected_energy = data['energy'] - 1.2 + (0.5 * token)
            data['predicted_energy'] = max(10.0, min(120.0, expected_energy))
            self.internal_ego_model[x, y, z] = data['predicted_energy']

        # 2. Симуляция шага организма
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            data['state'] = Base4Operator.apply(data['state'], token, valenc)
            
            if data['subsystem'] == "EGO_SELF_MODEL":
                data['energy'] = min(120.0, data['energy'] + 2.0)
            else:
                data['energy'] = max(10.0, data['energy'] - 1.2)

        # 3. Вычисление ошибки прогноза (Prediction Error) и оптимизация развития
        new_energy_sum = sum(d['energy'] for _, d in self.graph.nodes(data=True))
        self.prediction_error = abs(actual_energy_sum - new_energy_sum) / 75.0
        
        # Организм оптимизирует свое развитие на основе ошибки
        if self.prediction_error > 2.0:
            self.evolutionary_drive *= 1.15  # Ускоряем адаптацию при расхождении модели с реальностью
        else:
            self.evolutionary_drive = max(0.8, self.evolutionary_drive * 0.95)

    def process_cycle(self, token):
        self.tick += 1
        self.run_self_modeling_and_prediction(token)
        
        # Сохранение слепка в историю состояний
        self.state_history.append({
            "tick": self.tick,
            "error": float(self.prediction_error),
            "drive": float(self.evolutionary_drive)
        })

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        # Палитра отражает точность модели себя (ошибку предсказания)
        colormap = plt.get_cmap('coolwarm' if self.prediction_error < 1.5 else 'inferno')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Self-Modeling V35 [Err: {self.prediction_error:.2f}] Tick: {self.tick:02d}")
        
        fname = f"v35_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V35-SELF] Рендер самомоделирования (ошибка: {self.prediction_error:.2f}): {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v35_self_modeling.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V35-SELF] Мастер-гифка самомоделирования сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V35-SELF] Эволюция самомоделирования завершена. История состояний: {len(self.state_history)} записей.")

if __name__ == "__main__":
    organism = SelfModelingSuperorganismV35()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
