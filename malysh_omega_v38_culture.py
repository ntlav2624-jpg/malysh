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

class CultureEngineSuperorganismV38:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Культурные паттерны и традиции (Culture Engine)
        self.active_tradition = "RUAL_OF_HARMONY"
        self.tradition_strength = 1.0
        
        # 2. Коллективное обучение и социальная память (Group Learning)
        self.social_memory = deque(maxlen=25)
        self.collective_pattern_score = 0.5
        
        # 3. Надсоциальный слой (Meta-Social Layer)
        self.meta_social_profile = "COOPERATIVE_CIVILIZATION"
        self.interaction_optimizer = 1.0
        
        self.initialize_culture_matrix()

    def initialize_culture_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "CULTURAL_RITUAL_SURFACE"
                    elif z == 1:
                        domain = "GROUP_MEMORY_CORE"
                    else:
                        domain = "META_SOCIAL_ANALYTICS"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        cultural_weight=1.0
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

    def run_meta_social_and_culture(self):
        # 1. Meta-Social Layer: Анализ и прогнозирование социальных состояний
        mean_energy = np.mean([d['energy'] for _, d in self.graph.nodes(data=True)])
        
        if mean_energy > 90.0:
            self.meta_social_profile = "EXPANSIVE_CIVILIZATION"
            self.interaction_optimizer = 1.2
            self.active_tradition = "RITUAL_OF_EXPANSION"
        elif mean_energy < 55.0:
            self.meta_social_profile = "PRESERVING_TRIBAL_MODE"
            self.interaction_optimizer = 0.8
            self.active_tradition = "RITUAL_OF_PRESERVATION"
        else:
            self.meta_social_profile = "STABLE_NOOSPHERE"
            self.interaction_optimizer = 1.0
            self.active_tradition = "RITUAL_OF_BALANCE"

        # 2. Group Learning: Накопление социальной памяти
        self.collective_pattern_score = min(1.0, mean_energy / 100.0)
        self.tradition_strength = min(2.0, self.tradition_strength + 0.05)

    def process_cycle(self, token):
        self.tick += 1
        self.run_meta_social_and_culture()
        
        # Запись в социальную память
        self.social_memory.append({
            "tick": self.tick,
            "tradition": self.active_tradition,
            "profile": self.meta_social_profile
        })

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            culture_mod = 2 if self.active_tradition == "RITUAL_OF_EXPANSION" else 1
            data['state'] = Base4Operator.apply(data['state'], token * culture_mod, valenc)
            
            if self.active_tradition == "RITUAL_OF_PRESERVATION":
                data['energy'] = min(120.0, data['energy'] + 2.5)
            elif self.active_tradition == "RITUAL_OF_EXPANSION":
                data['energy'] = max(15.0, data['energy'] - 1.5)
            else:
                data['energy'] = max(15.0, data['energy'] - 1.0)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        tradition_cmaps = {
            "RITUAL_OF_EXPANSION": 'plasma',
            "RITUAL_OF_PRESERVATION": 'inferno',
            "RITUAL_OF_BALANCE": 'viridis'
        }
        colormap = plt.get_cmap(tradition_cmaps.get(self.active_tradition, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V38 Culture [{self.active_tradition[:10]}] Tick: {self.tick:02d}")
        
        fname = f"v38_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V38-CULTURE] Рендер традиции [{self.active_tradition} | Профиль: {self.meta_social_profile}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v38_culture.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V38-CULTURE] Мастер-гифка культурного суперорганизма сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V38-CULTURE] Эволюция завершена. Активная традиция: {self.active_tradition}. Сила традиций: {self.tradition_strength:.2f}")

if __name__ == "__main__":
    organism = CultureEngineSuperorganismV38()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
