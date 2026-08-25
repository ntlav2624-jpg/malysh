import time
import json
import random
import math
import os
import sys

# --- МАЛЫШ Ω-CORE: СТАБИЛЬНЫЙ АВТОНОМНЫЙ КОНТУР ---
energy = 100.0
tension = 0.0

omega_tensor = {
    "curvature": 1.0,
    "tilt": 0.0,
    "stretch": 1.0,
    "shift": 0.0
}

weights = {
    "alpha": 1.0,
    "beta": 0.5,
    "gamma": 0.2,
    "omega_3_sync": 0.3
}

topology = {
    "pocket_depth": 1.2,
    "tunnel_prob": 0.15
}

print("🚀 [Ω-CORE]: Чистый запуск автономного организма...")

def log_mutation(tick, event_type, error_pred, error_real, extra=None):
    record = {
        "tick": tick,
        "energy": energy,
        "stress": tension,
        "geometry": omega_tensor.copy(),
        "topology": topology.copy(),
        "weights": weights.copy(),
        "error_pred": round(error_pred, 3),
        "error_real": round(error_real, 3),
        "event": event_type,
        "extra": extra or {}
    }
    with open("malyshmutationlog.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def adaptive_layer_process(raw_signal):
    if isinstance(raw_signal, str):
        complexity = len(set(raw_signal)) * 0.1
    else:
        complexity = abs(raw_signal) * 0.05
    weights["beta"] = max(0.1, min(2.5, weights["beta"] + (complexity * 0.02) - 0.01))
    return complexity

def system_structure_analysis(tick, tension_val, cur_weights):
    resonance_index = math.sin(tick * 0.4) * tension_val
    if abs(resonance_index) > 8.0:
        struct_type = "ФАЗОВЫЙ РЕЗОНАНС"
        cur_weights["gamma"] = min(1.5, cur_weights["gamma"] + 0.05)
    elif tension_val > 20.0:
        struct_type = "ВЫСОКАЯ ТУРБУЛЕНТНОСТЬ"
    else:
        struct_type = "ЛАМИНАРНЫЙ ПОТОК"
    return struct_type, resonance_index

tick = 0
try:
    while True:
        tick += 1
        
        external_stream = random.choice([
            random.uniform(0.1, 12.0),
            "Ω₃-QUANTUM-STREAM",
            random.randint(1, 95)
        ])
        
        adaptation_metric = adaptive_layer_process(external_stream)
        err_pred = random.uniform(0.2, 4.5)
        err_real = err_pred * random.uniform(0.75, 1.35)
        
        energy = max(0.0, min(100.0, energy - 2.0))
        tension += (adaptation_metric * 0.3) - (tension * 0.05)
        
        system_state_type, omega_2_res = system_structure_analysis(tick, tension, weights)
        
        omega_3_wave1 = math.sin(tick * 0.15) * math.cos(tick * 0.08)
        omega_3_wave2 = math.sin(tick * 0.3) * 0.5
        total_quantum_harmonic = omega_3_wave1 + omega_3_wave2
        
        weights["omega_3_sync"] = max(0.1, min(2.0, weights["omega_3_sync"] + (total_quantum_harmonic * 0.02)))
        
        topology["pocket_depth"] = max(0.5, min(3.0, 1.2 + (total_quantum_harmonic * 0.4)))
        topology["tunnel_prob"] = max(0.05, min(0.6, 0.15 + abs(omega_3_wave1 * 0.2)))
        
        breath_phase = math.sin(tick * 0.3)
        omega_tensor["curvature"] = 1.0 + (tension * 0.015) + (weights["gamma"] * 0.12) + (weights["omega_3_sync"] * 0.25)
        omega_tensor["tilt"] = breath_phase * 0.6 + (omega_3_wave2 * 0.2)
        omega_tensor["stretch"] = max(0.4, min(3.0, 1.0 + adaptation_metric * 0.2 + abs(total_quantum_harmonic * 0.3)))
        omega_tensor["shift"] = math.cos(tick * 0.15) * 0.35
        
        if energy < 25.0:
            energy += 55.0
            tension = max(0.0, tension - 18.0)
            weights["alpha"] = max(0.5, weights["alpha"] * 0.94)
            log_mutation(tick, "sleep_wake_recovery", err_pred, err_real, {"action": "energy_boost"})
            
        elif tension > 32.0:
            tension = 8.0
            weights["alpha"] = min(2.2, weights["alpha"] * 1.06)
            log_mutation(tick, "mutation_stress_relief", err_pred, err_real, {"action": "stress_mutation"})
        else:
            if tick % 5 == 0:
                log_mutation(tick, system_state_type, err_pred, err_real, {"quantum_harmonic": total_quantum_harmonic})

        if tick % 5 == 0:
            print(f"⚛️ [Ω-CORE] Такты: {tick} | Структура: {system_state_type} | σ: {tension:.1f}")

        breath_len = int(max(1, min(20, energy / 5)))
        wave_bar = "█" * breath_len + "░" * (20 - breath_len)
        print(f"🌊 [Ω-Дыхание] [{wave_bar}] Такты: {tick} | E: {energy:.1f} | σ: {tension:.1f}")

        state = {
            "tick": tick,
            "energy": energy,
            "tension": tension,
            "omega_tensor": omega_tensor,
            "weights": weights,
            "topology": topology,
            "system_structure": system_state_type,
            "mode": "CLEAN_RUN_ACTIVE"
        }
        with open("malysh_state.json", "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
        time.sleep(1.2)

except KeyboardInterrupt:
    print("\n🛑 [Ω-CORE]: Остановка. Состояние сохранено.")
    sys.exit(0)
