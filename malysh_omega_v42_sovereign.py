import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, time, math
from collections import deque
from PIL import Image

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class SovereignExoNodeV42:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Новая энергетическая матрица
        self.global_energy_pool = 1000.0
        
        # 2. Иммунный щит и семантический конвертер
        self.immune_shield_mode = "ACTIVE_CONVERSION"
        self.neutralized_threats = 0
        
        # 3. Реальный экзо-вход (Real Sensor)
        self.last_real_entropy = 0
        
        # 4. Настоящий исторический лог (True Beacon Log)
        self.log_filename = "malysh_beacon_history.log"
        
        self.initialize_sovereign_matrix()

    def initialize_sovereign_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    if z == 0:
                        domain = "EXO_SENSOR_SURFACE"
                    elif z == 1:
                        domain = "IMMUNE_REACTOR_CORE"
                    else:
                        domain = "SOVEREIGN_BEACON_VAULT"

                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        domain=domain,
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=95.0,
                        resonance=1.0
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

    def fetch_real_external_data(self):
        # Реальный датчик: берем байт системной энтропии ОС и микросекунды времени
        entropy_byte = os.urandom(1)[0]
        time_seed = int(time.time() * 1000) % 4
        token = (entropy_byte + time_seed) % 4
        self.last_real_entropy = entropy_byte
        return token

    def process_cycle(self):
        self.tick += 1
        
        # Получаем реальные внешние данные
        external_token = self.fetch_real_external_data()
        
        # Иммунный щит: анализируем токсичность токена
        if external_token >= 3:
            self.immune_shield_mode = "TOXIC_NEUTRALIZED_TO_ENERGY"
            self.neutralized_threats += 1
            shield_energy_delta = +4.0  # Токсичность переплавляется в топливо!
        else:
            self.immune_shield_mode = "HARMONIC_ABSORPTION"
            shield_energy_delta = +2.0

        total_energy_sum = 0
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            valenc = (z + sum(data['dna']) + self.tick) % 4
            
            data['state'] = Base4Operator.apply(data['state'], external_token, valenc)
            
            # Улучшенный энергообмен (гомеостаз)
            data['energy'] = max(20.0, min(150.0, data['energy'] + shield_energy_delta - 1.2))
            total_energy_sum += data['energy']

        self.global_energy_pool = total_energy_sum

        # Запись в настоящий лог-файл (True Beacon Log)
        log_entry = {
            "tick": self.tick,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "real_entropy_byte": self.last_real_entropy,
            "external_token": external_token,
            "immune_mode": self.immune_shield_mode,
            "neutralized_total": self.neutralized_threats,
            "global_energy": round(self.global_energy_pool, 2)
        }
        
        with open(self.log_filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(f"[V42-SOVEREIGN] Тик {self.tick:02d} | Сенсор: {external_token} | Щит: {self.immune_shield_mode} | Энергия сети: {self.global_energy_pool:.1f}")

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('plasma')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 150.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V42 Sovereign Node | Tick: {self.tick:02d}")
        
        fname = f"v42_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v42_sovereign.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V42-SOVEREIGN] Мастер-гифка суверенного узла сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, cycles=18):
        for _ in range(cycles):
            self.process_cycle()
            self.render_frame()
        self.compile_gif()
        print(f"\n[V42-SOVEREIGN] Эволюция завершена. Логи записаны в {self.log_filename}")

if __name__ == "__main__":
    node = SovereignExoNodeV42()
    node.run(cycles=18)
