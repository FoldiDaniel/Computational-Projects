import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


N = 100 # number of nodes
Length = 3.0  # length of the rod (in meters)
FPS = 25
dt = 1. / FPS  # time spacing (in seconds)
dx = Length / (N - 1)  # grid spacing (in meters)
alpha = 0.1  # thermal diffusivity (in m^2/s)

r = alpha * dt / (dx * dx)

temperature = np.zeros(N)
temperature[-1] = 25.0  # initial temperature at the left end (in °C)


A = np.zeros((N, N))
for i in range(N):
        if i == 0:
            # fixed temperature boundary condition at the left end
            A[i, i] = 1
        elif i == N - 1:
            # fixed temperature boundary condition at the right end
            A[i, i] = 1
        else:
            A[i, i-1] = -r
            A[i, i] = 2 + 2 * r
            A[i, i+1] = -r

def update_temperature(initial_temperature, r):
    # Using Crank-Nicolson method to update the temperature distribution
    b = np.zeros(N)

    for i in range(N):
        if i == 0:
            b[i] = initial_temperature[i]  
        elif i == N - 1:
            b[i] = initial_temperature[i]
        else:
            b[i] = (2 - 2 * r) * initial_temperature[i] + r * (initial_temperature[i-1] + initial_temperature[i+1])
    
    return np.linalg.solve(A, b)


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={'height_ratios': [10, 1]})
fig.suptitle('1D Heat Transfer', fontsize=14)
x = np.linspace(0, Length, N)

# Line graph
line, = ax1.plot(x, temperature, color='black', lw=2)
ax1.set_ylim(temperature.min()-max(2, temperature.min()*0.1), temperature.max()*1.1)
ax1.set_ylabel('Temperature (°C)')
ax1.set_xlabel('Position (m)')
ax1.grid(True, linestyle='--', alpha=0.6)

# Thermal map
extent = [0, Length, 0, 1] # [xmin, xmax, ymin, ymax]
thermal_map = ax2.imshow(temperature.reshape(1, -1), cmap='hot', aspect='auto', 
                         extent=extent, vmin=temperature.min()-1, vmax=temperature.max()+1)
ax2.set_yticks([])


def update(frame):
    global temperature
    temperature = update_temperature(temperature, r)
    line.set_ydata(temperature)
    thermal_map.set_data(temperature.reshape(1, -1))
    return line, thermal_map


animation = FuncAnimation(fig, update, frames=200, interval=1000/FPS, blit=False)

plt.tight_layout()
plt.show()