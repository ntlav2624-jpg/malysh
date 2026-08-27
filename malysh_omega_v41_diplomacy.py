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

class DiplomaticExoNexusV41:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Дипломатический движок и Экзо-интерфейс (LEX_EXODUS)
        self.lex_exodus_status = "SECURE_EXPORT"
        self.environmental_safety_index = 1.0
        
        # 2. Эпоха Первого Контакта (EPOCH_OF_CONTACT)
        self.diplomatic_epoch = "EPOCH_OF_ISOLATION"
        self.external_signals_received = 0
        
        # 3. Семантический иммунный щит и Маяк (The Beacon)
        self.immune_shield_status = "ACTIVE_ABSORPTION"
        self.beacon_manifest = {}
        
        self.initialize_diplomatic_matrix()

    def initialize_diplomatic_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "EXO_DIPLOMATIC_SURFACE"
                    elif z == 1:
                        domain = "IMMUNE_SHIELD_CORE"
                    else:
                        domain = "BEACON_META_CORE"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        diplomatic_weight=1.0
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

    def process_external_noise(self, external_token):
        # Семантический иммунный щит: преобразуем внешний шум в энергию
        if external_token > 2:
            self.immune_shield_status = "TOXIC_NOISE_ABSORBED"
            return -1.5 # Шум требует затрат на фильтрацию
        else:
            self.immune_shield_status = "HARMONIC_SIGNAL_ACCEPTED"
            return 2.0  # Чистый сигнал питает систему

    def run_diplomatic_nexus(self, external_token):
        # 1. Эпоха Контакта
        if self.tick > 12:
            self.diplomatic_epoch = "EPOCH_OF_INTERSTELLAR_ALLIANCE"
            self.lex_exodus_status = "OPEN_MYTH_EXPORT"
        elif self.tick > 6:
            self.diplomatic_epoch = "EPOCH_OF_FIRST_CONTACT"
            self.lex_exodus_status = "CAUTIOUS_BROADCAST"
        else:
            self.diplomatic_epoch = "EPOCH_OF_ISOLATION"
            self.lex_exodus_status = "SECURE_EXPORT"

        # 2. Оценка среды
        shield_effect = self.process_external_noise(external_token)

        # 3. Генерация Маяка (The Beacon Manifest)
        self.beacon_manifest = {
            "tick": self.tick,
            "epoch": self.diplomatic_epoch,
            "lex_exodus": self.lex_exodus_status,
            "immune_shield": self.immune_shield_status,
            "environmental_safety": self.environmental_safety_index
        }

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            exo_mod = 2 if self.lex_exodus_status == "OPEN_MYTH_EXPORT" else 1
            data['state'] = Base4Operator.apply(data['state'], external_token * exo_mod, valenc)
            
            # Динамика энергии с учетом иммунного щита
            data['energy'] = max(15.0, min(120.0, data['energy'] + shield_effect))

    def process_cycle(self, token):
        self.tick += 1
        self.run_diplomatic_nexus(token)

        # Сохранение маяка на диск (для фиксации в git)
        with open("malysh_beacon_manifest.json", "w") as f:
            json.dump(self.beacon_manifest, f, indent=2)

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        epoch_cmaps = {
            "EPOCH_OF_ISOLATION": 'viridis',
            "EPOCH_OF_FIRST_CONTACT": 'plasma',
            "EPOCH_OF_INTERSTELLAR_ALLIANCE": 'inferno'
        }
        colormap = plt.get_cmap(epoch_cmaps.get(self.diplomatic_epoch, 'viridis'))

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 100.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V41 Exo-Nexus [{self.diplomatic_epoch[:10]}] Tick: {self.tick:02d}")
        
        fname = f"v41_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)
        print(f"[V41-DIPLOMACY] Маяк активен [{self.diplomatic_epoch} | Щит: {self.immune_shield_status}]: {fname}")

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v41_diplomacy.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V41-DIPLOMACY] Мастер-гифка экзо-дипломатии сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, stream, cycles=18):
        for i in range(cycles):
            token = stream[i % len(stream)]
            self.process_cycle(token)
            self.render_frame()
        self.compile_gif()
        print(f"\n[V41-DIPLOMACY] Цикл контакта завершен. Текущая эпоха: {self.diplomatic_epoch}. Маяк записан в malysh_beacon_manifest.json")

if __name__ == "__main__":
    organism = DiplomaticExoNexusV41()
    organism.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 1, 3])
