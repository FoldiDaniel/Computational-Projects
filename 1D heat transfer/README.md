# 1D Heat Transfer Simulator: Crank-Nicolson Method

An interactive, real-time physics simulation of 1D thermal diffusion. This project solves the 1D Heat Equation Partial Differential Equation (PDE) using the **Crank-Nicolson Finite Difference Method**. 

It features a custom-built GUI that allows users to manipulate boundary conditions, material properties, and initial temperatures on the fly to observe how heat propagates through different mediums over time.

how xca

## Features

* **Numerical Solver:** Implements the unconditionally stable, second-order accurate Crank-Nicolson method, avoiding the strict stability limits of standard explicit Euler methods.
* **Dynamic Boundary Conditions:** 
  * **Dirichlet (Fixed):** Hold the ends of the rod at a constant temperature.
  * **Neumann (Insulated):** Prevent heat flux at the boundaries using mathematical "ghost nodes."
* **Real-time Visualization:** Plot interface showing both a standard 2D Cartesian temperature profile and a mapped 1D thermal color gradient.
* **Material Presets:** Can swap between materials (Copper, Steel, Glass) to see how varying thermal diffusivities ($\alpha$) affect the physical diffusion rate.

## The Mathematics

The simulation models the standard 1D Heat Equation:

$$ \frac{\partial u}{\partial t} = \alpha \frac{\partial^2 u}{\partial x^2} $$

To solve this computationally, the spatial and temporal derivatives are discretised. Instead of relying on a first-order explicit or implicit solution, this project utilizes the **Crank-Nicolson method**, which averages the forward and backward Euler methods in time:

$$ -ru_{j-1}^{n+1} + (2 + 2r)u_j^{n+1} - ru_{j+1}^{n+1} = ru_{j-1}^n + (2 - 2r)u_j^n + ru_{j+1}^n $$

Where the Grid Fourier Number ($r$) is defined by the material's thermal diffusivity ($\alpha$):
$$ r = \frac{\alpha \Delta t}{\Delta x^2} $$

### Handling Insulated Boundaries (Neumann)
When a boundary is set to "Insulated", the temperature gradient must be zero ($\frac{\partial u}{\partial x} = 0$). This is handled algorithmically by introducing a "ghost node" outside the domain (e.g., $u_{-1} = u_1$). Subbing this into the Crank-Nicolson stencil dynamically alters the tridiagonal matrix to reflect zero heat flux at the boundary:
$$ (2 + 2r)u_0^{n+1} - 2ru_1^{n+1} = (2 - 2r)u_0^n + 2ru_1^n $$
