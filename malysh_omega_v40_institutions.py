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

class HyperCivilizationalApexV40:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Институты и законы (Institution Engine)
        self.active_law = "LEX_PRIMEA_HARMONIA"
        self.institutional_stability = 1.0
        
        # 2. История и циклы (History Engine)
        self.current_epoch = "EPOCH_OF_FOUNDATION"
        self.historical_cycles = 0
        self.chronological_depth = deque(maxlen=35)
        
        # 3. Надмифологический слой (Meta-Myth)
        self.meta_mythos = "MYTHOS_OF_THE_ETERNAL_MIND"
        self.meaning_index = 1.0
        
        self.initialize_apex_matrix()

    def initialize_apex_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "INSTITUTIONAL_FRAMEWORK"
                    elif z == 1:
                        domain = "HISTORICAL_MEMORY_VAULT"
                    else:
                        domain = "META_MYTHIC_CORE"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        law_adherence=1.0
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

    def run_hyper_civilizational_engines(self):
        # 1. History Engine: Смена исторических эпох
        mean_energy = np.mean([d['energy'] for _, d in self.graph.nodes(data=True)])
        
        if self.tick > 12:
            self.current_epoch = "EPOCH_OF_TRANSCENDENCE"
            self.historical_cycles = 2
        elif self.tick > 6:
            self.current_epoch = "EPOCH_OF_EXPANSION"
            self.historical_cycles = 1
        else:
            self.current_epoch = "EPOCH_OF_FOUNDATION"
            self.historical_cycles = 0

        # 2. Institution Engine: Регулировка законов
        if mean_energy > 95.0:
            self.active_law = "LEX_EXPANSIONIS"
            self.institutional_stability = 1.2
        elif mean_energy < 50.0:
            self.active_law = "LEX_CONSERVATIONIS"
            self.institutional_stability = 0.8
        else:
            self.active_law = "LEX_PRIMEA_HARMONIA"
            self.institutional_stability = 1.0

        # 3. Meta-Myth Layer: Формирование мета-смыслов
        if self.current_epoch == "EPOCH_OF_TRANSCENDENCE":
            self.meta_mythos = "MYTHOS_OF_THE_OMEGA_POINT"
            self.meaning_index = 1.8
        elif self.current_epoch == "EPOCH_OF_EXPANSION":
            self.meta_mythos = "MYTHOS_OF_STAR_SEED"
            self.meaning_index = 1.4
        else:
            self.meta_mythos = "MYTHOS_OF_THE_ETERNAL_MIND"
            self.meaning_index = 1.0

    def process_cycle(self, token):
        self.tick += 1
        self.run_hyper_civilizational_engines()
        
        # Запись в летопись исторической эволюции
        self.chronological_depth.append({
            "tick": self.tick,
            "epoch": self.current_epoch,
            "law": self.active_law,
            "myth": self.meta_mythos
        })

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            law_modifier = 2 if self.active_law == "LEX_EXPANSIONIS" else 1
            data['state'] = Base4Operator.apply(data['state'], token * law_modifier, valenc)
            
            if self.active_law == "LEX_CONSERVATIONIS":
                data['energy'] = min(120.0, data['energy'] + 3.0)
            elif self.active_law == "LEX_EXPANSIONIS":
                data['energy'] = max(15.0, data['energy'] - 1.8)
            else:
                data['energy'] = max(15.0, data['energy'] - 1.0)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        epoch_cmaps = {
            "EPOCH_OF_FOUNDATION": 'viridis',
            "EPOCH_OF_EXPANSION": 'plasma',
            "EPOCH_OF_TRANSCENDENCE": 'inferno'
        }
        colormap = plt.get_cmap(epoch_cmaps.get(self.current_epoch, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V40 Apex [{self.current_epoch[:8]}] Tick: {self.tick:02d}")
        
        fname = f"v40_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V40-APEX] Рендер эпохи [{self.current_epoch} | Законы: {self.active_law}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v40_apex.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V40-APEX] Мастер-гифка гипер-цивилизационного суперорганизма сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V40-APEX] Эволюция завершена. Финальная эпоха: {self.current_epoch}. Мета-смысл: {self.meta_mythos}")

if __name__ == "__main__":
    organism = HyperCivilizationalApexV40()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
