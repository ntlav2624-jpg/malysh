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

class MetaCognitiveSuperorganismV34:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Поведенческая система, память состояний и надкогнитивный слой
        self.current_mode = "EXPLORE"
        self.state_memory = deque(maxlen=25)
        self.digital_habits = {}
        
        # Надкогнитивные метрики
        self.meta_efficiency = 1.0
        self.structural_plasticity = 1.0
        self.self_reflection_score = 0.5
        
        self.initialize_metacognitive_matrix()

    def initialize_metacognitive_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        layer_role = "SENSORY_BUFFER"
                    elif z == 1:
                        layer_role = "NEURAL_EXECUTION"
                    else:
                        layer_role = "META_COGNITIVE_CORE" # Верхний слой самоанализа

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        role=layer_role,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        efficiency_index=1.0,
                        active_meta=False
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

    def run_meta_cognition_layer(self):
        # Надкогнитивный слой анализирует состояние графа и оптимизирует структуру
        energies = [d['energy'] for _, d in self.graph.nodes(data=True)]
        mean_energy = np.mean(energies)
        
        # Самоанализ и регулировка обучения
        if mean_energy < 50.0:
            self.current_mode = "REST_OPTIMIZATION"
            self.structural_plasticity = 0.5
        elif self.self_reflection_score > 0.8:
            self.current_mode = "DEEP_LEARNING"
            self.structural_plasticity = 1.5
        else:
            self.current_mode = "ACTIVE_ANALYTICS"
            self.structural_plasticity = 1.0

        # Надкогнитивная оптимизация графа (прунинг слабых связей / усиление ключевых)
        edges_to_prune = []
        for u, v, edata in self.graph.edges(data=True):
            edata['weight'] *= self.structural_plasticity
            if edata['weight'] < 0.2:
                edges_to_prune.append((u, v))
        
        for u, v in edges_to_prune:
            if self.graph.has_edge(u, v):
                self.graph.remove_edge(u, v) # Удаление неэффективных синапсов

        self.self_reflection_score = min(1.0, max(0.1, mean_energy / 100.0))

    def process_cycle(self, token):
        self.tick += 1
        self.run_meta_cognition_layer()
        
        # Память состояний (State Memory)
        snapshot = {
            "tick": self.tick,
            "mode": self.current_mode,
            "reflection": float(self.self_reflection_score),
            "plasticity": float(self.structural_plasticity)
        }
        self.state_memory.append(snapshot)

        # Формирование цифровых привычек
        habit_key = f"{self.current_mode}_{token}"
        self.digital_habits[habit_key] = self.digital_habits.get(habit_key, 1.0) + 0.3

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            data['state'] = Base4Operator.apply(data['state'], token, valenc)
            
            # Надкогнитивная регуляция узлов
            if data['role'] == "META_COGNITIVE_CORE":
                data['efficiency_index'] = self.self_reflection_score * 1.2
                data['energy'] = min(120.0, data['energy'] + 2.5)
                data['active_meta'] = True
            else:
                data['energy'] = max(10.0, data['energy'] - 1.2)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('plasma' if self.current_mode == "DEEP_LEARNING" else 'viridis')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Meta-Cognition V34 [{self.current_mode}] Tick: {self.tick:02d}")
        
        fname = f"v34_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V34-META] Рендер надкогнитивного кадра [{self.current_mode}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v34_metacognition.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V34-META] Мастер-гифка надкогнитивной системы сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V34-META] Синтез завершен. Самоанализ стабилен. Активных синапсов: {self.graph.number_of_edges()}")

if __name__ == "__main__":
    organism = MetaCognitiveSuperorganismV34()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
