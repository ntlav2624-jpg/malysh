import os
import time
import numpy as np

class PureDNSClaySolver:
    """Чистый DNS (Direct Numerical Simulation) без SGS и искусственных демпферов."""
    def __init__(self, N=32):
        print(f"⚡ [Малыш PURE DNS]: Снятие всех защит. Чистая вязкость на сетке {N}³...")
        self.N = N
        self.dx = 2 * np.pi / N
        self.viscosity = 0.005  # Малая вязкость, чтобы дать нелинейности проявить себя
        self.cycle = 0
        
        # Сложные, сильно закрученные начальные условия (асимметричные гармоники)
        x = np.linspace(0, 2 * np.pi, self.N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        self.u = np.sin(X) * np.cos(Y) * np.sin(Z) + 0.5 * np.cos(Y * Z)
        self.v = -np.cos(X) * np.sin(Y) * np.sin(Z) + 0.5 * np.sin(X * Z)
        self.w = 0.2 * np.sin(X) * np.sin(Y)
        
        self.E_0 = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
        print(f"📊 Стартовая кинетическая энергия (E_0): {self.E_0:.6f}\n")

    def compute_laplacian(self, field):
        return (
            np.roll(field, 1, axis=0) + np.roll(field, -1, axis=0) +
            np.roll(field, 1, axis=1) + np.roll(field, -1, axis=1) +
            np.roll(field, 1, axis=2) + np.roll(field, -1, axis=2) - 
            6.0 * field
        ) / (self.dx**2)

    def compute_convective(self, u, v, w):
        # Аппроксимация нелинейного конвективного члена (u * grad)u через центральные разности
        du_dx, du_dy, du_dz = np.gradient(u, self.dx)
        dv_dx, dv_dy, dv_dz = np.gradient(v, self.dx)
        dw_dx, dw_dy, dw_dz = np.gradient(w, self.dx)
        
        conv_u = u * du_dx + v * du_dy + w * du_dz
        conv_v = u * dv_dx + v * dv_dy + w * dv_dz
        conv_w = u * dw_dx + v * dw_dy + w * dw_dz
        return conv_u, conv_v, conv_w

    def run_simulation(self, max_cycles=150):
        enstrophy_history = []
        
        for self.cycle in range(1, max_cycles + 1):
            # Лапласиан (чистая вязкость)
            lap_u = self.compute_laplacian(self.u)
            lap_v = self.compute_laplacian(self.v)
            lap_w = self.compute_laplacian(self.w)
            
            # Нелинейный конвективный член
            conv_u, conv_v, conv_w = self.compute_convective(self.u, self.v, self.w)
            
            dt = 0.003  # Малый шаг по времени для устойчивости схемы
            
            # Чистое обновление по уравнениям Навье — Стокса (без искусственных коэффициентов)
            self.u += dt * (self.viscosity * lap_u - conv_u)
            self.v += dt * (self.viscosity * lap_v - conv_v)
            self.w += dt * (self.viscosity * lap_w - conv_w)
            
            # Расчет энстрофии
            du_dy, du_dx, du_dz = np.gradient(self.u, self.dx)
            dv_dy, dv_dx, dv_dz = np.gradient(self.v, self.dx)
            dw_dy, dw_dx, dw_dz = np.gradient(self.w, self.dx)
            
            rot_x = dw_dy - dv_dz
            rot_y = du_dz - dw_dx
            rot_z = dv_dx - du_dy
            
            enstrophy = 0.5 * np.sum(rot_x**2 + rot_y**2 + rot_z**2) * (self.dx**3)
            enstrophy_history.append(enstrophy)
            
            energy = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
            div_max = np.max(np.abs(du_dx + dv_dy + dw_dz))
            
            if self.cycle % 20 == 0 or np.isnan(energy) or np.isinf(energy):
                print(f"🔬 [Чистый DNS | Цикл {self.cycle}]: E = {energy:.5f} | Ω = {enstrophy:.4f} | Div = {div_max:.5f}")
            
            if np.isnan(energy) or np.isinf(energy) or energy > 1e4:
                print(f"\n💥 [ВЗРЫВ / BLOW-UP НА ОБНАРУЖЕННОМ УРОВНЕ]: На цикле {self.cycle} система потеряла устойчивость!")
                return "BLOW_UP_DETECTED"
            
            time.sleep(0.01)

        max_ens = max(enstrophy_history)
        print(f"\n🔒 [Малыш]: Цикл завершен без машинного срыва. Макс. энстрофия: {max_ens:.4f}")
        return "PURE_BOUNDED"

if __name__ == "__main__":
    solver = PureDNSClaySolver()
    solver.run_simulation()
