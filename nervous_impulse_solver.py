import numpy as np

print("===============================================================")
print("     ODU CPS NEURO-COMPUTATIONAL ELECTRICAL IMPULSE ENGINE     ")
print("===============================================================")
print("Initializing Synaptic Action Potential Propagation Loop...\n")

# Simulation domain: modeling a nerve axon split into 30 space segments
num_nodes = 30
axon_length_mm = 5.0
dx = axon_length_mm / (num_nodes - 1)

# Neural membrane electrical parameters
resting_potential_mv = -70.0
peak_action_potential_mv = 40.0
membrane_resistance = 1.5   # kOhm * cm
membrane_capacitance = 1.0  # uF / cm^2

# Initialize neural voltage matrix (all resting at -70mV)
voltages = np.full(num_nodes, resting_potential_mv)

# Trigger a continuous initial electrical impulse stimulus at the first synapse node (Inlet)
voltages[0] = peak_action_potential_mv

time_steps = 600
dt = 0.002  # 2ms calculation slices

print(f"Simulating action potential conduction across {num_nodes} spatial nodes.")
print("\nCycle  |  Synapse Input  |  Mid-Axon Channel (mV)  |  Nerve Output")
print("-------------------------------------------------------------------")

# Computational solver loop modeling electrical propagation diffusion equations
for step in range(time_steps):
    v_old = voltages.copy()
    
    for i in range(1, num_nodes - 1):
        # Calculate localized axial current diffusion across adjacent nerve spaces
        axial_current = (v_old[i+1] - 2*v_old[i] + v_old[i-1]) / (dx**2)
        
        # Calculate active voltage leak back to resting state baseline values
        membrane_leak = -(v_old[i] - resting_potential_mv) / (membrane_resistance * membrane_capacitance)
        
        # Explicit Euler numerical integration update register
        voltages[i] += (axial_current + membrane_leak) * dt

    if step % 120 == 0:
        print(f"{step:03d}    |     {voltages[0]:.2f} mV    |         {voltages[num_nodes//2]:.4f} mV        |    {voltages[-1]:.4f} mV")

print("-------------------------------------------------------------------")
print("NEUROLOGICAL IMPULSE SIMULATION LOGS COMPLETE.")
print(f"Final Signal Level Arriving at Terminus Node: {voltages[-2]:.4f} mV")
print("===============================================================")
