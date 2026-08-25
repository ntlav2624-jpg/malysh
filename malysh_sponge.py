import os
import time
import numpy as np

class MalyshSpongeSolver:
    """Решатель 64³ с буферной зоной (Sponge Layer) для подавления периодических границ."""
    def __init__(self, N=64):
        print("🛡️ [Малыш Sponge]: Инициализация демпфирующей буферной зоны...")
        self.N = N
        self.L = 2 * np.pi
        self.dx = self.L / N
        self.viscosity = 0.002
        self.cycle = 0
        
        # Волновые числа
        k = np.fft.fftfreq(N, d=self.dx) * 2 * np.pi
        self.KX, self.KY, self.KZ = np.meshgrid(k, k, k, indexing='ij')
        self.K_sq = self.KX**2 + self.KY**2 + self.KZ**2
        self.K_sq[0, 0, 0] = 1.0  
        
        # Координаты сетки
        x = np.linspace(0, self.L, N, endpoint=False)
        self.X, self.Y, self.Z = np.meshgrid(x, x, x, indexing='ij')
        
        # Создаем маску буферной зоны на правом конце по оси X (последние 20% куба)
        self.sigma = np.zeros((N, N, N))
        sponge_start = self.L * 0.8
        mask_indices = self.X > sponge_start
        self.sigma[mask_indices] = 10.0 * ((self.X[mask_indices] - sponge_start) / (self.L - sponge_start))**2
        
        # Инициализация потока с возмущением
        self.u = 1.5 + 0.3 * np.sin(self.X) * np.cos(self.Y)
        self.v = 0.2 * np.sin(self.Y) * np.sin(self.Z)
        self.w = np.zeros((N, N, N))
        
        print(f"🎯 Буферная зона активирована. Затронуто узлов: {int(np.sum(mask_indices))}")

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
        dt = 0.001
        u_target = 1.5  # Целевая скорость потока на выходе
        
        for self.cycle in range(1, max_cycles + 1):
            start_time = time.time()
            
            U_hat = np.fft.fftn(self.u)
            V_hat = np.fft.fftn(self.v)
            W_hat = np.fft.fftn(self.w)
            
            du_dx = np.real(np.fft.ifftn(1j * self.KX * U_hat))
            du_dy = np.real(np.fft.ifftn(1j * self.KY * U_hat))
            du_dz = np.real(np.fft.ifftn(1j * self.KZ * U_hat))
            
            dv_dx = np.real(np.fft.ifftn(1j * self.KX * V_hat))
            dv_dy = np.real(np.fft.ifftn(1j * self.KY * V_hat))
            dv_dz = np.real(np.fft.ifftn(1j * self.KZ * V_hat))
            
            dw_dx = np.real(np.fft.ifftn(1j * self.KX * W_hat))
            dw_dy = np.real(np.fft.ifftn(1j * self.KY * W_hat))
            dw_dz = np.real(np.fft.ifftn(1j * self.KZ * W_hat))
            
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
            
            U_hat = U_hat + dt * (-self.viscosity * self.K_sq * U_hat - P_conv_u)
            V_hat = V_hat + dt * (-self.viscosity * self.K_sq * V_hat - P_conv_v)
            W_hat = W_hat + dt * (-self.viscosity * self.K_sq * W_hat - P_conv_w)
            
            self.u = np.real(np.fft.ifftn(U_hat))
            self.v = np.real(np.fft.ifftn(V_hat))
            self.w = np.real(np.fft.ifftn(W_hat))
            
            # ПРИМЕНЕНИЕ БУФЕРНОЙ ЗОНЫ (гашение возмущений справа)
            self.u = self.u - dt * self.sigma * (self.u - u_target)
            self.v = self.v - dt * self.sigma * self.v
            self.w = self.w - dt * self.sigma * self.w
            
            energy = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
            elapsed = time.time() - start_time
            
            if self.cycle % 10 == 0:
                print(f"🛡️ [Sponge Цикл {self.cycle}]: E = {energy:.4f} | Буфер активен | [{elapsed:.2f}s]")

        print("🏁 Симуляция с буферной зоной успешно завершена!")

if __name__ == "__main__":
    solver = MalyshSpongeSolver(N=64)
    solver.run_simulation()
