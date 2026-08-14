import numpy as np

print("===============================================================")
print("     COMPUTATIONAL BIOMEDICAL FLUID SOLVER CHASSIS        ")
print("===============================================================")
print("Initializing Hemodynamic Finite-Difference Solver Loop...\n")

# Simulation domain: modeling a 10cm segment of an artery split into 20 discrete nodes
artery_length_cm = 10.0
num_nodes = 20
dx = artery_length_cm / (num_nodes - 1)

# Blood physical fluid properties
blood_viscosity = 0.035  # Poise (g/cm*s)
blood_density = 1.06     # g/cm^3

# Initialize simulation velocity array arrays across all nodes (cm/s)
velocities = np.zeros(num_nodes)
# Set boundary condition: systolic blood pumping injection speed at the arterial inlet (node 0)
velocities[0] = 30.0  # 30 cm/s typical peak systolic inflow velocity

time_steps = 500
dt = 0.001  # 1ms time slices to preserve mathematical stability bounds

print(f"Simulating fluid progression over {time_steps} cycles across a {artery_length_cm}cm vascular grid.")
print("\nCycle  |  Inlet (cm/s)  |  Midpoint Vessel (cm/s)  |  Outlet (cm/s)")
print("-------------------------------------------------------------------")

# Discrete approximation solver loop tracking fluid momentum translation
for step in range(time_steps):
    # Create a backup matrix copy to preserve states during calculations
    v_old = velocities.copy()
    
    for i in range(1, num_nodes - 1):
        # Viscous diffusion matrix calculations (Simulating friction losses against vessel walls)
        viscous_drag = blood_viscosity * (v_old[i+1] - 2*v_old[i] + v_old[i-1]) / (dx**2)
        
        # Update fluid velocities register array using explicit Euler stepping equations
        velocities[i] += (viscous_drag / blood_density) * dt

    if step % 100 == 0:
        print(f"{step:03d}    |     {velocities[0]:.2f}      |          {velocities[num_nodes//2]:.4f}          |     {velocities[-1]:.4f}")

print("-------------------------------------------------------------------")
print("HEMODYNAMIC FLUID SOLVER LIFE-CYCLE LIFECYCLE COMPLETE.")
print(f"Final Mid-Vessel Steady State Flow Speed Output: {velocities[num_nodes//2]:.4f} cm/s")
print("Biomedical Simulation Model Logs Registered Successfully.")
