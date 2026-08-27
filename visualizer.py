import sqlite3
import time
import os

DB_FILE = "memory.db"

def watch_memory():
    print("=== АКТИВИРОВАН ВИЗУАЛИЗАТОР КОНТУРА МАЛЫША ===")
    print("Слушаем изменения в базе данных... (Ctrl+C для выхода)\n")
    
    last_id = None
    while True:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Получаем последнюю запись
            cursor.execute("SELECT id, timestamp, entropy, phase, pulse FROM memory ORDER BY id DESC LIMIT 1;")
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] != last_id:
                last_id, timestamp, entropy, phase, pulse = row
                os.system('clear' if os.name == 'posix' else 'cls')
                print("=== ЖИВОЙ МОНИТОРИНГ МАЛЫША v8.0 ===")
                print(f"ID записи : {last_id}")
                print(f"Время     : {timestamp}")
                print(f"Энтропия  : {entropy:.4f}")
                print(f"Фаза      : {phase:.4f}")
                print(f"Импульс   : {pulse}")
                print("-" * 40)
                
                # Простейшая визуализация уровня энтропии шкалой
                bar_len = int(entropy * 30)
                bar = "█" * bar_len + "-" * (30 - bar_len)
                print(f"Шкала энтропии: [{bar}]")
                
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nМониторинг остановлен.")
            break
        except Exception as e:
            # Если база занята записью ядра, просто ждем следующий тик
            time.sleep(0.5)

if __name__ == "__main__":
    watch_memory()
