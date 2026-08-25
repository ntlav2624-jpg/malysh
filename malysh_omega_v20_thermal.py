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

class MalyshThermalFieldV20:
    def __init__(self, x_size=4, y_size=4, z_layers=3, wal="malysh_v20_wal.log"):
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
                        temperature=25.0, # Базовая температура
                        is_spiral_source=False
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
                        weight = float(1.0 + (uz * 0.2))
                        self.graph.add_edge(u, v, weight=weight, thermal_flow=0.0)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[THERMAL V20] Холодный старт теплового континуума.")
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
            print(f"[THERMAL V20] Восстановление из WAL на такте: {self.tick}")
            return True
        except Exception as e:
            print(f"[THERMAL V20] Ошибка чтения WAL: {e}")
            return False

    def process_thermal_field_and_routing(self, val, spiral_points):
        for node in self.graph.nodes():
            self.graph.nodes[node]['is_spiral_source'] = False

        active_spiral_nodes = set()
        for sx, sy, sz in spiral_points:
            for node, data in self.graph.nodes(data=True):
                nx_x, nx_y, nx_z = data['xyzt'][:3]
                if nx_x == sx and nx_y == sy and nx_z == sz:
                    active_spiral_nodes.add(node)
                    data['is_spiral_source'] = True
                    data['energy'] = min(100.0, data['energy'] + 50.0)
                    data['temperature'] += 8.0 # Интенсивный разогрев в эпицентре спирали

        # 1. Тепловая диффузия: передача тепла соседям по графу
        new_temps = {}
        for node in self.graph.nodes():
            curr_temp = self.graph.nodes[node]['temperature']
            neighbors = list(self.graph.neighbors(node))
            if neighbors:
                # Диффузия части тепла в сторону соседей
                diffused_heat = curr_temp * 0.08
                curr_temp -= diffused_heat
                share = diffused_heat / len(neighbors)
                for n in neighbors:
                    new_temps[n] = new_temps.get(n, self.graph.nodes[n]['temperature']) + share
            new_temps[node] = new_temps.get(node, curr_temp)

        for node, t in new_temps.items():
            self.graph.nodes[node]['temperature'] = min(100.0, max(20.0, t))

        # 2. Термо-поле влияет на потоки графа (высокая температура увеличивает вес/сопротивление ребер)
        for u, v, data in self.graph.edges(data=True):
            u_temp = self.graph.nodes[u]['temperature']
            v_temp = self.graph.nodes[v]['temperature']
            avg_temp = (u_temp + v_temp) / 2.0
            
            if u in active_spiral_nodes or v in active_spiral_nodes:
                data['weight'] = max(0.05, data['weight'] - 0.1) # Рукав спирали пробивает сопротивление
            else:
                # Термическое сопротивление: горячие ребра замедляют потоки
                thermal_penalty = (avg_temp / 100.0) * 0.3
                data['weight'] = min(4.0, 1.0 + thermal_penalty)

        # Метаболизм узлов и Base-4 переходы
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            if n_data['energy'] > 10.0 and n_data['temperature'] < 98.0:
                n_data['energy'] -= 3.2
                n_data['temperature'] += 1.2
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                # Естественное охлаждение среды
                n_data['energy'] = max(5.0, n_data['energy'] - 2.0)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 4.5)

        # Маршрутизация через термически-модифицированный граф
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
                                        self.graph[u][v]['thermal_flow'] += 1.0
                        except Exception:
                            pass

    def render_dynamic_voxel_frame(self, cam_angle):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        # 3. Термо-объем цветным (True Heatmap на основе температуры узла)
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            temp = data['temperature']
            
            # Генерация Heatmap RGB по шкале температуры (от холода к пламени)
            norm_t = min(1.0, max(0.0, (temp - 20.0) / 80.0))
            if norm_t < 0.33:
                # Холодная зона (Синий -> Голубой)
                color_array[x, y, z] = '#2980B9'
            elif norm_t < 0.66:
                # Умеренная зона (Зеленый -> Желтый)
                color_array[x, y, z] = '#F1C40F'
            elif norm_t < 0.9:
                # Горячая зона (Оранжевый)
                color_array[x, y, z] = '#E67E22'
            else:
                # Зона плазменного перегрева (Красный / Бордовый)
                color_array[x, y, z] = '#900C3F'

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        # Камера следует по логарифмической спирали
        elevation = 32 + 12 * math.sin(cam_angle * 0.4)
        azimuth = math.degrees(cam_angle) % 360
        ax.view_init(elev=elevation, azim=azimuth)

        ax.set_title(f"Thermal Field V20 [Tick: {self.tick:03d}] (Heatmap)")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        filename = f"v20_frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[THERMAL V20] Рендер heatmap-кадра: {filename}")

    def compile_animation(self):
        if not self.frame_files:
            return
        print("[THERMAL V20] Компиляция теплового GIF-континуума...")
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_thermal_field.gif"
        images[0].save(
            gif_name,
            save_all=True,
            append_images=images[1:],
            duration=300,
            loop=0
        )
        print(f"[THERMAL V20] Heatmap-анимация сохранена: {gif_name}")

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

            self.process_thermal_field_and_routing(val, spiral_points)
            self.render_dynamic_voxel_frame(self.tick * 0.4)

        self.compile_animation()

        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "xyzt": d["xyzt"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[THERMAL V20] Цикл завершен. Тактов: {self.tick}. WAL синхронизирован.")

if __name__ == "__main__":
    engine = MalyshThermalFieldV20()
    engine.run_engine([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
