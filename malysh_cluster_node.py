import os
import socket
import threading
import json
import time
import numpy as np

class NexusNode:
    """Узел распределенной сети Малыша, способный обмениваться данными с другими нодами."""
    def __init__(self, node_id: int, port: int, peer_ports: list):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports
        self.memory = {}
        self.is_running = True

    def start_server(self):
        """Запуск серверного потока для приема данных от других нод кластера."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", self.port))
        server.listen(5)
        
        while self.is_running:
            try:
                client, _ = server.accept()
                data = client.recv(4096).decode("utf-8")
                if data:
                    packet = json.loads(data)
                    self.handle_incoming_packet(packet)
                client.close()
            except:
                break

    def handle_incoming_packet(self, packet: dict):
        """Обработка распределенного пакета знаний от соседнего узла."""
        sender_id = packet.get("node_id")
        concept = packet.get("concept")
        print(f"\n[NODE {self.node_id}] Получен пакет от Node {sender_id}: концепт '{concept}'")
        self.memory[concept] = packet.get("vector")

    def broadcast_thought(self, concept: str, vector: list):
        """Рассылка состояния (синхронизация векторов) по всем узлам кластера."""
        packet = json.dumps({
            "node_id": self.node_id,
            "concept": concept,
            "vector": vector
        })
        for p_port in self.peer_ports:
            if p_port != self.port:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(("127.0.0.1", p_port))
                    s.sendall(packet.encode("utf-8"))
                    s.close()
                except:
                    pass

    def run_node_loop(self):
        print(f"[INIT] Кластерный узел №{self.node_id} запущен на порту {self.port}")
        server_thread = threading.Thread(target=self.start_server, daemon=True)
        server_thread.start()

        for step in range(1, 4):
            time.sleep(3)
            # Генерация локального когнитивного вектора
            local_vector = np.random.uniform(0.0, 1.0, size=(4,)).tolist()
            concept_name = f"cluster_state_n{self.node_id}_step{step}"
            
            self.memory[concept_name] = local_vector
            print(f"[NODE {self.node_id}] Синтезирован вектор на шаге {step}. Синхронизация с кластером...")
            
            # Рассылка данных соседям
            self.broadcast_thought(concept_name, local_vector)

        self.is_running = False

# Запуск локального микро-кластера из трех связанных нод в разных потоках
def deploy_local_cluster():
    ports = [9001, 9002, 9003]
    nodes = []

    for i, port in enumerate(ports, start=1):
        node = NexusNode(node_id=i, port=port, peer_ports=ports)
        nodes.append(node)
        t = threading.Thread(target=node.run_node_loop, daemon=True)
        t.start()

    time.sleep(10)
    print("\n[COMPLETE] Сетевой кластер завершил сессию обмена распределенными данными.")

if __name__ == "__main__":
    deploy_local_cluster()
