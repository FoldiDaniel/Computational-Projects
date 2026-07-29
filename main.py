from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button, Slider, TextBox
import matplotlib.cm as cm
import matplotlib.colors as mcolors

N = 10  # Default number of bodies in the simulation
SOFTENING = 0.15  # Softening factor to avoid huge jumps in acceleration when bodies are very close
MAX_HISTORY_LENGTH = 500  # Maximum number of positions to keep in history for drawing orbits

plt.style.use('dark_background')
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
        self.position_history: deque[Vector] = deque([self.position], maxlen=MAX_HISTORY_LENGTH)
        self.color = "white" # Will be set during generation

    def update(self, dt: float):
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
        self.position_history.append(self.position)

    def reset(self):
        self.position = self.initial_position
        self.velocity = self.initial_velocity
        self.acceleration = Vector(0, 0)
        self.position_history = deque([self.position], maxlen=500)

    def get_size(self):
        return self.mass * 8  # Scale factor for visualization




def update_accelerations(bodies: list[Body]):
    for i in range(len(bodies)):
        bodies[i].acceleration = Vector(0, 0)  # Reset acceleration
    for i in range(len(bodies)):
        for j in range(i+1, len(bodies)):
            r_vector = bodies[j].position - bodies[i].position
            distance = r_vector.magnitude()
            if distance > 0:
                force_magnitude = (bodies[i].mass * bodies[j].mass) / (distance ** 2 + SOFTENING ** 2)
                force_direction = r_vector.normalize()
                force = force_direction * force_magnitude
                bodies[i].acceleration += (force / bodies[i].mass)
                bodies[j].acceleration -= (force / bodies[j].mass)  # Newton's third law

def update_positions(bodies: list[Body], dt: float):
    for body in bodies:
        body.update(dt)


bodies = []
focused_body: Body = None
orbit_plots = []

cmap = cm.get_cmap('plasma')
norm = mcolors.Normalize(vmin=2.5, vmax=20)

# generate random bodies
def generate_random_bodies(n):
    bodies.clear()
    for i in range(n):
        mass = np.random.uniform(5, 20)
        position = Vector(np.random.uniform(-50, 50), np.random.uniform(-50, 50))
        # Set initial velocity to create a circular orbit around the origin
        velocity = Vector(-position.y * 0.04, position.x * 0.04) 
        acceleration = Vector(0, 0)
        body = Body(mass, position, velocity, acceleration)
        body.color = cmap(norm(mass))
        bodies.append(body)

def generate_orbit_plots():
    for plot in orbit_plots:
        plot.remove()  # Remove the old plot from the axes
    orbit_plots.clear()
    for body in bodies:
        plot, = ax.plot([], [], color=body.color, alpha=0.45, linewidth=1.5, zorder=2)
        orbit_plots.append(plot)

generate_random_bodies(N)

fig, ax = plt.subplots(facecolor='#0f172a')

# customize the layout 
# plt.subplots_adjust(bottom=0.2)
ax.set_facecolor('#0f172a')
ax.axes.set_axis_off() 
fig.subplots_adjust(bottom=0.25) # room for ui elements


generate_orbit_plots()

initial_x = [body.position.x for body in bodies]
initial_y = [body.position.y for body in bodies]

sizes = [body.get_size() for body in bodies]
colors = [body.color for body in bodies]

# Layer 1: The Glow (Large, highly transparent)
glow_scatter = ax.scatter(initial_x, initial_y, s=[s*6 for s in sizes], c=colors, alpha=0.15, zorder=3, edgecolors='none')
# Layer 2: The Core (Small, solid)
body_scatter = ax.scatter(initial_x, initial_y, s=sizes, c=colors, zorder=4, edgecolors='white', linewidths=0.5)

arrow_an = ax.annotate("", xy=(0, 0), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color='#38bdf8', lw=2), visible=False, zorder=10)
info_an = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points", fontsize=9, color="#f8fafc", 
                      bbox=dict(boxstyle="round,pad=0.4", fc="#1e293b", ec="#334155", alpha=0.8), visible=False, zorder=10)


ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
fig.suptitle("N-Body Simulation", color="#f8fafc", fontsize=14, fontweight='bold', y=0.95)
# ax.set_title("N-Body Simulation")

def update_annotation():
    if focused_body is not None:
        arrow_an.set_position((focused_body.position.x, focused_body.position.y))
        mag= focused_body.acceleration.magnitude()

        visual_length = 25*(mag/(mag + 0.04))  # Scaling: max * (mag/(mag + k)) to keep it bounded
        acc_dir = focused_body.acceleration.normalize()
        arrow_an.xy = (
            focused_body.position.x + (acc_dir.x * visual_length), 
            focused_body.position.y + (acc_dir.y * visual_length)
        )
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

ax_n_box = plt.axes([0.15, 0.03, 0.1, 0.04])
n_textbox = TextBox(ax_n_box, 'Num Bodies (N): ', initial=str(N), color='#1e293b', hovercolor='#334155')
n_textbox.label.set_color("#181b21")
n_textbox.label.set_fontweight('bold')
n_textbox.text_disp.set_color('#a78bfa')
n_textbox.text_disp.set_fontweight('bold')

ax_slider = plt.axes([0.15, 0.11, 0.7, 0.02], facecolor='#1e293b')
dt_slider = Slider(
    ax=ax_slider, label='Time Step (dt)', valmin=0.01, valmax=1, valstep=0.01, valinit=0.1,
    valfmt='%1.2f', color='#3b82f6', initcolor='none'
)

# Customize text colors to match a dark theme
dt_slider.label.set_color('#94a3b8')
dt_slider.valtext.set_color('#38bdf8')
dt_slider.valtext.set_fontweight('bold')

ax_new = plt.axes([0.30, 0.03, 0.1, 0.04])
ax_pause = plt.axes([0.45, 0.03, 0.1, 0.04])
ax_restart = plt.axes([0.60, 0.03, 0.1, 0.04])
ax_exit = plt.axes([0.75, 0.03, 0.1, 0.04])

btn_new = Button(ax_new, 'Generate', color='#1e293b', hovercolor='#334155')
btn_pause = Button(ax_pause, 'Pause', color='#1e293b', hovercolor='#334155')
btn_restart = Button(ax_restart, 'Restart', color='#1e293b', hovercolor='#334155')
btn_exit = Button(ax_exit, 'Exit', color='#7f1d1d', hovercolor='#991b1b')

for btn in [btn_new, btn_pause, btn_restart, btn_exit]:
    btn.label.set_color('#f8fafc')
    btn.label.set_fontweight('bold')

def update(frame):
    current_dt = dt_slider.val  # Adjust time step based on slider value
    update_accelerations(bodies)
    update_positions(bodies, current_dt)

    coords = [[body.position.x, body.position.y] for body in bodies]
    body_scatter.set_offsets(coords)
    glow_scatter.set_offsets(coords)

    for i, orbit_plot in enumerate(orbit_plots):
        orbit_plot.set_data([v.x for v in bodies[i].position_history], [v.y for v in bodies[i].position_history])

    update_annotation()
    

    return  *orbit_plots, body_scatter, glow_scatter, arrow_an, info_an



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
    global is_paused

    for body in bodies:
        body.reset()
    focused_body = None
    # Clear the visible plot data so it doesn't draw a massive straight line 
    # from the old positions back to the start!
    for orbit_plot in orbit_plots:
        orbit_plot.set_data([], [])

    if is_paused:
        toggle_pause(event)
    else:
        fig.canvas.draw_idle()

def new_start(event):
    global bodies, orbit_plots

    try:
        # Try to convert user input to an integer
        n_requested = int(n_textbox.text)
    except ValueError:
        # If they typed letters or left it blank, default to 10
        n_requested = 10 

    # Ensure the number of bodies is within a reasonable range
    n_requested = max(2, min(n_requested, 200))
    n_textbox.set_val(str(n_requested))
    
    generate_random_bodies(n_requested)

    generate_orbit_plots()  # Regenerate orbit plots for the new bodies

    new_sizes = [body.get_size() for body in bodies]
    new_colors = [body.color for body in bodies]

    body_scatter.set_sizes(new_sizes)
    body_scatter.set_color(new_colors)
    glow_scatter.set_sizes([s*6 for s in new_sizes])
    glow_scatter.set_color(new_colors)

    for i, body in enumerate(bodies):
        orbit_plots[i].set_color(body.color)

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
        
def exit_app(event):
    plt.close('all')


# Bind the button clicks to our functions
btn_pause.on_clicked(toggle_pause)
btn_restart.on_clicked(restart)
btn_new.on_clicked(new_start)
btn_exit.on_clicked(exit_app)
fig.canvas.mpl_connect('button_press_event', on_click)

try:
    mng = plt.get_current_fig_manager()
    mng.full_screen_toggle()
except:
    pass # Fails if full screen is not supported

plt.show()

