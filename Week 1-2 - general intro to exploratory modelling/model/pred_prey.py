import numpy as np


def PredPrey(prey_birth_rate=0.025, predation_rate=0.0015, predator_efficiency=0.002,
             predator_loss_rate=0.06, initial_prey=50, initial_predators=20, dt=0.25, final_time=365, reps=1):
    # Initial values
    predators, prey, sim_time = [np.zeros((reps, int(final_time / dt) + 1)) for _ in range(3)]

    for r in range(reps):
        predators[r, 0] = initial_predators
        prey[r, 0] = initial_prey

        # Calculate the time series
        for t in range(0, sim_time.shape[1] - 1):
            dx = (prey_birth_rate * prey[r, t]) - (predation_rate * prey[r, t] * predators[r, t])
            dy = (predator_efficiency * predators[r, t] * prey[r, t]) - (predator_loss_rate * predators[r, t])

            prey[r, t + 1] = max(prey[r, t] + dx * dt, 0)
            predators[r, t + 1] = max(predators[r, t] + dy * dt, 0)
            sim_time[r, t + 1] = (t + 1) * dt

    # Return outcomes
    return {'TIME': sim_time,
            'predators': predators,
            'prey': prey}
