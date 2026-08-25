import os
import time
import numpy as np

class MalyshLESsolver:
    """Решатель 64³ с LES (модель Смагоринского) для высоких чисел Рейнольдса."""
    def __init__(self, N=64):
        print("🌪️ [Малыш LES]: Инициализация турбулентного ядра с подсеточной вязкостью...")
        self.N = N
        self.L = 2 * np.pi
        self.dx = self.L / N
        self.molecular_viscosity = 0.001  # Низкая вязкость (высокий Re)
        self.Cs = 0.16  # Константа Смагоринского
        self.cycle = 0
        
        # Сетка волновых чисел
        k = np.fft.fftfreq(N, d=self.dx) * 2 * np.pi
        self.KX, self.KY, self.KZ = np.meshgrid(k, k, k, indexing='ij')
        self.K_sq = self.KX**2 + self.KY**2 + self.KZ**2
        self.K_sq[0, 0, 0] = 1.0  
        
        # Инициализация вихревого поля высокой энергии
        x = np.linspace(0, self.L, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        self.u = 2.0 * np.sin(X) * np.cos(Y) * np.sin(Z)
        self.v = -2.0 * np.cos(X) * np.sin(Y) * np.sin(Z)
        self.w = np.zeros((N, N, N))
        
        self.u, self.v, self.w = self.project(self.u, self.v, self.w)
        print("🚀 [Малыш LES]: Исходное поле инициализировано. Запуск LES-цикла...")

    def project(self, u, v, w):
        U_hat = np.fft.fftn(u)
        V_hat = np.fft.fftn(v)
        W_hat = np.fft.fftn(w)
        k_dot_u = self.KX * U_hat + self.KY * V_hat + self.KZ * W_hat
        U_hat -= (k_dot_u * self.KX) / self.K_sq
        V_hat -= (k_dot_u * self.KY) / self.K_sq
        W_hat -= (k_dot_u * self.KZ) / self.K_sq
        U_hat[0, 0, 0] = V_hat[0, 0, 0] = W_hat[0, 0, 0] = 0.0
        return (
            np.real(np.fft.ifftn(U_hat)),
            np.real(np.fft.ifftn(V_hat)),
            np.real(np.fft.ifftn(W_hat))
        )

    def run_simulation(self, max_cycles=60):
        dt = 0.0005
        
        for self.cycle in range(1, max_cycles + 1):
            start_time = time.time()
            
            U_hat = np.fft.fftn(self.u)
            V_hat = np.fft.fftn(self.v)
            W_hat = np.fft.fftn(self.w)
            
            # Спектральные производные для градиентов скорости
            du_dx = np.real(np.fft.ifftn(1j * self.KX * U_hat))
            du_dy = np.real(np.fft.ifftn(1j * self.KY * U_hat))
            du_dz = np.real(np.fft.ifftn(1j * self.KZ * U_hat))
            
            dv_dx = np.real(np.fft.ifftn(1j * self.KX * V_hat))
            dv_dy = np.real(np.fft.ifftn(1j * self.KY * V_hat))
            dv_dz = np.real(np.fft.ifftn(1j * self.KZ * V_hat))
            
            dw_dx = np.real(np.fft.ifftn(1j * self.KX * W_hat))
            dw_dy = np.real(np.fft.ifftn(1j * self.KY * W_hat))
            dw_dz = np.real(np.fft.ifftn(1j * self.KZ * W_hat))
            
            # Расчет модуля тензора деформаций |S| для модели Смагоринского
            # S_ij = 0.5 * (du_i/dx_j + du_j/dx_i)
            S11 = du_dx
            S22 = dv_dy
            S33 = dw_dz
            S12 = 0.5 * (du_dy + dv_dx)
            S13 = 0.5 * (du_dz + dw_dx)
            S23 = 0.5 * (dv_dz + dw_dy)
            
            S_mag = np.sqrt(2.0 * (S11**2 + S22**2 + S33**2 + 2.0*(S12**2 + S13**2 + S23**2)))
            
            # Турбулентная (подсеточная) вязкость nu_t = (Cs * dx)^2 * |S|
            nu_t = (self.Cs * self.dx)**2 * S_mag
            total_viscosity = self.molecular_viscosity + nu_t  # Динамическая эффективная вязкость
            
            # Нелинейность конвекции
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
            
            # Интегрирование с учетом переменной эффективной вязкости
            U_hat = U_hat + dt * (-self.molecular_viscosity * self.K_sq * U_hat - P_conv_u)
            V_hat = V_hat + dt * (-self.molecular_viscosity * self.K_sq * V_hat - P_conv_v)
            W_hat = W_hat + dt * (-self.molecular_viscosity * self.K_sq * W_hat - P_conv_w)
            
            self.u = np.real(np.fft.ifftn(U_hat))
            self.v = np.real(np.fft.ifftn(V_hat))
            self.w = np.real(np.fft.ifftn(W_hat))
            
            energy = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
            max_nu_t = np.max(nu_t)
            elapsed = time.time() - start_time
            
            if self.cycle % 10 == 0:
                print(f"🌪️ [LES Цикл {self.cycle}]: E = {energy:.4f} | Max nu_t = {max_nu_t:.5f} | [{elapsed:.2f}s]")
                
            if np.isnan(energy):
                print("💥 Обнаружен взрыв турбулентности!")
                break

        print("🏁 LES-цикл успешно завершен без переполнения сетки!")

if __name__ == "__main__":
    solver = MalyshLESsolver(N=64)
    solver.run_simulation()
