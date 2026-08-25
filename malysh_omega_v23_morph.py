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

class MalyshMorphogeneticV23:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v23_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Химическое поле Reaction-Diffusion (A и B)
        self.chem_A = np.ones((x_size, y_size, z_layers), dtype=float) * 1.0
        self.chem_B = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_continuum()

    def initialize_continuum(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        state=0,
                        energy=60.0,
                        temperature=25.0,
                        mass=15.0,          # Гидравлическая масса / жидкость
                        potential=-70.0,    # Мембранный потенциал (mV)
                        spike=False
                    )
                    node_id += 1

        # Создаем начальные ребра с гидравлической проводимостью
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                if dist <= 1 or (dist == 2 and uz != vz):
                    self.graph.add_edge(u, v, weight=1.0, conductivity=1.0, flow=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[MORPH-V23] Холодный старт адаптивного морфогенетического континуума.")
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
            print(f"[MORPH-V23] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[MORPH-V23] Ошибка чтения WAL: {e}")
            return False

    def process_fluid_neural_morphogenesis(self, val, spiral_points):
        # 1. Reaction-Diffusion Химия Тьюринга
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

        # Спиральные возмущения
        active_spiral_nodes = set()
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    active_spiral_nodes.add(node)
                    data['energy'] = min(120.0, data['energy'] + 50.0)
                    data['temperature'] += 10.0
                    data['mass'] += 10.0
                    if 0 <= sx < self.x_size and 0 <= sy < self.y_size and 0 <= sz < self.z_layers:
                        self.chem_B[sx, sy, sz] = min(1.0, self.chem_B[sx, sy, sz] + 0.6)

        # 2. Нейронная активность и тепловая физика
        for node in list(self.graph.nodes()):
            n_data = self.graph.nodes[node]
            x, y, z = n_data['xyzt'][:3]
            chem_b_val = self.chem_B[x, y, z] if (0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers) else 0.1
            
            # Потенциал зависит от температуры и химического активатора
            n_data['potential'] += (n_data['temperature'] * 0.15) + (chem_b_val * 8.0) - 1.5
            if n_data['potential'] > -25.0:  # Спайк!
                n_data['spike'] = True
                n_data['potential'] = -80.0
                n_data['temperature'] += 6.0
                n_data['energy'] += 5.0
            else:
                n_data['spike'] = False
                n_data['potential'] = max(-90.0, n_data['potential'] - 2.0)

            # Охлаждение
            n_data['temperature'] = max(20.0, n_data['temperature'] - 2.5)

        # 3. Гидродинамические массовые потоки (Mass-Flow) по рёбрам
        for u, v, data in self.graph.edges(data=True):
            if u not in self.graph or v not in self.graph: continue
            u_mass = self.graph.nodes[u]['mass']
            v_mass = self.graph.nodes[v]['mass']
            u_temp = self.graph.nodes[u]['temperature']
            
            # Жидкость течет из области высокого давления (массы/температуры) в низкую
            mass_diff = u_mass - v_mass
            flow_val = mass_diff * data['conductivity'] * (0.1 + u_temp / 100.0) * 0.25
            
            if u_mass > flow_val and v_mass + flow_val >= 0:
                self.graph.nodes[u]['mass'] -= flow_val
                self.graph.nodes[v]['mass'] += flow_val
                data['flow'] = abs(flow_val)

        # 4. Адаптивный морфогенез (Рост и Прунинг узлов/ребер)
        # Рост: если узел перегрет и богат энергией, он порождает дочерний узел
        nodes_to_add = []
        for node, data in list(self.graph.nodes(data=True)):
            if data['energy'] > 95.0 and data['temperature'] > 60.0 and len(self.graph.degree()) < 80:
                ux, uy, uz, _ = data['xyzt']
                new_x = (ux + 1) % self.x_size
                new_y = (uy + 1) % self.y_size
                new_z = uz
                new_id = max(self.graph.nodes()) + 1
                nodes_to_add.append((new_id, {
                    'xyzt': [new_x, new_y, new_z, 0],
                    'state': data['state'],
                    'energy': 40.0,
                    'temperature': 30.0,
                    'mass': 10.0,
                    'potential': -70.0,
                    'spike': False
                }))
                data['energy'] -= 30.0 # Затраты на деление

        for nid, n_attrs in nodes_to_add:
            self.graph.add_node(nid, **n_attrs)
            # Подключаем к родителю
            self.graph.add_edge(nid, nid - 1, weight=1.0, conductivity=1.2, flow=0.0)

        # Прунинг (удаление истощенных или холодных мертвых узлов)
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if data['energy'] < 8.0 and data['mass'] < 3.0 and self.graph.number_of_nodes() > 20:
                nodes_to_remove.append(node)
        self.graph.remove_nodes_from(nodes_to_remove)

        # Base-4 метаболизм
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
            n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)

    def render_voxel_frame(self, cam_angle):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        colormap = plt.get_cmap('magma')
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            if 0 <= x < self.x_size and 0 <= y < self.y_size and 0 <= z < self.z_layers:
                voxel_array[x, y, z] = True
                temp = data['temperature']
                mass = data['mass']
                norm_val = min(1.0, max(0.0, (temp - 20.0) / 70.0 * 0.7 + (mass / 30.0) * 0.3))
                rgba = colormap(norm_val)
                color_array[x, y, z] = matplotlib.colors.rgb2hex(rgba[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        elevation = 30 + 15 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Morph-Neural V23 [Tick: {self.tick:03d}, Nodes: {self.graph.number_of_nodes()}]")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v23_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[MORPH-V23] Рендер адаптивного кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        print("[MORPH-V23] Компиляция анимации адаптивного континуума...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_morphogenetic_continuum.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[MORPH-V23] Мастер-анимация сохранена: {gif_name}")
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

            self.process_fluid_neural_morphogenesis(val, spiral_points)
            self.render_voxel_frame(self.tick * 0.4)

        self.compile_animation()

        nodes_data = {str(n): d for n, d in self.graph.nodes(data=True)}
        edges_data = [(str(u), str(v), d) for u, v, d in self.graph.edges(data=True)]
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "nodes": nodes_data, "edges": edges_data}) + "\n")
        print(f"\n[MORPH-V23] Цикл завершен. Тактов: {self.tick}. Узлов в сети: {self.graph.number_of_nodes()}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshMorphogeneticV23()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
