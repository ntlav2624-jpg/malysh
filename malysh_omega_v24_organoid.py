import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, math
from PIL import Image

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class MalyshOrganoidV24:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v24_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Химическое поле Тьюринга
        self.chem_A = np.ones((x_size, y_size, z_layers), dtype=float) * 1.0
        self.chem_B = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_organoid_continuum()

    def initialize_organoid_continuum(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Распределение по органоидным зонам в зависимости от координат
                    if z == 0:
                        organ_type = "METABOLIC_CORE"   # Энергетика и масса
                    elif z == 1:
                        organ_type = "NEURAL_ORGANOID"  # Спайки и осцилляции
                    else:
                        organ_type = "SENSORY_SHELL"    # Регуляция и внешние связи

                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        organ=organ_type,
                        gene_expr=np.random.uniform(0.5, 1.5), # Генетический регулятор
                        state=0,
                        energy=70.0,
                        temperature=25.0,
                        mass=20.0,
                        potential=-70.0,
                        spike=False
                    )
                    node_id += 1

        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                if dist <= 1 or (dist == 2 and uz != vz):
                    # Синапс с весом и пластичностью
                    self.graph.add_edge(u, v, weight=1.0, plasticity=1.0, flow=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[ORGANOID-V24] Холодный старт многоорганного континуума.")
            return False
        try:
            with open(self.wal_file, "r") as f:
                lines = f.readlines()
                if not lines: return False
                last_record = json.loads(lines[-1].strip())
                self.tick = last_record["tick"]
                self.graph.clear()
                for nid_str, data in last_record["nodes"].items():
                    self.graph.add_node(int(nid_str), **data)
                for u_str, v_str, data in last_record["edges"]:
                    self.graph.add_edge(int(u_str), int(v_str), **data)
            print(f"[ORGANOID-V24] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[ORGANOID-V24] Ошибка чтения WAL: {e}")
            return False

    def process_organoid_dynamics(self, val, spiral_points):
        # 1. Глобальные нейронные осцилляции (ритм мозга континуума)
        global_oscillation = math.sin(self.tick * 0.5) * 5.0

        # 2. Reaction-Diffusion Химия
        Da, Db, f, k = 0.2, 0.1, 0.035, 0.065
        lap_A = np.zeros_like(self.chem_A)
        lap_B = np.zeros_like(self.chem_B)

        for x in range(self.x_size):
            for y in range(self.y_size):
                for z in range(self.z_layers):
                    sum_a, sum_b, count = 0.0, 0.0, 0
                    for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                        nx, ny, nz = x+dx, y+dy, z+dz
                        if 0 <= nx < self.x_size and 0 <= ny < self.y_size and 0 <= nz < self.z_layers:
                            sum_a += self.chem_A[nx, ny, nz]
                            sum_b += self.chem_B[nx, ny, nz]
                            count += 1
                    if count > 0:
                        lap_A[x, y, z] = (sum_a / count) - self.chem_A[x, y, z]
                        lap_B[x, y, z] = (sum_b / count) - self.chem_B[x, y, z]

        A, B = self.chem_A, self.chem_B
        abb = A * (B ** 2)
        self.chem_A += (Da * lap_A - abb + f * (1.0 - A)) * 0.8
        self.chem_B += (Db * lap_B + abb - (f + k) * B) * 0.8
        self.chem_A = np.clip(self.chem_A, 0.0, 1.0)
        self.chem_B = np.clip(self.chem_B, 0.0, 1.0)

        # Спиральная инжекция энергии в органы
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    data['energy'] = min(150.0, data['energy'] + 45.0 * data['gene_expr'])
                    data['temperature'] += 8.0
                    if 0 <= sx < self.x_size and 0 <= sy < self.y_size and 0 <= sz < self.z_layers:
                        self.chem_B[sx, sy, sz] = min(1.0, self.chem_B[sx, sy, sz] + 0.5)

        # 3. Нейродинамика, генетическая регуляция и синаптическое обучение (STDP)
        for node in list(self.graph.nodes()):
            n_data = self.graph.nodes[node]
            x, y, z = n_data['xyzt'][:3]
            chem_val = self.chem_B[x, y, z] if (0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers) else 0.1
            
            # Потенциал с учетом генетического регулятора и глобальных осцилляций
            n_data['potential'] += (n_data['temperature'] * 0.1) + (chem_val * 6.0) + (global_oscillation * n_data['gene_expr']) - 1.2
            
            if n_data['potential'] > -22.0:
                n_data['spike'] = True
                n_data['potential'] = -80.0
                n_data['temperature'] += 5.0
            else:
                n_data['spike'] = False
                n_data['potential'] = max(-90.0, n_data['potential'] - 2.0)

            n_data['temperature'] = max(20.0, n_data['temperature'] - 2.0)

        # Синаптическая пластичность (укрепление связей между активными узлами)
        for u, v, data in self.graph.edges(data=True):
            if u in self.graph and v in self.graph:
                u_spike = self.graph.nodes[u]['spike']
                v_spike = self.graph.nodes[v]['spike']
                if u_spike and v_spike:
                    data['plasticity'] = min(5.0, data['plasticity'] + 0.2) # Hebbian learning
                    data['weight'] += 0.1
                else:
                    data['plasticity'] = max(0.2, data['plasticity'] - 0.02) # Затухание неиспользуемых связей

        # 4. Морфогенез и деление органов
        nodes_to_add = []
        for node, data in list(self.graph.nodes(data=True)):
            if data['energy'] > 110.0 and data['organ'] == "METABOLIC_CORE" and self.graph.number_of_nodes() < 90:
                ux, uy, uz, _ = data['xyzt']
                new_id = max(self.graph.nodes()) + 1
                nodes_to_add.append((new_id, {
                    'xyzt': [(ux + 1) % self.x_size, (uy + 1) % self.y_size, uz, 0],
                    'organ': "NEURAL_ORGANOID",
                    'gene_expr': data['gene_expr'] * 1.05,
                    'state': data['state'],
                    'energy': 50.0,
                    'temperature': 30.0,
                    'mass': 15.0,
                    'potential': -70.0,
                    'spike': False
                }))
                data['energy'] -= 40.0

        for nid, n_attrs in nodes_to_add:
            self.graph.add_node(nid, **n_attrs)
            self.graph.add_edge(nid, nid - 1, weight=1.2, plasticity=1.0, flow=0.0)

        # Base-4 метаболизм
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
            n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)

    def render_organoid_frame(self, cam_angle):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('coolwarm')
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            if 0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers:
                voxel_array[x, y, z] = True
                # Цвет зависит от типа органа и потенциала
                organ_mod = 0.2 if data['organ'] == "METABOLIC_CORE" else (0.6 if data['organ'] == "NEURAL_ORGANOID" else 0.9)
                norm_val = min(1.0, max(0.0, organ_mod + (data['temperature'] - 20.0) / 100.0))
                rgba = colormap(norm_val)
                color_array[x, y, z] = matplotlib.colors.rgb2hex(rgba[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        elevation = 30 + 15 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Organoid V24 [Tick: {self.tick:03d}, Nodes: {self.graph.number_of_nodes()}]")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v24_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[ORGANOID-V24] Рендер многоорганного кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        print("[ORGANOID-V24] Компиляция мастер-анимации органоидов...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_organoid_continuum.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[ORGANOID-V24] Мастер-анимация сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run_engine(self, stream):
        self.recover_from_wal()

        for val in stream:
            self.tick += 1
            spiral_points = []
            for d_t in range(3):
                s_angle = (self.tick - d_t) * 0.4
                radius = 0.35 * math.exp(0.08 * s_angle)
                sx = int(abs(radius * math.cos(s_angle)) * 2) % self.x_size
                sy = int(abs(radius * math.sin(s_angle)) * 2) % self.y_size
                sz = (self.tick - d_t) % self.z_layers
                spiral_points.append((sx, sy, sz))

            self.process_organoid_dynamics(val, spiral_points)
            self.render_organoid_frame(self.tick * 0.4)

        self.compile_animation()

        nodes_data = {str(n): d for n, d in self.graph.nodes(data=True)}
        edges_data = [(str(u), str(v), d) for u, v, d in self.graph.edges(data=True)]
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "nodes": nodes_data, "edges": edges_data}) + "\n")
        print(f"\n[ORGANOID-V24] Цикл завершен. Тактов: {self.tick}. Узлов в органоидах: {self.graph.number_of_nodes()}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshOrganoidV24()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
