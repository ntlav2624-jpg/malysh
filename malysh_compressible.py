import os
import time
import numpy as np

class MalyshCompressibleSolver:
    """Решатель 64³ для сжимаемой среды (акустика и волны плотности)."""
    def __init__(self, N=64):
        print("🔊 [Малыш Compressible]: Инициализация сжимаемого акустического ядра...")
        self.N = N
        self.L = 2 * np.pi
        self.dx = self.L / N
        self.sound_speed = 5.0  # Скорость звука в среде
        self.viscosity = 0.001
        self.cycle = 0
        
        # Волновые числа
        k = np.fft.fftfreq(N, d=self.dx) * 2 * np.pi
        self.KX, self.KY, self.KZ = np.meshgrid(k, k, k, indexing='ij')
        self.K_sq = self.KX**2 + self.KY**2 + self.KZ**2
        self.K_sq[0, 0, 0] = 1.0  
        
        # Координаты сетки
        x = np.linspace(0, self.L, N, endpoint=False)
        self.X, self.Y, self.Z = np.meshgrid(x, x, x, indexing='ij')
        
        # Инициализация: фоновая плотность ро = 1.0 + локальный импульс давления (акустический сгусток)
        self.rho = 1.0 + 0.2 * np.exp(-((self.X - np.pi)**2 + (self.Y - np.pi)**2 + (self.Z - np.pi)**2) / 0.5)
        self.u = np.zeros((N, N, N))
        self.v = np.zeros((N, N, N))
        self.w = np.zeros((N, N, N))
        
        print("🎯 Акустический сгусток плотности внедрен в центр сетки.")

    def run_simulation(self, max_cycles=60):
        dt = 0.0002  # Малый шаг для сжимаемости (условие Куранта для звука)
        
        for self.cycle in range(1, max_cycles + 1):
            start_time = time.time()
            
            # Спектральные производные плотности и скорости
            Rho_hat = np.fft.fftn(self.rho)
            U_hat = np.fft.fftn(self.u)
            V_hat = np.fft.fftn(self.v)
            W_hat = np.fft.fftn(self.w)
            
            drho_dx = np.real(np.fft.ifftn(1j * self.KX * Rho_hat))
            drho_dy = np.real(np.fft.ifftn(1j * self.KY * Rho_hat))
            drho_dz = np.real(np.fft.ifftn(1j * self.KZ * Rho_hat))
            
            du_dx = np.real(np.fft.ifftn(1j * self.KX * U_hat))
            dv_dy = np.real(np.fft.ifftn(1j * self.KY * V_hat))
            dw_dz = np.real(np.fft.ifftn(1j * self.KZ * W_hat))
            
            # Уравнение непрерывности (сжимаемость): drho/dt = - div(rho * u)
            div_rho_u = self.rho * (du_dx + dv_dy + dw_dz) + self.u * drho_dx + self.v * drho_dy + self.w * drho_dz
            self.rho = self.rho - dt * div_rho_u
            
            # Уравнение движения с градиентом давления (акустическая волна ~ c^2 * grad(rho))
            dp_dx = (self.sound_speed**2) * drho_dx
            dp_dy = (self.sound_speed**2) * drho_dy
            dp_dz = (self.sound_speed**2) * drho_dz
            
            self.u = self.u - dt * (dp_dx / self.rho)
            self.v = self.v - dt * (dp_dy / self.rho)
            self.w = self.w - dt * (dp_dz / self.rho)
            
            total_mass = np.sum(self.rho) * (self.dx**3)
            max_rho = np.max(self.rho)
            elapsed = time.time() - start_time
            
            if self.cycle % 10 == 0:
                print(f"🔊 [Акустика Цикл {self.cycle}]: Max Rho = {max_rho:.4f} | Масса = {total_mass:.2f} | [{elapsed:.2f}s]")

        print("🏁 Симуляция сжимаемой газодинамики успешно завершена!")

if __name__ == "__main__":
    solver = MalyshCompressibleSolver(N=64)
    solver.run_simulation()
