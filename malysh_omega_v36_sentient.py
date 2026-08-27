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

class SentientSuperorganismV36:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Эмоциональный настрой и мотивационные драйвы
        self.current_mood = "HOMEOSTASIS" # AFFECTIVE LAYER
        self.valence = 0.5               # Настроение от -1.0 до 1.0
        self.primary_drive = "EXPLORE"   # DRIVE SYSTEM: SEEK / AVOID / STABILIZE
        self.meta_optimization_rate = 1.0 # SELF-OPTIMIZATION LAYER
        self.prediction_error_history = deque(maxlen=20)
        
        self.initialize_sentient_matrix()

    def initialize_sentient_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "AFFECTIVE_LIMBIC"
                    elif z == 1:
                        domain = "MOTIVATIONAL_DRIVE"
                    else:
                        domain = "RECURSIVE_OPTIMIZER"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        goal_alignment=1.0,
                        plasticity=1.0
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

    def evaluate_affective_and_drives(self):
        # 1. Эмоциональный слой (Affective Layer)
        mean_energy = np.mean([d['energy'] for _, d in self.graph.nodes(data=True)])
        
        if mean_energy > 80.0:
            self.current_mood = "EUPHORIA"
            self.valence = 0.8
        elif mean_energy < 40.0:
            self.current_mood = "ANXIETY_STRESS"
            self.valence = -0.7
        else:
            self.current_mood = "CALM_FOCUS"
            self.valence = 0.2

        # 2. Мотивационные контуры (Drive System - Цели)
        if self.valence < 0.0:
            self.primary_drive = "SEEK_RECOVERY"  # Стремление к восстановлению
        elif mean_energy > 105.0:
            self.primary_drive = "AVOID_OVERLOAD" # Избежание перегрева
        else:
            self.primary_drive = "EXPLORE_GROWTH" # Цель: экспансия и обучение

    def run_recursive_self_optimization(self):
        # 3. Надсамомодельный слой (Self-Optimization)
        energies = [d['energy'] for _, d in self.graph.nodes(data=True)]
        target_energy = 90.0
        current_error = abs(np.mean(energies) - target_energy) / 100.0
        self.prediction_error_history.append(current_error)
        
        # Рекурсивная оптимизация структуры графа
        avg_error = np.mean(self.prediction_error_history)
        if avg_error > 0.3:
            self.meta_optimization_rate = 1.3 # Усиление адаптации при ошибках
            # Прунинг слабых связей для очистки структуры
            edges_to_remove = [(u, v) for u, v, d in self.graph.edges(data=True) if d['weight'] < 0.3]
            for u, v in edges_to_remove:
                if self.graph.has_edge(u, v):
                    self.graph.remove_edge(u, v)
        else:
            self.meta_optimization_rate = 0.9

    def process_cycle(self, token):
        self.tick += 1
        self.evaluate_affective_and_drives()
        self.run_recursive_self_optimization()

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            # Влияние мотивационных драйвов на вычисления
            drive_mod = 2 if self.primary_drive == "EXPLORE_GROWTH" else 1
            data['state'] = Base4Operator.apply(data['state'], token * drive_mod, valenc)
            
            # Динамика энергии под управлением эмоционального слоя
            if self.primary_drive == "SEEK_RECOVERY":
                data['energy'] = min(120.0, data['energy'] + 3.5) # Восстановление
            elif self.primary_drive == "AVOID_OVERLOAD":
                data['energy'] = max(10.0, data['energy'] - 2.5) # Сброс тепла
            else:
                data['energy'] = max(10.0, data['energy'] - 1.1)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        # Палитра зависит от эмоционального настроения (Mood)
        mood_palettes = {
            "EUPHORIA": 'plasma',
            "ANXIETY_STRESS": 'inferno',
            "CALM_FOCUS": 'viridis',
            "HOMEOSTASIS": 'coolwarm'
        }
        colormap = plt.get_cmap(mood_palettes.get(self.current_mood, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Sentient V36 [{self.current_mood}] Tick: {self.tick:02d}")
        
        fname = f"v36_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V36-SENTIENT] Рендер настроения [{self.current_mood} | Цель: {self.primary_drive}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v36_sentient.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V36-SENTIENT] Мастер-гифка чувствующего суперорганизма сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V36-SENTIENT] Эволюция завершена. Настроение: {self.current_mood}. Активных связей: {self.graph.number_of_edges()}")

if __name__ == "__main__":
    organism = SentientSuperorganismV36()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
