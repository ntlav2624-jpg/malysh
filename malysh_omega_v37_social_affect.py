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

class SocialAffectiveSuperorganismV37:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Мотивационные контуры и желания (Drive System)
        self.desires = {"stability": 1.0, "expansion": 0.5, "harmony": 0.8}
        self.current_goal = "HARMONIC_COOPERATION"
        
        # 2. Социальный слой (Social Layer)
        self.social_field = 0.5
        self.cooperative_index = 1.0
        
        # 3. Надэмоциональный слой (Meta-Affect)
        self.emotional_profile = "BALANCED_COOPERATOR"
        self.affect_history = deque(maxlen=20)
        self.emotional_regulation = 1.0
        
        self.initialize_social_matrix()

    def initialize_social_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "SOCIAL_INTERFACE"
                    elif z == 1:
                        domain = "DRIVE_MOTIVATION"
                    else:
                        domain = "META_AFFECT_CORE"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        coop_factor=1.0
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

    def run_meta_affect_and_drives(self):
        # 1. Meta-Affect: Анализ и регулировка эмоций
        energies = [d['energy'] for _, d in self.graph.nodes(data=True)]
        mean_energy = np.mean(energies)
        
        if mean_energy > 95.0:
            self.emotional_profile = "EUPHORIC_ALTRUIST"
            self.emotional_regulation = 0.8
        elif mean_energy < 50.0:
            self.emotional_profile = "DEFENSIVE_CAUTIOUS"
            self.emotional_regulation = 1.4
        else:
            self.emotional_profile = "BALANCED_COOPERATOR"
            self.emotional_regulation = 1.0

        # 2. Drive System: Смена целей на основе эмоционального профиля
        if self.emotional_profile == "DEFENSIVE_CAUTIOUS":
            self.current_goal = "SEEK_SAFETY"
            self.desires["stability"] = 1.8
        elif self.emotional_profile == "EUPHORIC_ALTRUIST":
            self.current_goal = "SOCIAL_EXPANSION"
            self.desires["expansion"] = 1.5
        else:
            self.current_goal = "HARMONIC_COOPERATION"
            self.desires["harmony"] = 1.2

        # 3. Social Layer: Симуляция внешнего социального поля
        self.social_field = 0.5 + 0.3 * math.sin(self.tick * 0.5)
        if self.social_field > 0.7:
            self.cooperative_index = min(2.0, self.cooperative_index + 0.1)
        else:
            self.cooperative_index = max(0.5, self.cooperative_index - 0.05)

    def process_cycle(self, token):
        self.tick += 1
        self.run_meta_affect_and_drives()
        
        self.affect_history.append({
            "tick": self.tick,
            "profile": self.emotional_profile,
            "goal": self.current_goal
        })

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            social_mod = (2 if self.current_goal == "SOCIAL_EXPANSION" else 1) * int(self.cooperative_index)
            data['state'] = Base4Operator.apply(data['state'], token * social_mod, valenc)
            
            if self.current_goal == "SEEK_SAFETY":
                data['energy'] = min(120.0, data['energy'] + 3.0)
            elif self.current_goal == "SOCIAL_EXPANSION":
                data['energy'] = max(15.0, data['energy'] - 1.5)
            else:
                data['energy'] = max(15.0, data['energy'] - 1.0)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        profile_cmaps = {
            "EUPHORIC_ALTRUIST": 'plasma',
            "DEFENSIVE_CAUTIOUS": 'inferno',
            "BALANCED_COOPERATOR": 'viridis'
        }
        colormap = plt.get_cmap(profile_cmaps.get(self.emotional_profile, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V37 [{self.emotional_profile}] Goal: {self.current_goal[:8]} Tick: {self.tick:02d}")
        
        fname = f"v37_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V37-SOCIAL] Рендер профиля [{self.emotional_profile} | Цель: {self.current_goal}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v37_social_affect.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V37-SOCIAL] Мастер-гифка социального суперорганизма сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V37-SOCIAL] Эволюция завершена. Профиль: {self.emotional_profile}. Кооперативный индекс: {self.cooperative_index:.2f}")

if __name__ == "__main__":
    organism = SocialAffectiveSuperorganismV37()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
