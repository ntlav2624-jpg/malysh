import time
import subprocess
from pathlib import Path

class MalyshProactiveDaemon:
    def __init__(self, check_interval_seconds=3600):
        self.interval = check_interval_seconds
        self.home_dir = Path("/data/data/com.termux/files/home")

    def gather_system_metrics(self) -> str:
        try:
            df = subprocess.run(['df', '-h', '/data'], capture_output=True, text=True).stdout.strip()
            ps = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
            py_processes = [line for line in ps.split('\n') if 'python' in line]
            
            summary = (
                f"Среда: Termux Android\n"
                f"Активных python-процессов: {len(py_processes)}\n"
                f"Состояние диска:\n{df}"
            )
            return summary
        except Exception as e:
            return f"Ошибка сбора метрик: {str(e)}"

    def simulate_proactive_thought(self):
        state = self.gather_system_metrics()
        print(f"\n[~] {time.strftime('%Y-%m-%d %H:%M:%S')} | Цикл самоанализа Малыша:")
        print(f"--- Сводка состояния ---\n{state}\n------------------------")
        print("[+] Запрос вектора развития сформирован. Ожидание настройки API на новом устройстве.")

    def run(self):
        print("[✓] Проактивный эволюционный демон Малыша запущен в Termux.")
        try:
            while True:
                self.simulate_proactive_thought()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n[!] Демон остановлен пользователем.")

if __name__ == "__main__":
    daemon = MalyshProactiveDaemon(check_interval_seconds=10)
    daemon.run()
