import numpy as np

# simplified version with 4 nodes

N = 4
initial_temperature = np.array([10.0, 0.0, 0.0, 0.0])

dt = 1.0  # time spacing (in seconds)
dx = 1.0  # grid spacing (in meters)
alpha = 0.1  # thermal diffusivity (in m^2/s)

r = alpha * dt / (dx * dx)

a = np.zeros((N, N))
b = np.zeros(N)

for i in range(N):
    if i == 0:
        # fixed temperature boundary condition at the left end
        a[i, i] = 1
        b[i] = initial_temperature[i]  
    elif i == N - 1:
        # fixed temperature boundary condition at the right end
        a[i, i] = 1
        b[i] = initial_temperature[i]
    else:
        a[i, i-1] = -r
        a[i, i] = 2 + 2 * r
        a[i, i+1] = -r
        b[i] = (2 - 2 * r) * initial_temperature[i] + r * (initial_temperature[i-1] + initial_temperature[i+1])

print(a)
print(b)

print(np.linalg.solve(a, b))  # solve for the updated temperature distribution