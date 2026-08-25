import matplotlib
matplotlib.use('Agg') # Автономный рендеринг для Termux / Android без GUI
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import json, os, math

class Base4Operator:
    MATRIX = [[0,2,3,1],[1,0,2,3],[2,3,1,0],[3,1,0,2]]
    @classmethod
    def apply(cls, cur, val, valenc):
        return (cls.MATRIX[cur%4][val%4] + valenc) % 4

class EngineV113D:
    def __init__(self, size=125, wal="malysh_v11_wal.log"): # 5x5x5 voxel grid
        self.size = size
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.initialize_networkx_continuum()

    def initialize_networkx_continuum(self):
        # 1. Построение полноценного графа через NetworkX
        dim = int(round(self.size ** (1/3))) # 5x5x5 куб = 125 узлов
        for i in range(self.size):
            x = i % dim
            y = (i // dim) % dim
            z = (i // (dim * dim)) % dim
            
            # Добавление узла с физическими параметрами
            self.graph.add_node(i, 
                xyzt=[x, y, z, 0],
                state=0,
                energy=100.0,
                temperature=25.0
            )

        # 2. Добавление взвешенных ребер (weighted edges) в граф
        for i in range(self.size):
            xi, yi, zi = self.graph.nodes[i]['xyzt'][:3]
            for j in range(i + 1, self.size):
                xj, yj, zj = self.graph.nodes[j]['xyzt'][:3]
                dist = abs(xi - xj) + abs(yi - yj) + abs(zi - zj)
                if dist == 1: # Связь только с ближайшими соседями (решетка)
                    weight = float(1.0 + (zi * 0.2))
                    self.graph.add_edge(i, j, weight=weight)

    def recover_from_wal(self):
        if not os.path.exists(self.wal_file):
            print(f"[ENGINE V11] WAL файл не найден. Холодный старт графа.")
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
            print(f"[ENGINE V11] Успешное восстановление графа из WAL с такта: {self.tick}")
            return True
        except Exception as e:
            print(f"[ENGINE V11] Ошибка восстановления WAL: {e}")
            return False

    def route_and_evolve_packets(self, val, attractor_node):
        # 3. Маршрутизация потоков (Pathfinding) и физика энергии
        for node in self.graph.nodes():
            n_data = self.graph.nodes[node]
            
            # Термодинамика и энергетический баланс
            if n_data['energy'] > 10.0 and n_data['temperature'] < 95.0:
                n_data['energy'] -= 3.5
                n_data['temperature'] += 1.8
                valenc = (n_data['xyzt'][2] + (self.tick % 4)) % 4
                n_data['state'] = Base4Operator.apply(n_data['state'], val, valenc)
            else:
                n_data['energy'] = min(100.0, n_data['energy'] + 30.0)
                n_data['temperature'] = max(20.0, n_data['temperature'] - 8.0)

        # Поиск путей данных (Pathfinding) к аттрактору через NetworkX
        active_packets = []
        for start_node in list(self.graph.nodes())[:15]:
            if start_node != attractor_node and nx.has_path(self.graph, start_node, attractor_node):
                try:
                    # Ищем путь с наименьшим весом (оптимальная маршрутизация)
                    path = nx.shortest_path(self.graph, source=start_node, target=attractor_node, weight='weight')
                    active_packets.append(path)
                    
                    # Динамическая перенастройка весов ребер (синаптическое обучение)
                    for idx in range(len(path) - 1):
                        u, v = path[idx], path[idx+1]
                        if self.graph.has_edge(u, v):
                            w = self.graph[u][v]['weight']
                            self.graph[u][v]['weight'] = max(0.2, w - 0.05) # Облегчаем пройденный путь
                except Exception:
                    pass
        return active_packets

    def render_3d_voxel_matplotlib(self, ax_coords):
        dim = 5
        voxel_array = np.zeros((dim, dim, dim), dtype=bool)
        color_array = np.empty((dim, dim, dim), dtype=object)
        
        # Заполнение воксельной матрицы по состоянию графа NetworkX
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            if 0 <= x < dim and 0 <= y < dim and 0 <= z < dim:
                voxel_array[x, y, z] = True
                if node == ax_coords:
                    color_array[x, y, z] = '#FF5733' # Фокус аттрактора (оранжевый)
                elif data['temperature'] > 75.0:
                    color_array[x, y, z] = '#C70039' # Перегрев (красный)
                elif data['energy'] > 70.0:
                    color_array[x, y, z] = '#28B463' # Высокая энергия (зеленый)
                else:
                    color_array[x, y, z] = '#5499C7' # Базовый поток (синий)

        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='k')
        ax.set_title(f"Engine V11 Omega 3D Voxel Continuum [Tick: {self.tick}]")
        ax.set_xlabel("X Axis")
        ax.set_ylabel("Y Axis")
        ax.set_zlabel("Z Axis")
        
        output_filename = "malysh_omega_v11_3d.png"
        plt.savefig(output_filename, dpi=150)
        plt.close(fig)
        print(f"[ENGINE V11] 3D Voxel-срез успешно отрендерен и сохранен в файл: {output_filename}")

    def run_continuum(self, stream):
        self.recover_from_wal()

        for val in stream:
            self.tick += 1
            
            # 4. Реальная логарифмическая спираль и фазовые переходы (Attractor Functions)
            angle = self.tick * 0.4
            radius = 0.6 * math.exp(0.09 * angle)
            ax_x = int(abs(radius * math.cos(angle)) * 3) % 5
            ax_y = int(abs(radius * math.sin(angle)) * 3) % 5
            ax_z = self.tick % 5
            
            # Находим ID узла-аттрактора по координатам спирали
            attractor_node = 0
            for node, data in self.graph.nodes(data=True):
                x, y, z = data['xyzt'][:3]
                if x == ax_x and y == ax_y and z == ax_z:
                    attractor_node = node
                    break

            # Выполнение физики и маршрутизации
            self.route_and_evolve_packets(val, attractor_node)

            # Рендеринг 3D вокселей каждые 3 такта
            if self.tick % 3 == 0:
                self.render_3d_voxel_matplotlib(attractor_node)

        # 5. Фиксация абсолютного состояния графа в WAL
        states = {str(n): {
            "state": d["state"], 
            "energy": d["energy"], 
            "temp": d["temperature"], 
            "xyzt": d["xyzt"]
        } for n, d in self.graph.nodes(data=True)}
        
        with open(self.wal_file, "a") as f:
            f.write(json.dumps({"tick": self.tick, "states": states}) + "\n")
        print(f"\n[ENGINE V11] Цикл завершен. Тактов: {self.ict if 'ict' in locals() else self.tick}. Состояние графа зафиксировано в WAL.")

if __name__ == "__main__":
    engine = EngineV113D()
    engine.run_continuum([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 2, 0, 3])
