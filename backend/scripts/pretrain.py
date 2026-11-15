"""Pre-trains baseline experiments for immediate platform use."""
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.rl_engine import train_agent
import backend.experiments as exp_store


def main():
    print("Training 50K episode baseline...")
    t0 = time.time()
    agent50k, summary50k = train_agent(episodes=50000, alpha=0.5, gamma=0.9, epsilon_start=1.0, epsilon_end=0.05)
    summary50k["id"] = "exp_baseline_50k"
    summary50k["name"] = "Q-Play 50K Self-Play (α=0.5, γ=0.9)"
    summary50k["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    exp_store.add_experiment(summary50k)
    print(f"50K Run complete in {time.time()-t0:.2f}s! States: {len(agent50k.Q)}")

    print("Training 20K episode comparative run...")
    t1 = time.time()
    agent20k, summary20k = train_agent(episodes=20000, alpha=0.3, gamma=0.95, epsilon_start=1.0, epsilon_end=0.10)
    summary20k["id"] = "exp_baseline_20k"
    summary20k["name"] = "Comparison Run 20K (α=0.3, γ=0.95)"
    summary20k["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    exp_store.add_experiment(summary20k)
    print(f"20K Run complete in {time.time()-t1:.2f}s! States: {len(agent20k.Q)}")

    print("Pre-training complete! Saved to experiments.json")


if __name__ == "__main__":
    main()
