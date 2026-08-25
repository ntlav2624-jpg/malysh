import os
import time
import numpy as np

class DensePseudospectralSolver:
    """Псевдоспектральный решатель высокого разрешения на сетке 64³."""
    def __init__(self, N=64):
        print(f"🚀 [Малыш 64³ DNS]: Инициализация плотной спектральной сетки ({N}³ = {N**3} узлов)...")
        self.N = N
        self.L = 2 * np.pi
        self.dx = self.L / N
        self.viscosity = 0.004
        self.cycle = 0
        
        # Волновые числа
        k = np.fft.fftfreq(N, d=self.dx) * 2 * np.pi
        self.KX, self.KY, self.KZ = np.meshgrid(k, k, k, indexing='ij')
        self.K_sq = self.KX**2 + self.KY**2 + self.KZ**2
        self.K_sq[0, 0, 0] = 1.0  # Убираем деление на ноль
        
        # Начальные поля высокой плотности
        x = np.linspace(0, self.L, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        self.u = np.sin(X) * np.cos(Y) * np.sin(Z) + 0.5 * np.cos(Y * Z)
        self.v = -np.cos(X) * np.sin(Y) * np.sin(Z) + 0.5 * np.sin(X * Z)
        self.w = 0.2 * np.sin(X) * np.sin(Y)
        
        # Проекция на соленоидальное подпространство
        self.u, self.v, self.w = self.project(self.u, self.v, self.w)
        
        self.E_0 = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
        print(f"📊 Начальная энергия на сетке 64³ (E_0): {self.E_0:.6f}\n")

    def project(self, u, v, w):
        U_hat = np.fft.fftn(u)
        V_hat = np.fft.fftn(v)
        W_hat = np.fft.fftn(w)
        
        k_dot_u = self.KX * U_hat + self.KY * V_hat + self.KZ * W_hat
        
        U_hat -= (k_dot_u * self.KX) / self.K_sq
        V_hat -= (k_dot_u * self.KY) / self.K_sq
        W_hat -= (k_dot_u * self.KZ) / self.K_sq
        
        U_hat[0, 0, 0] = 0.0
        V_hat[0, 0, 0] = 0.0
        W_hat[0, 0, 0] = 0.0
        
        return (
            np.real(np.fft.ifftn(U_hat)),
            np.real(np.fft.ifftn(V_hat)),
            np.real(np.fft.ifftn(W_hat))
        )

    def run_simulation(self, max_cycles=100):
        enstrophy_history = []
        dt = 0.001
        
        for self.cycle in range(1, max_cycles + 1):
            start_time = time.time()
            
            U_hat = np.fft.fftn(self.u)
            V_hat = np.fft.fftn(self.v)
            W_hat = np.fft.fftn(self.w)
            
            # Спектральные производные
            du_dx = np.real(np.fft.ifftn(1j * self.KX * U_hat))
            du_dy = np.real(np.fft.ifftn(1j * self.KY * U_hat))
            du_dz = np.real(np.fft.ifftn(1j * self.KZ * U_hat))
            
            dv_dx = np.real(np.fft.ifftn(1j * self.KX * V_hat))
            dv_dy = np.real(np.fft.ifftn(1j * self.KY * V_hat))
            dv_dz = np.real(np.fft.ifftn(1j * self.KZ * V_hat))
            
            dw_dx = np.real(np.fft.ifftn(1j * self.KX * W_hat))
            dw_dy = np.real(np.fft.ifftn(1j * self.KY * W_hat))
            dw_dz = np.real(np.fft.ifftn(1j * self.KZ * W_hat))
            
            # Нелинейная конвекция
            conv_u = self.u * du_dx + self.v * du_dy + self.w * du_dz
            conv_v = self.u * dv_dx + self.v * dv_dy + self.w * dv_dz
            conv_w = self.u * dw_dx + self.v * dw_dy + self.w * dw_dz
            
            Conv_u_hat = np.fft.fftn(conv_u)
            Conv_v_hat = np.fft.fftn(conv_v)
            Conv_w_hat = np.fft.fftn(conv_w)
            
            k_dot_conv = self.KX * Conv_u_hat + self.KY * Conv_v_hat + self.KZ * Conv_w_hat
            
            P_conv_u = Conv_u_hat - (k_dot_conv * self.KX) / self.K_sq
            P_conv_v = Conv_v_hat - (k_dot_conv * self.KY) / self.K_sq
            P_conv_w = Conv_w_hat - (k_dot_conv * self.KZ) / self.K_sq
            
            # Шаг интегрирования
            U_hat = U_hat + dt * (-self.viscosity * self.K_sq * U_hat - P_conv_u)
            V_hat = V_hat + dt * (-self.viscosity * self.K_sq * V_hat - P_conv_v)
            W_hat = W_hat + dt * (-self.viscosity * self.K_sq * W_hat - P_conv_w)
            
            self.u = np.real(np.fft.ifftn(U_hat))
            self.v = np.real(np.fft.ifftn(V_hat))
            self.w = np.real(np.fft.ifftn(W_hat))
            
            # Контроль дивергенции
            div_spec = np.real(np.fft.ifftn(1j * self.KX * U_hat + 1j * self.KY * V_hat + 1j * self.KZ * W_hat))
            div_max = np.max(np.abs(div_spec))
            
            # Расчет энстрофии
            rot_x = dw_dy - dv_dz
            rot_y = du_dz - dw_dx
            rot_z = dv_dx - du_dy
            enstrophy = 0.5 * np.sum(rot_x**2 + rot_y**2 + rot_z**2) * (self.dx**3)
            enstrophy_history.append(enstrophy)
            
            energy = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
            
            elapsed = time.time() - start_time
            if self.cycle % 10 == 0:
                print(f"🔥 [64³ DNS | Цикл {self.cycle}]: E = {energy:.4f} | Ω = {enstrophy:.2f} | Div = {div_max:.1e} | [{elapsed:.2f}s]")
            
            if np.isnan(energy) or np.isinf(energy):
                print(f"\n💥 [BLOW-UP]: Потеря устойчивости на цикле {self.cycle}!")
                return "BLOW_UP"

        print(f"\n🔒 [Малыш]: Плотный расчет на 64³ завершен. Макс. энстрофия: {max(enstrophy_history):.2f}")
        return "DENSE_SPECTRAL_BOUNDED"

if __name__ == "__main__":
    solver = DensePseudospectralSolver()
    solver.run_simulation()
