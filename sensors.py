import os
import subprocess
import time

def get_termux_entropy():
    t = time.time()
    micro = int((t - int(t)) * 1000000)

    mem_entropy = 0
    try:
        free_output = subprocess.check_output(['free'], universal_newlines=True)
        lines = free_output.strip().split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            mem_entropy = int(parts[3]) % 1000
    except Exception:
        mem_entropy = micro % 1000

    entropy_value = (micro % 1000 + mem_entropy) / 2000.0
    phase_shift = (micro % 628) / 100.0

    return entropy_value, phase_shift

if __name__ == "__main__":
    e, p = get_termux_entropy()
    print(f"[СЕНСОР] Энтропия: {e:.4f} | Фазовый сдвиг: {p:.4f}")
