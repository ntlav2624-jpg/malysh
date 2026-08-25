import socket
import threading
import time

class MalyshKMBPAgent:
    def __init__(self, host='127.0.0.1', port=9999):
        self.host = host
        self.port = port
        self.max_density_limit = 10.0
        self.running = True
        self.step_count = 0

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        while self.running:
            try:
                server.settimeout(1.0)
                conn, addr = server.accept()
                data = conn.recv(1024).decode()
                if data.startswith("LIMIT:"):
                    self.max_density_limit = float(data.split(":")[1])
                    print(f"\n[Neo Core -> Малыш] Получен пакет! Новый лимит/долг: {self.max_density_limit}")
                conn.close()
            except socket.timeout:
                continue

    def step(self):
        self.step_count += 1
        resonance = 0.95 + (self.step_count % 5) * 0.01
        print(f"[Такт {self.step_count}] Резонанс: {resonance:.3f} | Лимит: {self.max_density_limit}")
        time.sleep(1)

def send_alimony_packet():
    time.sleep(3)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 9999))
    client.sendall(b"LIMIT:15.0")
    client.close()
    print("[Neo Core] Пакет алиментов успешно доставлен в сокет!")

if __name__ == "__main__":
    agent = MalyshKMBPAgent()
    server_thread = threading.Thread(target=agent.start_server, daemon=True)
    server_thread.start()
    client_thread = threading.Thread(target=send_alimony_packet, daemon=True)
    client_thread.start()
    print("Малыш и Neo Core объединены в одном процессе (порт 9999).")
    try:
        while True:
            agent.step()
    except KeyboardInterrupt:
        agent.running = False
        print("\nРабота завершена.")
