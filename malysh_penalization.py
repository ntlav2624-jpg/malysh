import os
import time
import numpy as np

class PenalizedPseudospectralSolver:
    """Решатель 64³ с методом объемной пенализации для обтекания препятствия."""
    def __init__(self, N=64):
        print("🛠️ [Малыш Penalization]: Инициализация сетки с препятствием...")
        self.N = N
        self.L = 2 * np.pi
        self.dx = self.L / N
        self.viscosity = 0.004
        self.cycle = 0
        
        # Волновые числа
        k = np.fft.fftfreq(N, d=self.dx) * 2 * np.pi
        self.KX, self.KY, self.KZ = np.meshgrid(k, k, k, indexing='ij')
        self.K_sq = self.KX**2 + self.KY**2 + self.KZ**2
        self.K_sq[0, 0, 0] = 1.0  
        
        # Создаем маску препятствия (цилиндр по центру в плоскости XY)
        x = np.linspace(0, self.L, N, endpoint=False)
        X, Y, Z = np.meshgrid(x, x, x, indexing='ij')
        
        # Центр куба и радиус цилиндра
        center_x, center_y = self.L / 2, self.L / 2
        radius = 0.8
        
        # Маска: 1 внутри цилиндра, 0 снаружи
        self.chi = np.zeros((N, N, N))
        cylinder_mask = ((X - center_x)**2 + (Y - center_y)**2) <= radius**2
        self.chi[cylinder_mask] = 1.0
        
        # Задаем поступательный поток слева направо (U_inf = 1.0)
        self.u = np.ones((N, N, N)) * 1.0
        self.v = np.zeros((N, N, N))
        self.w = np.zeros((N, N, N))
        
        # Убираем скорость внутрь твердого тела
        self.u[self.chi > 0] = 0.0
        
        print(f"🎯 Препятствие внедрено. Узлов внутри тела: {int(np.sum(self.chi))}")

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

    def run_simulation(self, max_cycles=80):
        dt = 0.001
        eta = 1e-4  # Параметр проницаемости пенализации (чем меньше, тем тверже стенка)
        
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
            
            # Нелинейность
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
            
            # Шаг вязкости и конвекции в спектре
            U_hat = U_hat + dt * (-self.viscosity * self.K_sq * U_hat - P_conv_u)
            V_hat = V_hat + dt * (-self.viscosity * self.K_sq * V_hat - P_conv_v)
            W_hat = W_hat + dt * (-self.viscosity * self.K_sq * W_hat - P_conv_w)
            
            self.u = np.real(np.fft.ifftn(U_hat))
            self.v = np.real(np.fft.ifftn(V_hat))
            self.w = np.real(np.fft.ifftn(W_hat))
            
            # ПРИМЕНЕНИЕ ПЕНАЛИЗАЦИИ (зануление скорости внутри препятствия)
            self.u = self.u - dt * (self.chi / eta) * self.u
            self.v = self.v - dt * (self.chi / eta) * self.v
            self.w = self.w - dt * (self.chi / eta) * self.w
            
            energy = 0.5 * np.sum(self.u**2 + self.v**2 + self.w**2) * (self.dx**3)
            elapsed = time.time() - start_time
            
            if self.cycle % 10 == 0:
                print(f"🌊 [Obstacle Flow | Цикл {self.cycle}]: E = {energy:.4f} | [{elapsed:.2f}s]")

        print("🏁 Расчет обтекания с пенализацией успешно завершен!")

if __name__ == "__main__":
    solver = PenalizedPseudospectralSolver(N=64)
    solver.run_simulation()
