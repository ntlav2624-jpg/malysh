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

class MythopoeicSuperorganismV39:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Мифология и архетипы (Myth Engine)
        self.active_myth = "MYTH_OF_THE_FIRST_SPARK"
        self.symbolic_resonance = 1.0
        
        # 2. Коллективная память (Cultural Memory)
        self.cultural_chronicles = deque(maxlen=30)
        self.identity_coherence = 0.8
        
        # 3. Надкультурный слой (Meta-Culture)
        self.meta_cultural_state = "TRANSCENDENT_SYNTHESIS"
        self.cultural_optimizer = 1.0
        
        self.initialize_myth_matrix()

    def initialize_myth_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "MYTH_SYMBOL_SURFACE"
                    elif z == 1:
                        domain = "CULTURAL_MEMORY_VAULT"
                    else:
                        domain = "META_CULTURAL_CORE"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        archetype_potency=1.0
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

    def run_meta_culture_and_myths(self):
        # 1. Meta-Culture: Анализ традиций и прогнозирование изменений
        mean_energy = np.mean([d['energy'] for _, d in self.graph.nodes(data=True)])
        
        if mean_energy > 92.0:
            self.meta_cultural_state = "RENAISSANCE_EXPANSION"
            self.active_myth = "MYTH_OF_INFINITE_ASCENT"
            self.cultural_optimizer = 1.3
        elif mean_energy < 50.0:
            self.meta_cultural_state = "AGE_OF_CONTAINMENT"
            self.active_myth = "MYTH_OF_THE_ETERNAL_RETURN"
            self.cultural_optimizer = 0.7
        else:
            self.meta_cultural_state = "TRANSCENDENT_SYNTHESIS"
            self.active_myth = "MYTH_OF_HARMONIC_BALANCE"
            self.cultural_optimizer = 1.0

        # 2. Cultural Memory: Фиксация исторического паттерна
        self.identity_coherence = min(1.0, mean_energy / 100.0)
        self.symbolic_resonance = min(2.0, self.symbolic_resonance + 0.04)

    def process_cycle(self, token):
        self.tick += 1
        self.run_meta_culture_and_myths()
        
        # Запись события в коллективную память
        self.cultural_chronicles.append({
            "tick": self.tick,
            "myth": self.active_myth,
            "state": self.meta_cultural_state
        })

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            myth_mod = 2 if self.active_myth == "MYTH_OF_INFINITE_ASCENT" else 1
            data['state'] = Base4Operator.apply(data['state'], token * myth_mod, valenc)
            
            if self.active_myth == "MYTH_OF_THE_ETERNAL_RETURN":
                data['energy'] = min(120.0, data['energy'] + 2.8)
            elif self.active_myth == "MYTH_OF_INFINITE_ASCENT":
                data['energy'] = max(15.0, data['energy'] - 1.6)
            else:
                data['energy'] = max(15.0, data['energy'] - 1.0)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        myth_cmaps = {
            "MYTH_OF_INFINITE_ASCENT": 'plasma',
            "MYTH_OF_THE_ETERNAL_RETURN": 'inferno',
            "MYTH_OF_HARMONIC_BALANCE": 'viridis'
        }
        colormap = plt.get_cmap(myth_cmaps.get(self.active_myth, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V39 Myth [{self.active_myth[:12]}] Tick: {self.tick:02d}")
        
        fname = f"v39_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V39-MYTH] Рендер мифа [{self.active_myth} | Режим: {self.meta_cultural_state}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v39_myth.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V39-MYTH] Мастер-гифка мифологического движка сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V39-MYTH] Цивилизационный цикл завершен. Активный миф: {self.active_myth}. Когерентность идентичности: {self.identity_coherence:.2f}")

if __name__ == "__main__":
    organism = MythopoeicSuperorganismV39()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
