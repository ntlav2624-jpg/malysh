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

class MalyshTissueOrganoidV25:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v25_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Многоуровневые поля сигнальных молекул (гормонов)
        self.hormone_field = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.chem_A = np.ones((x_size, y_size, z_layers), dtype=float) * 1.0
        self.chem_B = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_layered_continuum()

    def initialize_layered_continuum(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Многослойная тканевая дифференциация
                    if z == 0:
                        tissue = "EPITHELIUM"
                        organ = "CHEMICAL_CENTER" # Нижний слой выделяет химию
                    elif z == 1:
                        tissue = "PARENCHYMA"
                        organ = "NEURAL_NODE"    # Средний слой думает и передает спайки
                    else:
                        tissue = "VASCULAR_CORE"
                        organ = "HEART"          # Верхний слой качает энергию

                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        tissue_layer=tissue,
                        organ_type=organ,
                        state=0,
                        energy=80.0,
                        temperature=25.0,
                        potential=-70.0,
                        contraction=0.0,         # Степень сокращения (для сердца)
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
                    self.graph.add_edge(u, v, weight=1.0, bandwidth=1.5, signaling_flow=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[TISSUE-V25] Холодный старт многослойного континуума.")
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
            print(f"[TISSUE-V25] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[TISSUE-V25] Ошибка чтения WAL: {e}")
            return False

    def process_tissue_dynamics(self, val, spiral_points):
        # 1. Диффузия межклеточных сигнальных молекул (гормонов)
        lap_hormone = np.zeros_like(self.hormone_field)
        for x in range(self.x_size):
            for y in range(self.y_size):
                for z in range(self.z_layers):
                    sum_h, count = 0.0, 0
                    for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                        nx, ny, nz = x+dx, y+dy, z+dz
                        if 0 <= nx < self.x_size and 0 <= ny < self.y_size and 0 <= nz < self.z_layers:
                            sum_h += self.hormone_field[nx, ny, nz]
                            count += 1
                    if count > 0:
                        lap_hormone[x, y, z] = (sum_h / count) - self.hormone_field[x, y, z]

        self.hormone_field += (0.15 * lap_hormone) * 0.9
        self.hormone_field = np.clip(self.hormone_field, 0.0, 1.0)

        # 2. Спиральная инжекция
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    data['energy'] = min(150.0, data['energy'] + 50.0)
                    data['temperature'] += 10.0
                    if 0 <= sx < self.x_size and 0 <= sy < self.y_size and 0 <= sz < self.z_layers:
                        self.hormone_field[sx, sy, sz] = min(1.0, self.hormone_field[sx, sy, sz] + 0.8)

        # 3. Специализированная физика органов (Heart, Neural, Chemical Center)
        heart_rhythm = math.sin(self.tick * 0.8) # Водитель ритма сердца

        for node, data in list(self.graph.nodes(data=True)):
            x, y, z = data['xyzt'][:3]
            local_hormone = self.hormone_field[x, y, z] if (0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers) else 0.1

            if data['organ_type'] == "HEART":
                # Сердце сокращается в такт с ритмом и перекачивает энергию соседям
                data['contraction'] = (heart_rhythm + 1.0) * 0.5
                data['temperature'] += data['contraction'] * 2.0
                data['energy'] = max(10.0, data['energy'] - 1.5)

            elif data['organ_type'] == "NEURAL_NODE":
                # Нейронный узел возбуждается от гормонов и тепла
                data['potential'] += (data['temperature'] * 0.15) + (local_hormone * 10.0) - 2.0
                if data['potential'] > -25.0:
                    data['spike'] = True
                    data['potential'] = -80.0
                    data['temperature'] += 6.0
                    # Нейрон при спайке выделяет гормон в межклеточную среду
                    if 0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers:
                        self.hormone_field[x, y, z] = min(1.0, self.hormone_field[x, y, z] + 0.4)
                else:
                    data['spike'] = False
                    data['potential'] = max(-90.0, data['potential'] - 2.0)

            elif data['organ_type'] == "CHEMICAL_CENTER":
                # Химический центр постоянно синтезирует базовый гормональный фон
                if 0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers:
                    self.hormone_field[x, y, z] = min(1.0, self.hormone_field[x, y, z] + 0.1)
                data['energy'] = min(100.0, data['energy'] + 1.0)

            data['temperature'] = max(20.0, data['temperature'] - 2.0)

        # 4. Межорганоидный обмен по рёбрам
        for u, v, data in self.graph.edges(data=True):
            if u in self.graph and v in self.graph:
                u_en = self.graph.nodes[u]['energy']
                v_en = self.graph.nodes[v]['energy']
                diff = u_en - v_en
                transfer = diff * 0.1 * data['bandwidth']
                if u_en > transfer and v_en + transfer >= 0:
                    self.graph.nodes[u]['energy'] -= transfer
                    self.graph.nodes[v]['energy'] += transfer
                    data['signaling_flow'] = abs(transfer)

        # Base-4 метаболизм
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
            n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)

    def render_tissue_frame(self, cam_angle):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('seismic')
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            if 0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers:
                voxel_array[x, y, z] = True
                # Цветовая дифференциация по слоям и органам
                base_color = 0.2 if data['organ_type'] == "CHEMICAL_CENTER" else (0.5 if data['organ_type'] == "NEURAL_NODE" else 0.9)
                hormone_mod = self.hormone_field[x, y, z] * 0.3
                norm_val = min(1.0, max(0.0, base_color + hormone_mod))
                rgba = colormap(norm_val)
                color_array[x, y, z] = matplotlib.colors.rgb2hex(rgba[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        elevation = 30 + 15 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Tissue-Organoid V25 [Tick: {self.tick:03d}]")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Tissue Layer (Z)")
        
        filename = f"v25_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[TISSUE-V25] Рендер тканевого кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        print("[TISSUE-V25] Компиляция мастер-анимации тканевого континуума...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_tissue_organoid_continuum.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[TISSUE-V25] Мастер-анимация сохранена: {gif_name}")
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

            self.process_tissue_dynamics(val, spiral_points)
            self.render_tissue_frame(self.tick * 0.4)

        self.compile_animation()

        nodes_data = {str(n): d for n, d in self.graph.nodes(data=True)}
        edges_data = [(str(u), str(v), d) for u, v, d in self.graph.edges(data=True)]
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "nodes": nodes_data, "edges": edges_data}) + "\n")
        print(f"\n[TISSUE-V25] Цикл завершен. Тактов: {self.tick}. Узлов в ткани: {self.graph.number_of_nodes()}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshTissueOrganoidV25()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
