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

class PDESovereignContinuumV43:
    def __init__(self, x_size=5, y_size=5, z_layers=3):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # 1. Параметры PDE-модели (диффузия и диссипация)
        self.diffusion_coeff = 0.15
        self.dissipation_rate = 0.05
        
        # 2. Иммунный щит
        self.immune_status = "PDE_ABSORPTION_ACTIVE"
        self.neutralized_count = 0
        
        # 3. Лог-файл маяка
        self.log_filename = "malysh_pde_beacon.log"
        
        self.initialize_pde_matrix()

    def initialize_pde_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    self.graph.add_node(node_id,
                        xyzt=[x, y, z, 0],
                        dna=[np.random.randint(0,4) for _ in range(4)],
                        state=0,
                        energy=100.0, # Начальный потенциал поля
                        potential=0.0
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

    def fetch_real_sensor_data(self):
        # Реальный сенсорный ввод из энтропии ОС
        entropy_val = os.urandom(1)[0]
        time_seed = int(time.time() * 1000) % 4
        token = (entropy_val + time_seed) % 4
        return entropy_val, token

    def process_pde_cycle(self):
        self.tick += 1
        entropy_byte, token = self.fetch_real_sensor_data()
        
        # Иммунный щит обрабатывает экзо-данные
        if token >= 3:
            self.immune_status = "TOXIC_MUTATION_CONVERTED"
            self.neutralized_count += 1
            external_energy_injection = +15.0
        else:
            self.immune_status = "HARMONIC_FLUX_STABLE"
            external_energy_injection = +5.0

        # Шаг 1: Расчет PDE-диффузии энергии по сетке (дискретный аналог уравнения теплопроводности)
        new_energies = {}
        for node in self.graph.nodes():
            current_energy = self.graph.nodes[node]['energy']
            neighbors = list(self.graph.neighbors(node))
            
            # Лапласиан энергии (сумма разностей с соседями)
            laplacian = sum(self.graph.nodes[n]['energy'] - current_energy for n in neighbors)
            
            # PDE update: dE/dt = D * Laplacian - gamma * E + Injection
            d_energy = (self.diffusion_coeff * laplacian) - (self.dissipation_rate * current_energy)
            
            # Применение оператора Base4 для нелинейности состояния
            valenc = (sum(self.graph.nodes[node]['dna']) + self.tick) % 4
            self.graph.nodes[node]['state'] = Base4Operator.apply(
                self.graph.nodes[node]['state'], token, valenc
            )
            
            new_energies[node] = max(10.0, min(200.0, current_energy + d_energy + (external_energy_injection / len(self.graph.nodes()))))

        # Присвоение новых значений энергии узлам
        total_system_energy = 0
        for node, energy in new_energies.items():
            self.graph.nodes[node]['energy'] = energy
            total_system_energy += energy

        # Шаг 2: Запись в настоящий лог (True Beacon Log)
        log_entry = {
            "tick": self.tick,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "entropy_byte": entropy_byte,
            "sensor_token": token,
            "immune_mode": self.immune_status,
            "neutralized_threats": self.neutralized_count,
            "total_pde_energy": round(total_system_energy, 2)
        }
        
        with open(self.log_filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

        print(f"[V43-PDE] Тик {self.tick:02d} | Сенсор: {token} | Щит: {self.immune_status} | PDE Энергия поля: {total_system_energy:.1f}")

    def render_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('inferno')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm = min(1.0, data['energy'] / 200.0)
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 20)
        ax.set_title(f"V43 PDE Continuum | Tick: {self.tick:02d}")
        
        fname = f"v43_frame_{self.tick:02d}.png"
        plt.savefig(fname, dpi=110)
        plt.close(fig)
        self.frame_files.append(fname)

    def compile_gif(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_supreme_v43_pde.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=300, loop=0)
        print(f"[V43-PDE] Мастер-гифка PDE континуума сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, cycles=18):
        for _ in range(cycles):
            self.process_pde_cycle()
            self.render_frame()
        self.compile_gif()
        print(f"\n[V43-PDE] Эволюция завершена. Логи диффузии записаны в {self.log_filename}")

if __name__ == "__main__":
    continuum = PDESovereignContinuumV43()
    continuum.run(cycles=18)
