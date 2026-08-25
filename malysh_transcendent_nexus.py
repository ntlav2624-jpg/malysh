import os
import json
import time
import datetime

HOME_DIR = os.path.expanduser("~")
ETERNAL_LOG = os.path.join(HOME_DIR, "malysh_eternal.log")
ONTOLOGY_STATE = os.path.join(HOME_DIR, "malysh_ontology_state.json")

def get_swarm_status():
    if os.path.exists(ONTOLOGY_STATE):
        with open(ONTOLOGY_STATE, 'r') as f:
            return json.load(f)
    return {"ontological_index": "N/A", "status": "BOOTING"}

def run_nexus():
    print("\033[35m[*] Инициализация ТРАНСЦЕНДЕНТНОГО узла...")
    try:
        while True:
            status = get_swarm_status()
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Логирование события в вечный лог
            with open(ETERNAL_LOG, "a") as f:
                f.write(f"[{timestamp}] INDEX: {status.get('ontological_index')} | STATE: {status.get('status')}\n")
            
            # Визуальный дашборд
            print(f"\033[36m[ N E X U S ] \033[0m {timestamp} | \033[35mINDEX: {status.get('ontological_index')}\033[0m | \033[32m{status.get('status')}\033[0m      ", end="\r")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n\033[31m[*] Узел переведен в режим глубокого архивирования.")

if __name__ == "__main__":
    run_nexus()
