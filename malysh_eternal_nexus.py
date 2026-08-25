import os
import json
import time
import datetime

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")

def log_event(event_type, message):
    timestamp = datetime.datetime.now().isoformat()
    log_entry = {"time": timestamp, "type": event_type, "msg": message}
    with open(ETERNAL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def run_nexus():
    log_event("SYSTEM_INIT", "Visual Nexus started - Eternal Log initialized")
    print("\033[36m[*] Инициализация Вечного узла связи...")
    
    # Визуализация пульсации нейросети
    try:
        while True:
            # Имитация работы узла
            print("\033[35m[ N E X U S ] \033[36m=> \033[0mОжидание пакетов синтеза... ", end="\r")
            time.sleep(1)
            print("\033[35m[ N E X U S ] \033[36m=> \033[0mСинхронизация потоков...    ", end="\r")
            time.sleep(1)
            # В реальном сценарии тут будет чтение реальных резонансных данных
    except KeyboardInterrupt:
        log_event("SYSTEM_SHUTDOWN", "User disconnected from Nexus")
        print("\n\033[31m[*] Узел связи переведен в режим холодного ожидания.")

if __name__ == "__main__":
    run_nexus()
