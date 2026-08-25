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

class BehavioralSuperorganismV33:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Поведенческий движок и память состояний
        self.current_mode = "EXPLORE"  # Режимы: EXPLORE, OPTIMIZE, DEFEND, REST
        self.state_memory = deque(maxlen=20) # Эпизодическая память состояний
        self.digital_habits = {}             # Словарь сформированных привычек
        self.stress_level = 0.1
        
        self.initialize_behavioral_matrix()

    def initialize_behavioral_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        zone = "SENSORY_CORE"
                    elif z == 1:
                        zone = "NEURAL_STRATEGY"
                    else:
                        zone = "HABIT_MEMORY"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        zone=zone,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        habit_weight=1.0,
                        active_behavior=False
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
                    self.graph.add_edge(u, v, synaptic_weight=1.0)

    def evaluate_behavioral_mode(self):
        # Поведенческий движок переключает стратегию по уровню стресса и энергии
        avg_energy = np.mean([d['energy'] for _, d in self.graph.nodes(data=True)])
        
        if avg_energy < 40.0:
            self.current_mode = "REST"
            self.stress_level = 0.8
        elif self.stress_level > 0.5:
            self.current_mode = "DEFEND"
        elif self.tick % 5 == 0:
            self.current_mode = "OPTIMIZE"
        else:
            self.current_mode = "EXPLORE"

    def process_behavior_cycle(self, token):
        self.tick += 1
        self.evaluate_behavioral_mode()
        
        # Запись текущего состояния в память состояний (State Memory)
        snapshot = {
            "tick": self.tick,
            "mode": self.current_mode,
            "token": int(token),
            "avg_energy": float(np.mean([d['energy'] for _, d in self.graph.nodes(data=True)]))
        }
        self.state_memory.append(snapshot)

        # Формирование цифровых привычек (Long-term patterns & Habits)
        pattern_key = f"{self.current_mode}_{token}"
        if pattern_key not in self.digital_habits:
            self.digital_habits[pattern_key] = 1.0
        else:
            self.digital_habits[pattern_key] += 0.25 # Привычка укрепляется при повторении

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            # Реакция на стимулы с учетом текущей стратегии режима
            modifier = 2 if self.current_mode == "OPTIMIZE" else 1
            data['state'] = Base4Operator.apply(data['state'], token * modifier, valenc)
            
            # Управление энергией в зависимости от режима
            if self.current_mode == "REST":
                data['energy'] = min(110.0, data['energy'] + 3.0)
                self.stress_level = max(0.0, self.stress_level - 0.1)
            elif self.current_mode == "DEFEND":
                data['energy'] = max(10.0, data['energy'] - 2.0)
                self.stress_level = min(1.0, self.stress_level + 0.15)
            else:
                data['energy'] = max(10.0, data['energy'] - 1.0)
                
            # Закрепление цифровых привычек в узлах памяти
            if data['zone'] == "HABIT_MEMORY":
                habit_boost = min(5.0, self.digital_habits.get(pattern_key, 1.0))
                data['habit_weight'] = habit_boost

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        # Цветовая палитра зависит от активного поведенческого режима
        mode_colors = {
            "EXPLORE": 'viridis',
            "OPTIMIZE": 'plasma',
            "DEFEND": 'inferno',
            "REST": 'cividis'
        }
        colormap = plt.get_cmap(mode_colors.get(self.current_mode, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"Behavior Engine V33 [{self.current_mode}] Tick: {self.tick:02d}")
        
        fname = f"v33_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V33-BEHAVIOR] Рендер кадра режима [{self.current_mode}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v33_behavior.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V33-BEHAVIOR] Мастер-гифка поведенческой системы сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_behavior_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V33-BEHAVIOR] Цикл завершен. Память состояний содержит {len(self.state_memory)} записей. Привычек сформировано: {len(self.digital_habits)}")

if __name__ == "__main__":
    organism = BehavioralSuperorganismV33()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
