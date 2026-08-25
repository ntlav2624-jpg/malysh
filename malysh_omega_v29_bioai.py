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

class MalyshBioComputerV29:
    def __init__(self, x_size=5, y_size=5, z_layers=3, wal="malysh_v29_wal.log"):
        self.x_size = x_size
        self.y_size = y_size
        self.z_layers = z_layers
        self.wal_file = wal
        self.graph = nx.Graph()
        self.tick = 0
        self.frame_files = []
        
        # Поля распределенных вычислений и генетических факторов
        self.gene_expression = np.zeros((x_size, y_size, z_layers), dtype=float)
        self.compute_load = np.zeros((x_size, y_size, z_layers), dtype=float)
        
        self.initialize_neuro_genomic_matrix()

    def initialize_neuro_genomic_matrix(self):
        node_id = 0
        for z in range(self.z_layers):
            for y in range(self.y_size):
                for x in range(self.x_size):
                    # Органоидная специализация
                    if z == 0:
                        organ = "CHEMICAL_ALU"      # Химический сопроцессор
                    elif z == 1:
                        organ = "NEURAL_CORTEX"     # Нейронная сеть с Hebbian/STDP
                    else:
                        organ = "PACEMAKER_HEART"   # Ритмический узел

                    # Генетический профиль узла (Base-4 кодоны)
                    dna_code = [np.random.randint(0, 4) for _ in range(4)]

                    self.graph.add_node(node_id, 
                        xyzt=[x, y, z, 0],
                        organ_type=organ,
                        dna=dna_code,
                        state=0,
                        energy=95.0,
                        potential=-70.0,
                        last_spike_tick=-10,
                        expression_level=0.5,
                        spike=False
                    )
                    node_id += 1

        # Создаем распределенную сеть синапсов
        nodes = list(self.graph.nodes())
        for i in range(len(nodes)):
            u = nodes[i]
            ux, uy, uz, _ = self.graph.nodes[u]['xyzt']
            for j in range(i + 1, len(nodes)):
                v = nodes[j]
                vx, vy, vz, _ = self.graph.nodes[v]['xyzt']
                if abs(ux - vx) + abs(uy - vy) + abs(uz - vz) <= 1:
                    # Начальный синаптический вес и пластичность (Hebbian)
                    self.graph.add_edge(u, v, weight=1.0, stdp_trace=0.0)

    def process_neuro_genomic_cycle(self, task_packet):
        self.tick += 1
        
        # 1. Генетические регуляторы: экспрессия генов зависит от нагрузки
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            dna_sum = sum(data['dna'])
            # Регуляция экспрессии через Base-4 кодоны и локальную энергию
            data['expression_level'] = (dna_sum / 12.0) * (data['energy'] / 100.0)
            self.gene_expression[x, y, z] = data['expression_level']

        # 2. Распределенные вычисления по органоидам и STDP обучение
        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            
            # Распределение задач
            task_token = task_packet[self.tick % len(task_packet)]
            valenc = (z + sum(data['dna'])) % 4
            
            # Вычисление состояния через Base-4 оператор
            data['state'] = Base4Operator.apply(data['state'], task_token, valenc)
            
            # Нейродинамика и потенциал
            if data['organ_type'] == "NEURAL_CORTEX":
                data['potential'] += (data['expression_level'] * 8.0) + (data['state'] * 2.0) - 3.0
                if data['potential'] > -30.0:
                    data['spike'] = True
                    data['last_spike_tick'] = self.tick
                    data['potential'] = -80.0
                    data['energy'] -= 3.0
                else:
                    data['spike'] = False
                    data['potential'] = max(-90.0, data['potential'] - 1.5)
            elif data['organ_type'] == "PACEMAKER_HEART":
                # Сердце синхронизирует ритм вычислений
                pulse = math.sin(self.tick * 0.7)
                data['energy'] = min(110.0, data['energy'] + pulse * 2.0)

            data['energy'] = max(10.0, data['energy'] - 0.8)

        # 3. STDP (Spike-Timing-Dependent Plasticity) синаптическое обучение
        for u, v, edata in self.graph.edges(data=True):
            if u in self.graph and v in self.graph:
                u_spike = self.graph.nodes[u]['spike']
                v_spike = self.graph.nodes[v]['spike']
                
                # Hebbian обучение: если оба сработали синхронно — усиливаем синапс
                if u_spike and v_spike:
                    edata['weight'] = min(5.0, edata['weight'] + 0.3)
                elif u_spike or v_spike:
                    # STDP временная коррекция
                    du = self.tick - self.graph.nodes[u]['last_spike_tick']
                    dv = self.tick - self.graph.nodes[v]['last_spike_tick']
                    if abs(du - dv) <= 1:
                        edata['weight'] = min(5.0, edata['weight'] + 0.15)
                    else:
                        edata['weight'] = max(0.1, edata['weight'] - 0.05)
                else:
                    # Медленное затухание неиспользуемых синапсов (синаптический прунинг)
                    edata['weight'] = max(0.1, edata['weight'] - 0.01)

    def render_bioai_frame(self):
        voxel_array = np.zeros((self.x_size, self.y_size, self.z_layers), dtype=bool)
        color_array = np.empty((self.x_size, self.y_size, self.z_layers), dtype=object)
        colormap = plt.get_cmap('viridis')

        for node, data in self.graph.nodes(data=True):
            x, y, z = data['xyzt'][:3]
            voxel_array[x, y, z] = True
            norm_val = min(1.0, data['expression_level'])
            color_array[x, y, z] = matplotlib.colors.rgb2hex(colormap(norm_val)[:3])

        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(projection='3d')
        ax.voxels(voxel_array, facecolors=color_array, edgecolor='black')
        
        ax.view_init(elev=30, azim=self.tick * 25)
        ax.set_title(f"Neuro-Genomic AI V29 [Tick: {self.tick:02d}]")
        
        filename = f"v29_frame_{self.tick:02d}.png"
        plt.savefig(filename, dpi=110)
        plt.close(fig)
        self.frame_files.append(filename)
        print(f"[NEURO-GENOMIC] Рендер кадра обучения: {filename}")

    def compile_animation(self):
        if not self.frame_files: return
        images = [Image.open(f) for f in self.frame_files]
        gif_name = "malysh_neuro_genomic_ai.gif"
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=350, loop=0)
        print(f"[NEURO-GENOMIC] Мастер-анимация обучения сохранена: {gif_name}")
        for f in self.frame_files:
            try: os.remove(f)
            except Exception: pass

    def run(self, task_stream):
        for val in task_stream:
            self.process_neuro_genomic_cycle(task_stream)
            self.render_bioai_frame()
        self.compile_animation()
        print(f"\n[NEURO-GENOMIC] Цикл обучения завершен. Тактов: {self.tick}. Синапсов обучено: {len(self.graph.edges())}")

if __name__ == "__main__":
    engine = MalyshBioComputerV29()
    engine.run([0, 3, 2, 1, 3, 2, 0, 1, 3, 2, 3, 1, 0, 2])
