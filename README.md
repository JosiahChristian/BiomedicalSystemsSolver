\# CardioFluidSolver: Finite-Difference Hemodynamic Engine



A computational biomedical simulation framework implementing numerical finite-difference schemes. This project models fluid velocity distribution profiles and viscous drag forces across complex mammalian arterial grids.



\*\*Targeted for biophysics research\*\*



\## 🫀 Mathematical Framework



The simulation engine models fluid dynamics via one-dimensional simplifications of the Navier-Stokes velocity derivations. The system tracks momentum transport and friction drag losses across discrete arterial spatial nodes:



$$\\rho \\left( \\frac{\\partial v}{\\partial t} \\right) = \\mu \\left( \\frac{\\partial^2 v}{\\partial x^2} \\right)$$



Where:

\* $\\rho$ = Blood fluid density ($1.06 \\text{ g/cm}^3$)

\* $\\mu$ = Dynamic blood viscosity ($0.035 \\text{ Poise}$)

\* $\\frac{\\partial^2 v}{\\partial x^2}$ = Second-order spatial diffusion velocity matrix gradients



\## 🚀 Local Deployment Lifecycle



\### Prerequisites

\* Python 3.10+

\* NumPy



\### Execution

Run the transient explicit fluid state stepper calculation loop inside your terminal workspace:

```bash

python hemodynamic\_solver.py

```



\## 🛠️ Portfolio Mapping

This asset completes a multi-domain research engineering profile matrix, establishing core computational competencies in numerical partial differential equation (PDE) solving, discrete mathematical modeling, and safety-critical bio-physical simulations.



