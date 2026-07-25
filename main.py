import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button, Slider



# TODO: hide annotations when restarting

N = 5  # Number of bodies in the simulation
SOFTENING = 0.2  # Softening factor to avoid huge jumps in acceleration when bodies are very close
class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0)
        return self / mag
    
    def distance_to(self, other):
        return (self - other).magnitude()

class Body:
    

    def __init__(self, mass: int, position: Vector, velocity: Vector, acceleration: Vector):
        self.mass = mass
        self.initial_position = position
        self.position = position
        self.initial_velocity = velocity
        self.velocity = velocity
        self.acceleration = acceleration
        self.position_history: list[Vector] = [self.position]

    def update(self, dt: float):
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
        self.position_history.append(self.position)

    def reset(self):
        self.position = self.initial_position
        self.velocity = self.initial_velocity
        self.acceleration = Vector(0, 0)
        self.position_history = [self.position]

    def get_size(self):
        return self.mass * 5  # Scale factor for visualization




def update_accelerations(bodies: list[Body]):
    for i in range(len(bodies)):
        bodies[i].acceleration = Vector(0, 0)  # Reset acceleration
        for j in range(len(bodies)):
            if i != j:
                r_vector = bodies[j].position - bodies[i].position
                distance = r_vector.magnitude()
                if distance > 0:
                    force_magnitude = (bodies[i].mass * bodies[j].mass) / (distance ** 2 + SOFTENING ** 2)
                    force_direction = r_vector.normalize()
                    force = force_direction * force_magnitude
                    bodies[i].acceleration += (force / bodies[i].mass)

def update_positions(bodies: list[Body], dt: float):
    for body in bodies:
        body.update(dt)


bodies = []
focused_body: Body = None

# generate random bodies
def generate_random_bodies(n):
    bodies.clear()
    for i in range(n):
        mass = np.random.uniform(5, 20)
        position = Vector(np.random.uniform(-50, 50), np.random.uniform(-50, 50))
        velocity = Vector(np.random.uniform(-1, 1), np.random.uniform(-1, 1))
        acceleration = Vector(0, 0)
        body = Body(mass, position, velocity, acceleration)
        bodies.append(body)

generate_random_bodies(N)

fig, ax = plt.subplots()

# customize the layout 
# plt.subplots_adjust(bottom=0.2)
ax.axes.set_axis_off() 


orbit_plots = [ax.plot([], [])[0] for _ in bodies]


initial_x = [body.position.x for body in bodies]
initial_y = [body.position.y for body in bodies]
masses = [body.mass for body in bodies]

# Scale sizes (mass * 3 looks good for these numbers)
sizes = [body.get_size() for body in bodies]
body_scatter = ax.scatter(initial_x, initial_y, s=sizes, c=masses, cmap='plasma', zorder=5)

arrow_an = ax.annotate("", xy=(0, 0), xytext=(0, 0), color="red", arrowprops=dict(arrowstyle="->", color='red'), visible=False)
info_an = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points", fontsize=8, color="red", visible=False)

ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_title("N-Body Simulation")

def update_annotation():
    if focused_body is not None:
        arrow_an.set_position((focused_body.position.x, focused_body.position.y))
        mag= focused_body.acceleration.magnitude()
        scale = 5 / mag if (mag < 0.01) else (500 if mag < 0.1 else 50 / mag)
        arrow_an.xy = (focused_body.position.x + (focused_body.acceleration.x * scale), focused_body.position.y + (focused_body.acceleration.y * scale)) 
        arrow_an.set_visible(True)

        info_an.xy = (focused_body.position.x, focused_body.position.y)
        info_an.set_text(f"Mass: {focused_body.mass:.2f}\nVelocity: ({10*focused_body.velocity.x:.3f}, {10*focused_body.velocity.y:.3f})\nAcceleration: ({focused_body.acceleration.x:.3f}, {focused_body.acceleration.y:.3f})\nmag: {focused_body.acceleration.magnitude():.3f}")
        info_an.set_visible(True)
    else:
        arrow_an.set_visible(False)
        info_an.set_visible(False)

def hide_annotation():
    arrow_an.set_visible(False)
    info_an.set_visible(False)


ax_pause = plt.axes([0.55, 0.05, 0.15, 0.075])
ax_restart = plt.axes([0.72, 0.05, 0.15, 0.075])
ax_new = plt.axes([0.15, 0.05, 0.15, 0.075])

ax_slider = plt.axes([0.15, 0.15, 0.7, 0.02], facecolor='#1e293b')
dt_slider = Slider(
    ax=ax_slider,
    label='Time Step (dt)',
    valmin=0.01,
    valmax=1,
    valstep=0.01,
    valinit=0.1,
    valfmt='%1.2f s',      # Displays as "0.05 s" instead of raw floats
    color='#3b82f6',       # Blue accent color for the active bar
    initcolor='none'       # Hides the red default initial marker line
)

# Customize text colors to match a dark theme
dt_slider.label.set_color('#f8fafc')
dt_slider.valtext.set_color('#3b82f6')
dt_slider.valtext.set_fontweight('bold')



btn_pause = Button(ax_pause, 'Pause')
btn_restart = Button(ax_restart, 'Restart')
btn_new = Button(ax_new, 'New')

def update(frame):
    current_dt = dt_slider.val  # Adjust time step based on slider value
    update_accelerations(bodies)
    update_positions(bodies, current_dt)

    coords = [[body.position.x, body.position.y] for body in bodies]
    body_scatter.set_offsets(coords)

    for i, orbit_plot in enumerate(orbit_plots):
        orbit_plot.set_data([v.x for v in bodies[i].position_history], [v.y for v in bodies[i].position_history])

    update_annotation()
    

    return  *orbit_plots, body_scatter, arrow_an, info_an



animation = FuncAnimation(fig, update, frames=200, interval=50, blit=False)

is_paused = False

def toggle_pause(event):
    global is_paused
    if is_paused:
        animation.resume()  # Built-in FuncAnimation method
        btn_pause.label.set_text('Pause')
    else:
        animation.pause()   # Built-in FuncAnimation method
        btn_pause.label.set_text('Play')
    is_paused = not is_paused
    fig.canvas.draw_idle()  # Force the button text to redraw


def restart(event):
    global bodies
    global focused_body
    for body in bodies:
        body.reset()
    
    # Clear the visible plot data so it doesn't draw a massive straight line 
    # from the old positions back to the start!
    for orbit_plot in orbit_plots:
        orbit_plot.set_data([], [])
    body_scatter.set_offsets([])
    focused_body = None
    fig.canvas.draw_idle()

def new_start(event):
    global bodies
    generate_random_bodies(N)
    new_masses = [body.mass for body in bodies]
    new_sizes = [body.get_size() for body in bodies]
    body_scatter.set_sizes(new_sizes)
    body_scatter.set_array(np.array(new_masses))
    #Update the colormap limits so the colors scale correctly to the new min/max mass
    if new_masses:
        body_scatter.set_clim(vmin=min(new_masses), vmax=max(new_masses))
    restart(event)  # Reset the simulation after generating new bodies

def on_click(event):
    global focused_body
    for body in bodies:
        if event.xdata is None or event.ydata is None:
            continue
        if body.position.distance_to(Vector(event.xdata, event.ydata)) < 3:
            focused_body = body
            update_annotation()
            fig.canvas.draw_idle()
            return
        

# Bind the button clicks to our functions
btn_pause.on_clicked(toggle_pause)
btn_restart.on_clicked(restart)
btn_new.on_clicked(new_start)
fig.canvas.mpl_connect('button_press_event', on_click)

mng = plt.get_current_fig_manager()
mng .full_screen_toggle()
plt.show()

