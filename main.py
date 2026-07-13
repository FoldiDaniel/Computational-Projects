import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.widgets import Button


#TODO: add new annotatoin showing mass and acceleration of the body when clicked on.
# add slider to change speed
# change size of the bodies based on mass


DT = 0.1  # Time step
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
n = 3
bodies = []
focused_body: Body = None

# generate random bodies
for i in range(n):
    mass = np.random.uniform(1, 10)
    position = Vector(np.random.uniform(-10, 10), np.random.uniform(-10, 10))
    velocity = Vector(np.random.uniform(-1, 1), np.random.uniform(-1, 1))
    acceleration = Vector(0, 0)
    body = Body(mass, position, velocity, acceleration)
    bodies.append(body)


fig, ax = plt.subplots()

# customize the layout 
# plt.subplots_adjust(bottom=0.2)
ax.axes.set_axis_off() 


orbit_plots = [ax.plot([], [])[0] for _ in bodies]
body_plot, = ax.plot([], [], 'bo', markersize=5)
annotation = ax.annotate("", xy=(0, 0), xytext=(0, 0), color="red", arrowprops=dict(arrowstyle="->", color='red'), visible=False)
# annotation = ax.annotate("", xy=(0, 0), xytext=(10, 10), textcoords="offset points", fontsize=8, color="red", ha="left", va="bottom", arrowprops=dict(arrowstyle="->", color='red'), visible=False)


ax.set_xlim(-20, 20)
ax.set_ylim(-20, 20)
ax.set_title("N-Body Simulation")

def update_annotation():
    if focused_body is not None:
        annotation.set_position((focused_body.position.x, focused_body.position.y))
        scale = 2 / focused_body.acceleration.magnitude() if (focused_body.acceleration.magnitude() < 0.1) else 20
        annotation.xy = (focused_body.position.x + (focused_body.acceleration.x * scale), focused_body.position.y + (focused_body.acceleration.y * scale)) 
        # annotation.set_text(f"Mass: {focused_body.mass:.2f}\nAcc: ({focused_body.acceleration.x:.4f}, {focused_body.acceleration.y:.4f})")
        annotation.set_visible(True)
    else:
        annotation.set_visible(False)

def update(frame):
    update_accelerations(bodies)
    update_positions(bodies, DT)

    x_data = [body.position.x for body in bodies]
    y_data = [body.position.y for body in bodies]

    for i, orbit_plot in enumerate(orbit_plots):
        orbit_plot.set_data([v.x for v in bodies[i].position_history], [v.y for v in bodies[i].position_history])

    body_plot.set_data(x_data, y_data)
    update_annotation()
    

    return  *orbit_plots, body_plot, annotation

animation = FuncAnimation(fig, update, frames=200, interval=20, blit=True)

ax_pause = plt.axes([0.55, 0.05, 0.15, 0.075])
ax_restart = plt.axes([0.72, 0.05, 0.15, 0.075])

btn_pause = Button(ax_pause, 'Pause')
btn_restart = Button(ax_restart, 'Restart')

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
    for body in bodies:
        body.reset()
    
    # Clear the visible plot data so it doesn't draw a massive straight line 
    # from the old positions back to the start!
    for orbit_plot in orbit_plots:
        orbit_plot.set_data([], [])
    body_plot.set_data([], [])
    fig.canvas.draw_idle()


# def on_hover(event):
#     for body in bodies:
#         if event.xdata is None or event.ydata is None:
#             continue
#         if body.position.distance_to(Vector(event.xdata, event.ydata)) < 1:
#             annotation.set_position((body.position.x, body.position.y))
#             scale = 5
#             annotation.xy = (body.position.x + (body.acceleration.x * scale), body.position.y + (body.acceleration.y * scale)) 
#             annotation.set_text(f"Mass: {body.mass:.2f}\nAcc: ({body.acceleration.x:.4f}, {body.acceleration.y:.4f})")
#             annotation.set_visible(True)
#             fig.canvas.draw_idle()
#             return
#     annotation.set_visible(False)

def on_click(event):
    global focused_body
    for body in bodies:
        if event.xdata is None or event.ydata is None:
            continue
        if body.position.distance_to(Vector(event.xdata, event.ydata)) < 1:
            focused_body = body
            print(f"Focused on body with mass: {body.mass:.2f}\nand acceleration: ({body.acceleration.x:.4f}, {body.acceleration.y:.4f})")
            update_annotation()
            fig.canvas.draw_idle()
            return
        

# Bind the button clicks to our functions
btn_pause.on_clicked(toggle_pause)
btn_restart.on_clicked(restart)
fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()

