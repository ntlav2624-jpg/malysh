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

class MalyshBioChemicalV22:
    def __init__(self, x_size=4, y_size=4, z_layers=3, wal="malysh_v22_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.layers = {}
        self.tick = 0
        self.frame_files = []
        
        # Химические матрицы Reaction-Diffusion (A - активатор, B - ингибитор)
        self.chem_A = np.ones((x_size, y_size, z_layers), dtype=float) * 1.0
        self.chem_B = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_continuum()

    def initialize_continuum(self):
        node_id = 0
        for z in range(self.z_layers):
            layer_nodes = []
            for y in range(self.y_size):
                for x in range(self.x_size):
                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        layer=z,
                        state=0,
                        energy=50.0,
                        temperature=25.0,
                        mass=10.0,          # Материальный запас в узле
                        potential=-70.0,    # Мембранный потенциал нейрона (mV)
                        spike=False,
                        is_spiral=False
                    )
                    layer_nodes.append(node_id)
                    node_id += 1
            self.layers[z] = layer_nodes

        for u in self.graph.nodes():
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for v in self.graph.nodes():
                if u < v:
                    vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                    dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                    if dist <= 1 or (dist == 2 and uz != vz):
                        # Добавляем проводимость массы и веса
                        self.graph.add_edge(u, v, weight=1.0, capacity=20.0, flow_rate=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[BIO-CHEMICAL V22] Холодный старт био-химического континуума.")
            return False
        try:
            with open(self.wal_file, "r") as f:
                lines = f.readlines()
                if not lines: return False
                last_record = json.loads(lines[-1].strip())
                self.tick = last_record["tick"]
                for nid_str, data in last_record["states"].items():
                    nid = int(nid_str)
                    if nid in self.graph:
                        self.graph.nodes[nid]['state'] = data["state"]
                        self.graph.nodes[nid]['energy'] = data["energy"]
                        self.graph.nodes[nid]['temperature'] = data["temp"]
                        self.graph.nodes[nid]['mass'] = data["mass"]
                        self.graph.nodes[nid]['potential'] = data["potential"]
            print(f"[BIO-CHEMICAL V22] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[BIO-CHEMICAL V22] Ошибка чтения WAL: {e}")
            return False

    def process_biochemical_physics(self, val, spiral_points):
        # 1. Reaction-Diffusion (Уравнения Грея-Паркера / Тьюринга в 3D)
        Da, Db, f, k = 0.2, 0.1, 0.035, 0.065 # Коэффициенты морфогенеза
        laplacian_A = np.zeros_like(self.chem_A)
        laplacian_B = np.zeros_like(self.chem_B)

        for x in range(self.x_size):
            for y in range(self.y_size):
                for z in range(self.z_layers):
                    # Окрестность фон Неймана для диффузии
                    nb_sum_a = 0.0
                    nb_sum_b = 0.0
                    count = 0
                    for dx, dy, dz in [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]:
                        nx, ny, nz = x+dx, y+dy, z+dz
                        if 0 <= nx < self.x_size and 0 <= ny < self.y_size and 0 <= nz < self.z_layers:
                            nb_sum_a += self.chem_A[nx, ny, nz]
                            nb_sum_b += self.chem_B[nx, ny, nz]
                            count += 1
                    if count > 0:
                        laplacian_A[x, y, z] = (nb_sum_a / count) - self.chem_A[x, y, z]
                        laplacian_B[x, y, z] = (nb_sum_b / count) - self.chem_B[x, y, z]

        # Шаг интегрирования Reaction-Diffusion
        A = self.chem_A
        B = self.chem_B
        abb = A * (B ** 2)
        self.chem_A += (Da * laplacian_A - abb + f * (1.0 - A)) * 0.8
        self.chem_B += (Db * laplacian_B + abb - (f + k) * B) * 0.8
        self.chem_A = np.clip(self.chem_A, 0.0, 1.0)
        self.chem_B = np.clip(self.chem_B, 0.0, 1.0)

        for node in self.graph.nodes():
            self.graph.nodes[node]['is_spiral'] = False

        active_spiral_nodes = set()
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    active_spiral_nodes.add(node)
                    data['is_spiral'] = True
                    data['energy'] = min(100.0, data['energy'] + 40.0)
                    data['temperature'] += 8.0
                    self.chem_B[sx, sy, sz] = min(1.0, self.chem_B[sx, sy, sz] + 0.5)

        # 2. Термо-диффузия и Нейронная активность (Spiking / FitzHugh-Nagumo cущность)
        new_temps = {}
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            curr_temp = n_data['temperature']
            
            # Тепловая диффузия по соседям графа
            neighbors = list(self.graph.neighbors(node))
            if neighbors:
                diffused = curr_temp * 0.12
                curr_temp -= diffused
                share = diffused / len(neighbors)
                for n in neighbors:
                    new_temps[n] = new_temps.get(n, self.graph.nodes[n]['temperature']) + share
            new_temps[node] = new_temps.get(node, curr_temp)

            # Нейронная динамика: потенциал зависит от температуры и химического активатора B
            x_coord, y_coord, z_coord = n_data['xyzt'][:3]
            chem_val = self.chem_B[x_coord, y_coord, z_coord]
            
            # Возбуждение мембраны
            n_data['potential'] += (curr_temp * 0.2) + (chem_val * 5.0) - 2.0
            if n_data['potential'] > -30.0:  # Срабатывание спайка!
                n_data['spike'] = True
                n_data['potential'] = -80.0  # Реполяризация
                n_data['temperature'] += 5.0 # Спайк выделяет тепло
            else:
                n_data['spike'] = False
                n_data['potential'] = max(-90.0, n_data['potential'] - 1.5)

        for node, t in new_temps.items():
            self.graph.nodes[node]['temperature'] = min(100.0, max(20.0, t))

        # 3. Материальные потоки (Mass-Flow) по рёбрам графа
        for u, v, data in self.graph.edges(data=True):
            u_mass = self.graph.nodes[u]['mass']
            v_mass = self.graph.nodes[v]['mass']
            u_t = self.graph.nodes[u]['temperature']
            
            # Материал течет из зоны высокой концентрации в зону низкой по температурным магистралям
            mass_diff = u_mass - v_mass
            conductance = 0.1 + (u_t / 50.0)
            flow = mass_diff * conductance * 0.2
            
            if u_mass > flow and v_mass + flow >= 0:
                self.graph.nodes[u]['mass'] -= flow
                self.graph.nodes[v]['mass'] += flow
                data['flow_rate'] = abs(flow)

        # Метаболизм и Base-4 переходы
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            if n_data['energy'] > 10.0 and n_data['temperature'] < 95.0:
                n_data['energy'] -= 2.5
                n_data['temperature'] += 0.8
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                n_data['energy'] = max(5.0, n_data['energy'] - 1.5)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 3.0)

    def render_scientific_voxel_frame(self, cam_angle):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        # Научная палитра plasma для био-химического континуума
        colormap = plt.get_cmap('plasma')
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            
            # Цвет вокселя зависит от синергии температуры и химического ингибитора B
            temp = data['temperature']
            chem_b = self.chem_B[x, y, z]
            norm_val = min(1.0, max(0.0, ((temp - 20.0) / 80.0) * 0.6 + chem_b * 0.4))
            
            rgba = colormap(norm_val)
            hex_color = matplotlib.colors.rgb2hex(rgba[:3])
            color_array[x, y, z] = hex_color

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        elevation = 30 + 15 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Bio-Chemical V22 [Tick: {self.tick:03d}] (Plasma/Turing)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v22_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[BIO-CHEMICAL V22] Рендер био-химического кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files:
            return
        print("[BIO-CHEMICAL V22] Компиляция мастер-анимации био-континуума...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_biochemical_continuum.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[BIO-CHEMICAL V22] Мастер-анимация сохранена: {gif_name}")

        for f in self.frame_files:
            try:
                os.remove(f)
            except Exception:
                pass

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

            self.process_biochemical_physics(val, spiral_points)
            self.render_scientific_voxel_frame(self.tick * 0.4)

        self.compile_animation()

        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "mass": d["mass"],
            "potential": d["potential"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[BIO-CHEMICAL V22] Цикл завершен. Тактов: {self.tick}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshBioChemicalV22()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
