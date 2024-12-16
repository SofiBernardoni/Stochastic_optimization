import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Objective function to minimize
def objective_function(x):
    return x**2 + 2*x + 1

# PSO parameters
num_particles = 10
num_iterations = 30
inertia_weight = 0.7
cognitive_constant = 1.5
social_constant = 1.5

# Particle initialization
np.random.seed(42)
particles = np.random.uniform(-10, 10, num_particles)  # Particle positions
velocities = np.random.uniform(-1, 1, num_particles)   # Particle velocities
personal_best_positions = particles.copy()  # Best positions of each particle
personal_best_scores = objective_function(personal_best_positions)  # Best scores
global_best_position = personal_best_positions[np.argmin(personal_best_scores)]  # Global best

# PSO Algorithm
positions_history = []  # Store positions to visualize later

for t in range(num_iterations):
    # Update velocities and positions
    for i in range(num_particles):
        r1 = np.random.random()
        r2 = np.random.random()

        # Velocity update equation
        velocities[i] = (inertia_weight * velocities[i] +
                         cognitive_constant * r1 * (personal_best_positions[i] - particles[i]) +
                         social_constant * r2 * (global_best_position - particles[i]))

        # Position update equation
        particles[i] += velocities[i]

        # Evaluate new score
        score = objective_function(particles[i])

        # Update personal best if current score is better
        if score < personal_best_scores[i]:
            personal_best_scores[i] = score
            personal_best_positions[i] = particles[i]

    # Update global best
    global_best_position = personal_best_positions[np.argmin(personal_best_scores)]
    
    # Store positions for visualization
    positions_history.append(particles.copy())

    # Print iteration results
    print(f"Iteration {t+1}, Global Best Position: {global_best_position}, Best Score: {objective_function(global_best_position)}")

# Visualization
fig, ax = plt.subplots()

x = np.linspace(-10, 10, 400)
y = objective_function(x)

ax.plot(x, y, 'r', label='Objective Function')
particle_dots, = ax.plot([], [], 'bo', label='Particles')

# Add iteration counter
iteration_text = ax.text(0.05, 0.9, '', transform=ax.transAxes, fontsize=12, color='blue')

def update_plot(frame):
    # Update particle positions
    particle_dots.set_data(positions_history[frame], objective_function(np.array(positions_history[frame])))
    
    # Update iteration counter text
    iteration_text.set_text(f'Iteration: {frame + 1}')
    
    return particle_dots, iteration_text

ani = FuncAnimation(fig, update_plot, frames=num_iterations, interval=300)

ax.legend(loc="center right")
plt.xlabel("x")
plt.ylabel("f(x)")
plt.title("PSO Particle Movement with Iteration Counter")
plt.show()

