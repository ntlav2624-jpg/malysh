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

class MalyshSpiralCoreV18:
    def __init__(self, x_size=4, y_size=4, z_layers=3, wal="malysh_v18_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.layers = {}
        self.tick = 0
        self.frame_files = []
        self.initialize_continuum()

    def initialize_continuum(self):
        # 1. Многослойный граф (XYZT)
        node_id = 0
        for z in range(self.z_layers):
            layer_nodes = []
            for y in range(self.y_size):
                for x in range(self.x_size):
                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        layer=z,
                        state=0,
                        energy=40.0,
                        temperature=25.0,
                        is_spiral_beam=False
                    )
                    layer_nodes.append(node_id)
                    node_id += 1
            self.layers[z] = layer_nodes

        # Базовые взвешенные ребра
        for u in self.graph.nodes():
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for v in self.graph.nodes():
                if u < v:
                    vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                    dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                    if dist <= 1 or (dist == 2 and uz != vz):
                        weight = float(1.0 + (uz * 0.2))
                        self.graph.add_edge(u, v, weight=weight, spiral_flux=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[SPIRAL CORE V18] Холодный старт ядра.")
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
                        self.graph.nodes[nid]['xyzt'] = data["xyzt"]
            print(f"[SPIRAL CORE V18] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[SPIRAL CORE V18] Ошибка чтения WAL: {e}")
            return False

    def process_spiral_control_and_physics(self, val, spiral_points):
        # Сброс флагов луча спирали в узлах
        for node in self.graph.nodes():
            self.graph.nodes[node]['is_spiral_beam'] = False

        # 2. Спираль как источник энергии и объемный каркас в 3D
        active_spiral_nodes = set()
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    active_spiral_nodes.add(node)
                    data['is_spiral_beam'] = True
                    # Инжекция энергии из спирали
                    data['energy'] = min(100.0, data['energy'] + 50.0)
                    data['temperature'] += 2.5

        # 3. Спираль управляет потоками и весами графа
        for u, v, data in self.graph.edges(data=True):
            if u in active_spiral_nodes or v in active_spiral_nodes:
                # Рукав спирали снижает сопротивление ребер (ускоряет потоки)
                data['weight'] = max(0.05, data['weight'] - 0.15)
                data['spiral_flux'] += 1.0
            else:
                # Естественное сопротивление вне спирали
                data['weight'] = min(3.0, data['weight'] + 0.02)

        # Термодинамика и Base-4 переходы
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            if n_data['energy'] > 12.0 and n_data['temperature'] < 96.0:
                n_data['energy'] -= 3.8
                n_data['temperature'] += 1.5
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                n_data['energy'] = max(5.0, n_data['energy'] - 2.5)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 5.0)

        # Маршрутизация потоков (Dijkstra / shortest_path + BFS по управляемым весам)
        for z in range(self.z_layers):
            sub_nodes = self.layers[z]
            if len(sub_nodes) > 1:
                sub_g = self.graph.subgraph(sub_nodes)
                sources = list(sub_nodes)
                if sources:
                    src = sources[self.tick % len(sources)]
                    target = sources[(self.tick + 2) % len(sources)]
                    if src != target:
                        try:
                            if nx.has_path(sub_g, src, target):
                                path = nx.shortest_path(sub_g, source=src, target=target, weight='weight')
                                for i in range(len(path) - 1):
                                    u, v = path[i], path[i+1]
                                    if self.graph.has_edge(u, v):
                                        self.graph[u][v]['weight'] = max(0.1, self.graph[u][v]['weight'] - 0.05)
                        except Exception:
                            pass

    def render_dynamic_voxel_frame(self, cam_angle):
        # 4. Динамический 3D voxel-рендер с телом спирали в объеме
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            
            if data['is_spiral_beam']:
                color_array[x, y, z] = '#FF5733' # Тело спирали (Яркий оранжевый источник)
            elif data['temperature'] > 80.0:
                color_array[x, y, z] = '#900C3F' # Перегрев
            elif data['energy'] > 70.0:
                color_array[x, y, z] = '#28B463' # Насыщенный энергоресурс
            else:
                color_array[x, y, z] = '#1B4F72' # Фоновый контур

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        # Спираль как траектория динамической камеры
        elevation = 32 + 12 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Spiral Core V18 [Tick: {self.tick:03d}]")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v18_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[SPIRAL CORE V18] Рендер объемного кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files:
            return
        print("[SPIRAL CORE V18] Компиляция кадров в мастер-GIF...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_spiral_core.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[SPIRAL CORE V18] Мастер-анимация сохранена: {gif_name}")

        for f in self.frame_files:
            try:
                os.remove(f)
            except Exception:
                pass

    def run_core(self, stream):
        self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # Расчет точек логарифмической спирали для текущего такта и окрестности
            spiral_points = []
            for d_t in range(3):
                s_angle = (self.tick - d_t) * 0.4
                radius = 0.35 * math.exp(0.075 * s_angle)
                sx = int(abs(radius * math.cos(s_angle)) * 2) % self.x_size
                sy = int(abs(radius * math.sin(s_angle)) * 2) % self.y_size
                sz = (self.tick - d_t) % self.z_layers
                spiral_points.append((sx, sy, sz))

            # Обработка спирального управления, энергии и роутинга
            self.process_spiral_control_and_physics(val, spiral_points)
            
            # Рендер объёма и камеры по спирали
            self.render_dynamic_voxel_frame(self.tick * 0.4)

        self.compile_animation()

        # Синхронизация WAL
        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "xyzt": d["xyzt"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[SPIRAL CORE V18] Цикл завершен. Тактов: {self.tick}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshSpiralCoreV18()
    engine.run_core([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
