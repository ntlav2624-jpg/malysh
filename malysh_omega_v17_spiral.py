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

class MalyshSpiralEngineV17:
    def __init__(self, x_size=4, y_size=4, z_layers=3, wal="malysh_v17_wal.log"):
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
                        energy=50.0, # Начальный базовый заряд
                        temperature=25.0
                    )
                    layer_nodes.append(node_id)
                    node_id += 1
            self.layers[z] = layer_nodes

        # Взвешенные ребра с межслойными мостами
        for u in self.graph.nodes():
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for v in self.graph.nodes():
                if u < v:
                    vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                    dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                    if dist <= 1 or (dist == 2 and uz != vz):
                        weight = float(1.0 + (uz * 0.25))
                        self.graph.add_edge(u, v, weight=weight, traffic=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[SPIRAL ENGINE V17] Холодный старт спирального континуума.")
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
            print(f"[SPIRAL ENGINE V17] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[SPIRAL ENGINE V17] Ошибка чтения WAL: {e}")
            return False

    def process_spiral_physics_and_routing(self, val, attractor_node, spiral_coords):
        ax_x, ax_y, ax_z = spiral_coords

        # 2. Спираль как источник энергии (инжекция в узлы вблизи фронта спирали)
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            nx_x, nx_y, nx_z = n_data['xyzt'][:3]
            
            # Расстояние до текущего фокуса логарифмической спирали
            distance_to_spiral = abs(nx_x - ax_x) + abs(nx_y - ax_y) + abs(nx_z - ax_z)
            
            if distance_to_spiral == 0:
                # Прямое попадание в эпицентр спирального витка — колоссальная подпитка энергией!
                n_data['energy'] = min(100.0, n_data['energy'] + 45.0)
                n_data['temperature'] += 3.0
            elif distance_to_spiral == 1:
                # Периферийная инжекция поля
                n_data['energy'] = min(100.0, n_data['energy'] + 20.0)
            
            # Стандартный метаболизм и переходы состояний Base-4
            if n_data['energy'] > 12.0 and n_data['temperature'] < 95.0:
                n_data['energy'] -= 4.0
                n_data['temperature'] += 1.6
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                n_data['energy'] = max(5.0, n_data['energy'] - 2.0)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 6.0)

        # 3. Маршрутизация потоков (Dijkstra / shortest_path + BFS + веса)
        for z in range(self.z_layers):
            sub_nodes = self.layers[z]
            if attractor_node in sub_nodes and len(sub_nodes) > 1:
                sub_g = self.graph.subgraph(sub_nodes)
                sources = [n for n in sub_nodes if n != attractor_node]
                if sources:
                    src = sources[self.tick % len(sources)]
                    try:
                        if nx.has_path(sub_g, src, attractor_node):
                            path = nx.shortest_path(sub_g, source=src, target=attractor_node, weight='weight')
                            for i in range(len(path) - 1):
                                u, v = path[i], path[i+1]
                                if self.graph.has_edge(u, v):
                                    self.graph[u][v]['weight'] = max(0.1, self.graph[u][v]['weight'] - 0.06)
                                    self.graph[u][v]['traffic'] += 1.0
                        
                        for u, v in list(nx.bfs_edges(sub_g, source=src))[:2]:
                            if self.graph.has_edge(u, v):
                                self.graph[u][v]['weight'] = max(0.1, self.graph[u][v]['weight'] - 0.02)
                    except Exception:
                        pass

    def render_dynamic_voxel_frame(self, attractor_node, cam_angle):
        # 4. Динамический 3D voxel-рендер с камерой на спирали
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            if node == attractor_node:
                color_array[x, y, z] = '#FF5733' # Эпицентр спирального генератора
            elif data['temperature'] > 80.0:
                color_array[x, y, z] = '#900C3F' # Перегрев узла
            elif data['energy'] > 75.0:
                color_array[x, y, z] = '#28B463' # Высокий заряд энергии
            else:
                color_array[x, y, z] = '#2980B9' # Базовый контур

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        # 5. Спираль как траектория камеры (динамический ракурс обзора)
        # Угол камеры следует за логарифмической спиралью с плавным наклоном
        elevation = 30 + 15 * math.sin(cam_angle * 0.5)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Spiral Engine V17 [Tick: {self.tick:03d}] \nCam(elev={elevation:.1f}, azim={azimuth:.1f})")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v17_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[SPIRAL V17] Рендер кадра с ракурсом камеры: {filename}")

    def compile_spiral_animation(self):
        if not self.frame_files:
            return
        print("[SPIRAL ENGINE V17] Компиляция кадров в спиральный GIF-континуум...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_spiral_continuum.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=320,
            loop=0
        )
        print(f"[SPIRAL ENGINE V17] Анимация успешно сохранена: {gif_name}")

        for f in self.frame_files:
            try:
                os.remove(f)
            except Exception:
                pass

    def run_engine(self, stream):
        self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # Математика реальной логарифмической спирали
            spiral_angle = self.tick * 0.45
            radius = 0.35 * math.exp(0.08 * spiral_angle)
            
            ax_x = int(abs(radius * math.cos(spiral_angle)) * 2) % self.x_size
            ax_y = int(abs(radius * math.sin(spiral_angle)) * 2) % self.y_size
            ax_z = self.tick % self.z_layers
            
            attractor_node = 0
            for node, data in self.graph.nodes(data=True):
                x, y, z = data['xyzt'][:3]
                if x == ax_x and y == ax_y and z == ax_z:
                    attractor_node = node
                    break

            # Выполнение физики, спиральной инжекции энергии и роутинга
            self.process_spiral_physics_and_routing(val, attractor_node, (ax_x, ax_y, ax_z))
            
            # Рендер с камерой, привязанной к спирали
            self.render_dynamic_voxel_frame(attractor_node, spiral_angle)

        self.compile_spiral_animation()

        # Синхронизация WAL
        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "xyzt": d["xyzt"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[SPIRAL ENGINE V17] Цикл завершен. Тактов: {self.tick}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshSpiralEngineV17()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2, 3, 1])
