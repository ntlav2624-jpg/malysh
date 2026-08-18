import os
import numpy as np
import matplotlib.pyplot as plt

os.makedirs("malysh", exist_ok=True)
os.makedirs("examples", exist_ok=True)

class ResonantNavierStokesModel:
    def __init__(self, t_star=0.0, delta_t=1.0):
        self.t_star = t_star
        self.delta_t = delta_t

    def compute_dynamics(self, t_vals):
        classical_gradient = 5.0 / (np.abs(t_vals - self.t_star) + 0.05)**1.5
        coherence = np.exp(-((t_vals - self.t_star)**2) / (0.2 * self.delta_t**2))
        nu_eff_limit = 12.0
        regulated_gradient = classical_gradient * (1.0 - 0.98 * coherence) + nu_eff_limit * coherence
        nu_eff = nu_eff_limit * coherence
        return {
            "t_vals": t_vals,
            "classical_gradient": classical_gradient,
            "regulated_gradient": regulated_gradient,
            "coherence": coherence,
            "nu_eff": nu_eff
        }

def main():
    print("Инициализация единого модуля Малыш...")
    t_vals = np.linspace(-1.0, 1.0, 1000)
    model = ResonantNavierStokesModel(t_star=0.0, delta_t=1.0)
    data = model.compute_dynamics(t_vals)
    classical_display = np.minimum(data["classical_gradient"], 100.0)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    ax1.plot(data["t_vals"], classical_display, '--', color='#e74c3c', linewidth=2.5, label='Классический взрыв')
    ax1.plot(data["t_vals"], data["regulated_gradient"], '-', color='#27ae60', linewidth=3.0, label='Слой 7: Регуляризованный вихрь')
    ax1.fill_between(data["t_vals"], 0, data["regulated_gradient"], color='#2ecc71', alpha=0.3)
    ax1.axvline(0.0, color='#2980b9', linestyle='-.', alpha=0.8)
    ax1.set_title('Регуляризация турбулентности (Навье-Стокс)', fontsize=14, fontweight='bold', pad=12)
    ax1.set_xlabel('Временной резонансный вектор T', fontsize=12)
    ax1.set_ylabel('Градиент скорости |∇u|', fontsize=12)
    ax1.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    ax1.set_xlim(-1.0, 1.0)
    ax1.set_ylim(0, 110.0)

    ax2.plot(data["t_vals"], data["coherence"], color='#8e44ad', linewidth=2.5, label='Синхронизация вихрей C(T)')
    ax2.plot(data["t_vals"], data["nu_eff"], color='#d35400', linewidth=2.5, linestyle='--', label='Эффективная вязкость v_eff')
    ax2.axvline(0.0, color='#2980b9', linestyle='-.', alpha=0.8)
    ax2.set_title('Динамика вязкости в центре завихрения', fontsize=14, fontweight='bold', pad=12)
    ax2.set_xlabel('Временной резонансный вектор T', fontsize=12)
    ax2.set_ylabel('Уровень стабилизации', fontsize=12)
    ax2.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    ax2.set_xlim(-1.0, 1.0)

    plt.tight_layout()
    plt.savefig('navier_stokes_solution.png', dpi=300)
    print("Готово! График сохранен в файл: navier_stokes_solution.png")

if __name__ == '__main__':
    main()
