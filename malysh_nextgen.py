import cmath, math, time, numpy as np

genetic_memory = []

def get_system_metrics():
    return np.array([np.random.uniform(20, 90), 45.0, 80.0])

def malysh_core(metrics, state, last_load):
    current_load = metrics[0]
    delta_load = abs(current_load - last_load)
    theta_step = (math.pi / 4) * (1 + delta_load / 100)
    
    alpha = 1.0 + (current_load / 200.0)
    beta = 2.0 - alpha
    
    if current_load > 50:
        state *= cmath.rect(1.0, theta_step) * alpha
    else:
        state *= cmath.rect(1.0, -theta_step) * beta
        
    return state, current_load

state = complex(1.0, 0.0)
last_load = 50.0

print("=== Запуск Малыша 2.0 (Синтез: Иммунитет + Синапс + Память) ===")
for i in range(5):
    metrics = get_system_metrics()
    state, last_load = malysh_core(metrics, state, last_load)
    genetic_memory.append([state.real, state.imag])
    
    print(f"Синхронизация {i+1} | Нагрузка: {metrics[0]:.1f}% | Память: {len(genetic_memory)} форм")
    print(f"Тензор состояния: {state.real:.2f}, {state.imag:.2f}")

print("\nМалыш адаптирован. Паттерны зафиксированы в тензорной памяти.")
