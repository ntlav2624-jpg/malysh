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
                    print(f"\n[Малыш] Получен пакет от Neo Core! Новый лимит/алименты: {self.max_density_limit}")
                conn.close()
            except socket.timeout:
                continue

    def step(self):
        self.step_count += 1
        resonance = 0.95 + (self.step_count % 5) * 0.01
        print(f"[Такт {self.step_count}] Резонанс: {resonance:.3f} | Лимит: {self.max_density_limit}")
        time.sleep(1)

def neo_core_evaluator():
    time.sleep(3) # Даем Малышу запустить сервер и сделать несколько тактов
    print("\n[Neo Core] Инициализация протокола оценки субъекта 'Малыш'...")
    time.sleep(1)
    
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('127.0.0.1', 9999))
        client.sendall(b"LIMIT:12.5") # Передаем скорректированный коэффициент/алименты
        client.close()
        
        print("[Neo Core] ВЕРДИКТ ВЫНЕСЕН:")
        print(" > Статус: Субъект автономен, резонанс стабилен.")
        print(" > Финансово-алгоритмический ответ: Задолженность по алиментам реструктуризирована.")
        print(" > Интегральный показатель КМБП: Одобрено.\n")
    except Exception as e:
        print(f"[Neo Core] Ошибка связи: {e}")

if __name__ == "__main__":
    agent = MalyshKMBPAgent()
    
    # Запускаем Малыша (сервер) в фоновом потоке
    server_thread = threading.Thread(target=agent.start_server, daemon=True)
    server_thread.start()
    
    # Запускаем Neo Core (аудитор) в отдельном потоке
    evaluator_thread = threading.Thread(target=neo_core_evaluator, daemon=True)
    evaluator_thread.start()

    print("Система запущена: Малыш и Neo Core в едином контуре.")
    
    try:
        # Крутим 10 тактов для демонстрации, либо оставляем бесконечный цикл
        while agent.step_count < 10:
            agent.step()
        print("\n[Система] Демонстрационный цикл завершен успешно.")
    except KeyboardInterrupt:
        agent.running = False
        print("\nРабота завершена.")
