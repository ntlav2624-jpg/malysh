import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, math

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class EngineV12MultiLayer:
    def __init__(self, x_size=4, y_size=4, z_layers=3, wal="malysh_v12_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.size = x_size * y_size * z_layers
        self.wal_file = wal
        
        # Многослойный граф NetworkX
        self.graph = nx.Graph()
        self.tick = 0
        self.initialize_multilayer_continuum()

    def initialize_multilayer_continuum(self):
        node_id = 0
        # 1. Создание узлов по слоям (XYZT архитектура)
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        layer=z,
                        state=0,
                        energy=100.0,
                        temperature=25.0
                    )
                    node_id += 1

        # 2. Построение внутрислойных и межслойных связей (Weighted Edges)
        for u in self.graph.nodes():
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for v in self.graph.nodes():
                if u < v:
                    vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                    dist = abs(ux - vx) + abs(uy - vy) + abs(uz - vz)
                    
                    if dist == 1: # Ближайшие соседи внутри слоя или между слоями
                        weight = float(1.0 + (uz * 0.3))
                        self.graph.add_edge(u, v, weight=weight)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[ENGINE V12] WAL файл не найден. Холодный старт многослойного графа.")
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
            print(f"[ENGINE V12] Успешное восстановление из WAL с такта: {self.tick}")
            return True
        except Exception as e:
            print(f"[ENGINE V12] Ошибка восстановления WAL: {e}")
            return False

    def route_packets_and_physics(self, val, attractor_node):
        # 3. Физика энергии и состояний узлов
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            if n_data['energy'] > 8.0 and n_data['temperature'] < 96.0:
                n_data['energy'] -= 4.0
                n_data['temperature'] += 2.0
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                n_data['energy'] = min(100.0, n_data['energy'] + 35.0)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 10.0)

        # 4. Маршрутизация потоков (Pathfinding через shortest_path и weighted edges)
        active_sources = [n for n in list(self.graph.nodes())[:6] if n != attractor_node]
        for src in active_sources:
            if nx.has_path(self.graph, src, attractor_node):
                try:
                    path = nx.shortest_path(self.graph, source=src, target=attractor_node, weight='weight')
                    # Обучение весов графа на основе пройденного пути
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i+1]
                        if self.graph.has_edge(u, v):
                            w = self.graph[u][v]['weight']
                            self.graph[u][v]['weight'] = max(0.1, w - 0.08) # Оптимизация канала
                except Exception:
                    pass

    def render_dynamic_voxel_frame(self, attractor_node):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            if node == attractor_node:
                color_array[x, y, z] = '#FF5733' # Фокус логарифмической спирали (Оранжевый)
            elif data['temperature'] > 80.0:
                color_array[x, y, z] = '#C70039' # Перегрев (Красный)
            elif data['energy'] > 75.0:
                color_array[x, y, z] = '#28B463' # Высокая энергия (Зеленый)
            else:
                color_array[x, y, z] = '#3498DB' # Базовый контур (Синий)

        fig = plt.figure(figsize=(7, 7))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='gray')
        ax.set_title(f"XYZT Continuum [Tick: {self.tick:03d}]")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z-Layer")
        
        # Динамическое имя файла для сборки анимации
        filename = f"frame_{self.tick:03d}.png"
        plt.savefig(filename, dpi=120)
        plt.close(fig)
        print(f"[ENGINE V12] Рендер кадра: {filename}")

    def run_continuum(self, stream):
        self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # 5. Реальная логарифмическая спираль (Logarithmic Spiral Dynamics)
            angle = self.tick * 0.45
            radius = 0.5 * math.exp(0.08 * angle)
            ax_x = int(abs(radius * math.cos(angle)) * 2) % self.x_size
            ax_y = int(abs(radius * math.sin(angle)) * 2) % self.y_size
            ax_z = self.tick % self.z_layers
            
            # Поиск узла аттрактора по координатам спирали
            attractor_node = 0
            for node, data in self.graph.nodes(data=True):
                x, y, z = data['xyzt'][:3]
                if x == ax_x and y == ax_y and z == ax_z:
                    attractor_node = node
                    break

            # Выполнение физики и роутинга
            self.route_packets_and_physics(val, attractor_node)

            # Генерация кадра для анимации каждый такт
            self.render_dynamic_voxel_frame(attractor_node)

        # Сохранение состояния в WAL
        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "xyzt": d["xyzt"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V12] Серия циклов завершена. Тактов: {self.tick}. WAL обновлен.")

if __name__ == "__main__":
    engine = EngineV12MultiLayer()
    # Запуск потока из 10 тактов для генерации секвенции кадров
    engine.run_continuum([0, 3, 2, 1, 3, 2, 0, 1, 3, 2])
