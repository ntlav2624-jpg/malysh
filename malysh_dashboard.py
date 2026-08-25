import os
import time
import json

HOME_DIR = os.path.expanduser("~")
STREAM_FILE = os.path.join(HOME_DIR, "malysh_telemetry_stream.json")

def main():
    print("[*] Запуск дашборда телеметрии Малыша...")
    time.sleep(1.0)
    while True:
        try:
            if os.path.exists(STREAM_FILE):
                with open(STREAM_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Очистка экрана для динамического обновления
                os.system("clear" if os.name == "posix" else "cls")
                
                print("\033[35m========================================")
                print("      MALYSH HIVE TELEMETRY DASHBOARD    ")
                print("========================================\033[0m")
                print(f" 🌀 Цикл контура:    C{data.get('cycle', 0):03d}")
                print(f" 🧬 Поколение роя:   Gen {data.get('generation', 1)}")
                print(f" ⚡ Индекс симбиоза: {data.get('symbiosis_index', 0.0)}")
                print(f" 🌌 Кватерн. режим:  {data.get('quaternary_state', 'Q3')}")
                print(f" ⏱  Метка времени:   {data.get('timestamp', '-')}")
                print("\033[35m========================================\033[0m")
                print(" [Статус]: Рой стабилен, поток активен.")
                print(" Нажми Ctrl + C для выхода из дашборда.")
            else:
                print("[!] Ожидание файла телеметрии...")
            
            time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[!] Дашборд отключен.")
            break

if __name__ == "__main__":
    main()
