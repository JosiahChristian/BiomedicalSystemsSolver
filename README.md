# BiomedicalSystemsSolver: Neuro-Computational & Hemodynamic Engines

A multi-domain computational biophysics simulation suite implementing discrete numerical finite-difference equations. This project dual-models transient biological signaling and physical mechanics properties across mammalian grids.

Targeted for neural and biophysics research in **Modeling and Simulation Engineering**.

## 🧠 Electrophysiology Framework (Nervous System)
The neural propagation model solves the discrete one-dimensional spatial cable differential equation. The system tracks signal conduction velocity decays and active ion leaks along an automated axon channel path:

$$C_m \frac{\partial V}{\partial t} = \frac{1}{R_a} \frac{\partial^2 V}{\partial x^2} - I_{leak}$$

Where:
* $C_m$ = Membrane capacitance ($1.0 \ \mu\text{F/cm}^2$)
* $R_a$ = Axial resistance matrix parameters
* $I_{leak}$ = Active voltage leakage tracking index relative to a $-70\text{mV}$ resting baseline potential

*   **Engine Script:** `nervous_impulse_solver.py`
*   **Mathematical Scheme:** Explicit Euler transient voltage integrator loop tracking signal propagation across 30 space coordinates.

## 🫀 Hemodynamic Framework (Cardiovascular System)
The blood flow model maps transient fluid velocities via one-dimensional simplifications of the Navier-Stokes derivations, calculating viscous diffusion friction losses against vessel walls:

$$\rho \left( \frac{\partial v}{\partial t} \right) = \mu \left( \frac{\partial^2 v}{\partial x^2} \right)$$

*   **Engine Script:** `hemodynamic_solver.py`
*   **Mathematical Scheme:** Second-order spatial finite-difference diffusion approximation matrix tracking momentum profiles across 20 vascular nodes.

## 🚀 Local Deployment Lifecycle

### Prerequisites
* Python 3.10+
* NumPy
* Matplotlib

### Execution
Run the data science visualization module locally to calculate both engines and export your side-by-side subplot panel matrix graphic:
```bash
python generate_biomed_plots.py
```

## 📈 Simulation Analytics Visualization
![Biomedical Matrix Profile](biomedical_simulation_matrix.png)
