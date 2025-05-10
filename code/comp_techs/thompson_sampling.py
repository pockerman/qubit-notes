import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':

    # True conversion rates for each "arm"
    true_conversion_rates = [0.05, 0.03, 0.08]
    n_arms = len(true_conversion_rates)
    n_rounds = 1000

    # Track successes and failures for each arm
    successes = [0] * n_arms
    failures = [0] * n_arms
    rewards = []

    for _ in range(n_rounds):
        # Sample from Beta distribution for each arm
        sampled_theta = [np.random.beta(successes[i] + 1, failures[i] + 1) for i in range(n_arms)]

        # Choose the arm with the highest sampled value
        chosen_arm = np.argmax(sampled_theta)

        # Simulate reward
        reward = np.random.rand() < true_conversion_rates[chosen_arm]

        # Update successes/failures
        if reward:
            successes[chosen_arm] += 1
        else:
            failures[chosen_arm] += 1

        rewards.append(reward)

    # Plot cumulative average reward
    plt.plot(np.cumsum(rewards) / (np.arange(n_rounds) + 1))
    plt.xlabel("Round")
    plt.ylabel("Cumulative Average Reward")
    plt.title("Thompson Sampling Performance")
    plt.grid(True)
    plt.show()
