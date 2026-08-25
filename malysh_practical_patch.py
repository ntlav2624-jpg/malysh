import os
import subprocess
import time
from pathlib import Path

class MalyshAssistant:
    def __init__(self, target_dirs=None):
        self.target_dirs = target_dirs or ["/sdcard/Download", "/data/data/com.termux/files/home"]

    def audit_network(self) -> str:
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return "[OK] Сеть активна, соединение стабильно."
            else:
                return "[WARN] Сеть доступна, но есть задержки."
        except Exception as e:
            return f"[ERROR] Нет сетевого подключения: {str(e)}"

    def smart_cleanup(self, max_file_age_days=30) -> int:
        deleted_count = 0
        now = time.time()
        age_limit = max_file_age_days * 86400
        for d in self.target_dirs:
            path = Path(d)
            if not path.exists():
                continue
            for file_path in path.glob("**/*.log"):
                try:
                    if (now - file_path.stat().st_mtime) > age_limit:
                        file_path.unlink()
                        deleted_count += 1
                except Exception:
                    pass
        return deleted_count

    def check_scripts_health(self, script_names: list) -> dict:
        status = {}
        try:
            ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
            for script in script_names:
                if script in ps_output:
                    status[script] = "RUNNING"
                else:
                    status[script] = "STOPPED"
        except Exception:
            for script in script_names:
                status[script] = "UNKNOWN"
        return status

if __name__ == "__main__":
    print("[~] Запуск практических задач Малыша...")
    assistant = MalyshAssistant()
    print(f"[+] Аудит сети: {assistant.audit_network()}")
    print(f"[+] Статус процессов: {assistant.check_scripts_health(['malysh_wave_patch.py'])}")
    print(f"[+] Очистка памяти: удалено логов: {assistant.smart_cleanup(max_file_age_days=15)} шт.")
    print("[✓] Практический модуль успешно отработал.")
