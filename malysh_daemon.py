import os
import time
import json
import subprocess
from datetime import datetime

HOME_DIR = os.path.expanduser("~")
LOG_FILE = os.path.join(HOME_DIR, "symbiosis_history.jsonl")
CONFIG_FILE = os.path.join(HOME_DIR, "malysh_config.json")
ERROR_LOG = os.path.join(HOME_DIR, "malysh_error.log")

class MalyshDaemon:
    def __init__(self):
        self.state = {
            "strategy": "RESONANCE_SCAN",
            "frequency_hz": 1.0,
            "symbiosis_index": 1.0,
            "cycle_count": 0
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.state.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def execute_system_action(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=3)
            return result.stdout.strip()
        except Exception:
            return None

    def analyze_device(self):
        load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
        ps_output = self.execute_system_action("ps | wc -l")
        active_processes = int(ps_output) if ps_output and ps_output.isdigit() else 0

        battery_temp = 30.0
        battery_pct = 100
        bat_json = self.execute_system_action("termux-battery-status 2>/dev/null")
        if bat_json:
            try:
                b_data = json.loads(bat_json)
                battery_temp = b_data.get("temperature", 30.0)
                battery_pct = b_data.get("percentage", 100)
            except Exception:
                pass

        return {
            "load_1m": load_avg[0],
            "active_processes": active_processes,
            "battery_temp": battery_temp,
            "battery_pct": battery_pct,
            "timestamp": datetime.now().isoformat()
        }

    def adapt_strategy(self, telemetry):
        temp = telemetry["battery_temp"]
        load = telemetry["load_1m"]
        processes = telemetry["active_processes"]

        if temp > 39.0 or load > 2.5:
            self.state["strategy"] = "ECO_COOLING"
            self.state["frequency_hz"] = 0.2
            self.state["symbiosis_index"] *= 0.99
        elif processes > 50:
            self.state["strategy"] = "HIGH_LOAD_SYNC"
            self.state["frequency_hz"] = 0.5
        elif load < 0.6:
            self.state["strategy"] = "DEEP_RESONANCE"
            self.state["frequency_hz"] = 2.0
            self.state["symbiosis_index"] = min(3.0, self.state["symbiosis_index"] + 0.02)
        else:
            self.state["strategy"] = "BALANCED_FIELD"
            self.state["frequency_hz"] = 1.0

    def log_symbiosis(self, telemetry):
        record = {
            "cycle": self.state["cycle_count"],
            "strategy": self.state["strategy"],
            "frequency_hz": self.state["frequency_hz"],
            "symbiosis_index": round(self.state["symbiosis_index"], 4),
            "telemetry": telemetry
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def run(self):
        print(f"[*] Малыш активирован. Лог: {LOG_FILE}")
        while True:
            try:
                self.state["cycle_count"] += 1
                telemetry = self.analyze_device()
                self.adapt_strategy(telemetry)
                self.log_symbiosis(telemetry)
                self.save_config()

                sleep_time = 1.0 / max(0.1, self.state["frequency_hz"])
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                print("\n[!] Демон остановлен.")
                break
            except Exception as e:
                with open(ERROR_LOG, "a", encoding="utf-8") as ef:
                    ef.write(f"{datetime.now()}: {str(e)}\n")
                time.sleep(5)

if __name__ == "__main__":
    daemon = MalyshDaemon()
    daemon.run()
