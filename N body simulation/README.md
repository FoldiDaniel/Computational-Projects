# N-Body Gravitational Physics Simulator

Interactive N-body physics simulator built in Python. 

This project was developed as a foundational exercise in **Computational Engineering**, focusing on numerical integration, object-oriented physical modeling, and dynamic data visualization. It models the gravitational forces and orbital mechanics of celestial bodies in a 2D space.

<img width="2558" height="1438" alt="orbits" src="https://github.com/user-attachments/assets/ce6cbcd0-05af-4bfc-9309-ede2f8f3efa4" />


## Features
* **Custom Physics Engine:** Built entirely from scratch without relying on external physics libraries. 
* **Gravitational Softening:** Implements a softening parameter ($\epsilon$) to resolve the asymptotic force spikes that occur during near-collisions, ensuring stable simulations.
* **Interactive UI:** Includes full-screen Matplotlib widgets allowing users to pause, restart, adjust the time step ($\Delta t$), and dynamically spawn new bodies up to $N=200$.
* **Live Telemetry:** Clicking on any celestial body reveals real-time telemetry, including mass, velocity vectors, and a dynamically scaling acceleration vector arrow.
* **Deep Space Aesthetics:** Features glowing celestial bodies, dynamic color mapping based on mass, and fading orbital trails managed by an optimized `deque` memory buffer.



<img width="311" height="157" alt="image" src="https://github.com/user-attachments/assets/477fba37-5ed0-4496-a02b-e683960a83a4" />

Live telemetry

## Mathematical Foundation
The simulation calculates the gravitational pull of every body on every other body ($O(N^2)$ complexity) using Newton's Law of Universal Gravitation:

$$F = G \frac{m_1 m_2}{r^2 + \epsilon^2}$$

The forces are resolved into vectors, converted into acceleration, and integrated over time using a numerical Euler method to update positions and velocities frame-by-frame. 
