import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

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

class Body:
    

    def __init__(self, mass: int, position: Vector, velocity: Vector, acceleration: Vector):
        self.mass = mass
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.position_history: list[Vector] = [self.position]

    def update(self, dt: float):
        self.velocity = self.velocity + self.acceleration * dt
        self.position = self.position + self.velocity * dt
        self.position_history.append(self.position)




def update_accelerations(bodies: list[Body]):
    for i in range(len(bodies)):
        bodies[i].acceleration = Vector(0, 0)  # Reset acceleration
        for j in range(len(bodies)):
            if i != j:
                r_vector = bodies[j].position - bodies[i].position
                distance = r_vector.magnitude()
                if distance > 0:
                    force_magnitude = (bodies[i].mass * bodies[j].mass) / (distance ** 2)
                    force_direction = r_vector.normalize()
                    force = force_direction * force_magnitude
                    bodies[i].acceleration += (force / bodies[i].mass)

def update_positions(bodies: list[Body], dt: float):
    for body in bodies:
        body.update(dt)


bodies = [
    Body(1, Vector(-4, 0), Vector(0, 0), Vector(0, 0)),
    Body(1, Vector(5, 5), Vector(0, 0), Vector(0, 0)),]

fig, ax = plt.subplots()
orbit_plots = [ax.plot([], [])[0] for _ in bodies]
body_plot, = ax.plot([], [], 'bo', markersize=5)

ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_title("N-Body Simulation")


def update(frame):
    update_accelerations(bodies)
    update_positions(bodies, 0.5)

    x_data = [body.position.x for body in bodies]
    y_data = [body.position.y for body in bodies]

    body_plot.set_data(x_data, y_data)
    for i, orbit_plot in enumerate(orbit_plots):
        orbit_plot.set_data([v.x for v in bodies[i].position_history], [v.y for v in bodies[i].position_history])


    return body_plot, *orbit_plots

animation = FuncAnimation(fig, update, frames=200, interval=50, blit=True)


plt.show()

