import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button, RadioButtons, CheckButtons, TextBox

N = 100 # number of nodes
Length = 2.0  # length of the rod (in meters)
FPS = 25
dt = 1. / FPS  # time spacing (in seconds)
dx = Length / (N - 1)  # grid spacing (in meters)
alpha = 0.01  # thermal diffusivity (in m^2/s)

r = alpha * dt / (dx * dx)

fixed_left = True
fixed_right = True

temperature = np.zeros(N)
temperature[-1] = 25.0  # initial temperature at the right end (in °C)

def construct_matrix():
    a = np.zeros((N, N))
    for i in range(N):
            if i == 0:
                if fixed_left:
                    a[i, i] = 1
                else:
                    a[i, i] = 2 + 2 * r
                    a[i, i+1] = -2 * r
            elif i == N - 1:
                if fixed_right:
                    a[i, i] = 1
                else:
                    a[i, i] = 2 + 2 * r
                    a[i, i-1] = -2 * r
            else:
                a[i, i-1] = -r
                a[i, i] = 2 + 2 * r
                a[i, i+1] = -r
    return a

A = construct_matrix()

def update_temperature(initial_temperature, r):
    # Using Crank-Nicolson method to update the temperature distribution
    b = np.zeros(N)

    for i in range(N):
        if i == 0:
            if fixed_left:
                b[i] = initial_temperature[i]
            else:
                b[i] = (2 - 2 * r) * initial_temperature[i] + 2 *r * (initial_temperature[i+1])
        elif i == N - 1:
            if fixed_right:
                b[i] = initial_temperature[i]
            else:
                b[i] = (2 - 2 * r) * initial_temperature[i] + 2 *r * (initial_temperature[i-1])
        else:
            b[i] = (2 - 2 * r) * initial_temperature[i] + r * (initial_temperature[i-1] + initial_temperature[i+1])
    
    return np.linalg.solve(A, b)


fig = plt.figure(figsize=(12, 6))
fig.suptitle('1D Heat Transfer - Crank-Nicolson Method', fontsize=14)

gs = fig.add_gridspec(2, 2, width_ratios=[4, 1], height_ratios=[9, 1])
ax1 = fig.add_subplot(gs[0, 0])
x = np.linspace(0, Length, N)

# Line graph
line, = ax1.plot(x, temperature, color='black', lw=2)
ax1.set_ylim(temperature.min()-max(2, temperature.min()*0.1), temperature.max()*1.1)
ax1.set_ylabel('Temperature (°C)')
ax1.set_xlabel('Position (m)')
ax1.grid(True, linestyle='--', alpha=0.6)

# Thermal map
ax2 = fig.add_subplot(gs[1, 0])
extent = [0, Length, 0, 1] # [xmin, xmax, ymin, ymax]
thermal_map = ax2.imshow(temperature.reshape(1, -1), cmap='hot', aspect='auto', 
                         extent=extent, vmin=temperature.min()-1, vmax=temperature.max()+1)
ax2.set_yticks([])

# UI
ui_x = 0.82
ui_w = 0.14

# Checkbox: Left Fixed
ax_check_left = fig.add_axes([ui_x, 0.72, ui_w, 0.25])
check_left = CheckButtons(ax_check_left, ['Fixed Left temp'], [True])
ax_check_left.set_frame_on(False) # Removes the cramped bounding box

# Textbox: Left Temp
ax_box_left = fig.add_axes([ui_x, 0.90, ui_w, 0.04])
text_box_left = TextBox(ax_box_left, 'Left Temp ', initial='0.0')

# Checkbox: Right Fixed
ax_check_right = fig.add_axes([ui_x, 0.56, ui_w, 0.25])
check_right = CheckButtons(ax_check_right, ['Fixed Right temp'], [True])
ax_check_right.set_frame_on(False) # Removes the cramped bounding box

# Textbox: Right Temp
ax_box_right = fig.add_axes([ui_x, 0.74, ui_w, 0.04])
text_box_right = TextBox(ax_box_right, 'Right Temp ', initial='25.0')

# Textbox: Rod Initial Temp
ax_box_rod = fig.add_axes([ui_x, 0.58, ui_w, 0.04])
text_box_rod = TextBox(ax_box_rod, 'Rod Temp ', initial='0.0')

# Selection: Material
ax_radio_mat = fig.add_axes([ui_x, 0.18, ui_w, 0.25])
ax_radio_mat.set_title("Material")
radio_mat = RadioButtons(ax_radio_mat, ('Generic', 'Copper', 'Steel', 'Glass'))
ax_radio_mat.set_frame_on(False) # Removes the cramped bounding box

# Button: Start Simulation
ax_button_start = fig.add_axes([ui_x, 0.06, ui_w, 0.06])
start_button = Button(ax_button_start, 'Start Simulation', color='lightgreen', hovercolor='palegreen')


materials = {'Generic': 5000, 'Copper': 111, 'Steel': 11.72, 'Glass': 0.34}

def update(frame):
    global temperature
    temperature = update_temperature(temperature, r)
    line.set_ydata(temperature)
    thermal_map.set_data(temperature.reshape(1, -1))
    return line, thermal_map


def on_start(event):
    global temperature, fixed_left, fixed_right, A, alpha, r

     #update boundary conditions based on checkboxes
    fixed_left = check_left.get_status()[0]
    fixed_right = check_right.get_status()[0]
    # Reset temperature based on user input

    left_temp = float(text_box_left.text)
    right_temp = float(text_box_right.text)
    rod_temp = float(text_box_rod.text)

    temperature[0] = left_temp if fixed_left else rod_temp
    temperature[-1] = right_temp if fixed_right else rod_temp
    temperature[1:-1] = rod_temp

    # Update the plot limits based on new temperatures
    ax1.set_ylim(temperature.min()-max(2, temperature.min()*0.1), temperature.max()*1.1)
    thermal_map.set_clim(vmin=temperature.min()-1, vmax=temperature.max()+1)

    alpha = materials[radio_mat.value_selected] * 10**-6
    r = alpha * dt / (dx * dx)
   

    # Reconstruct the matrix A based on the new boundary conditions
    A = construct_matrix()

def on_fix(event):
    if check_left.get_status()[0]:
        text_box_left.set_active(True)
    else:
        text_box_left.set_active(False)
        text_box_left.set_val('0.0')

    if check_right.get_status()[0]:
        text_box_right.set_active(True)
    else:
        text_box_right.set_active(False)
        text_box_right.set_val('0.0')

animation = FuncAnimation(fig, update, frames=200, interval=1000/FPS, blit=False)

start_button.on_clicked(on_start)
check_left.on_clicked(on_fix)
check_right.on_clicked(on_fix)

plt.show()