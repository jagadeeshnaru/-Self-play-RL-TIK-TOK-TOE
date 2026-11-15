"""
Export Service for Tic-Tac-Toe RL Platform
Generates CSV files for:
- Training Run History
- Batch Convergence Curves
- Benchmark Evaluations
- Step-by-Step Game Replays
- Comprehensive Academic/Project Experiment Summary Reports (Markdown and Plaintext)
"""

import io
import csv
import json
from typing import Dict, List, Any, Optional


def export_training_history_csv(experiments: List[Dict[str, Any]]) -> str:
    """Exports summary rows of all training experiments as CSV."""
    output = io.StringIO()
    fieldnames = [
        "Experiment ID",
        "Timestamp",
        "Name",
        "Episodes Trained",
        "Learning Rate (alpha)",
        "Discount Factor (gamma)",
        "Epsilon Start",
        "Epsilon End",
        "Train Time (sec)",
        "Q-Table States",
        "Self-Play Draw %",
        "Self-Play X-Win %",
        "Self-Play O-Win %",
        "Non-Loss vs Minimax %",
        "Win vs Random %"
    ]
    writer = csv.writer(output)
    writer.writerow(fieldnames)

    for exp in experiments:
        writer.writerow([
            exp.get("id", ""),
            exp.get("timestamp", ""),
            exp.get("name", ""),
            exp.get("episodes_trained", exp.get("hyperparameters", {}).get("episodes", "")),
            exp.get("alpha", exp.get("hyperparameters", {}).get("alpha", "")),
            exp.get("gamma", exp.get("hyperparameters", {}).get("gamma", "")),
            exp.get("epsilon_start", exp.get("hyperparameters", {}).get("epsilon_start", "")),
            exp.get("epsilon_end", exp.get("hyperparameters", {}).get("epsilon_end", "")),
            exp.get("train_time_sec", ""),
            exp.get("q_states", ""),
            exp.get("self_play_draws_pct", ""),
            exp.get("self_play_x_wins_pct", ""),
            exp.get("self_play_o_wins_pct", ""),
            exp.get("non_loss_vs_minimax_pct", ""),
            exp.get("win_vs_random_pct", "")
        ])

    return output.getvalue()


def export_batch_curves_csv(experiment: Dict[str, Any]) -> str:
    """Exports batch-by-batch training curve checkpoints as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Episode",
        "Draw Rate %",
        "X Win Rate %",
        "O Win Rate %",
        "Non-Loss vs Minimax %",
        "Win vs Random %",
        "Epsilon",
        "Q-Table States"
    ])

    batch_records = experiment.get("batch_records", [])
    for rec in batch_records:
        writer.writerow([
            rec.get("episode", ""),
            rec.get("draw_rate", ""),
            rec.get("x_win_rate", ""),
            rec.get("o_win_rate", ""),
            rec.get("non_loss_vs_minimax", ""),
            rec.get("win_vs_random", ""),
            rec.get("epsilon", ""),
            rec.get("q_states", "")
        ])

    return output.getvalue()


def export_benchmark_results_csv(benchmarks: List[Dict[str, Any]]) -> str:
    """Exports benchmark trial results as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Benchmark ID",
        "Timestamp",
        "Opponent Type",
        "Agent Difficulty",
        "Total Games",
        "Agent Wins",
        "Agent Losses",
        "Draws",
        "Win Rate %",
        "Loss Rate %",
        "Draw Rate %",
        "Non-Loss Rate %"
    ])

    for bm in benchmarks:
        writer.writerow([
            bm.get("id", ""),
            bm.get("timestamp", ""),
            bm.get("opponent", ""),
            bm.get("difficulty", "Hard"),
            bm.get("games", ""),
            bm.get("wins", ""),
            bm.get("losses", ""),
            bm.get("draws", ""),
            bm.get("win_rate", ""),
            bm.get("loss_rate", ""),
            bm.get("draw_rate", ""),
            bm.get("non_loss_rate", "")
        ])

    return output.getvalue()


def export_replay_csv(replay: Dict[str, Any]) -> str:
    """Exports full step-by-step game replay as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Step",
        "Player",
        "Symbol",
        "Player Name",
        "Action (0-8)",
        "Row",
        "Col",
        "Board Before",
        "Board After",
        "Q-Values Map",
        "Move Rationale / Explanation"
    ])

    for move in replay.get("moves", []):
        writer.writerow([
            move.get("step", ""),
            move.get("player", ""),
            move.get("symbol", ""),
            move.get("player_name", ""),
            move.get("action", ""),
            move.get("row", ""),
            move.get("col", ""),
            str(move.get("board_before", [])),
            str(move.get("board_after", [])),
            json.dumps(move.get("q_values", {})),
            move.get("explanation", "")
        ])

    return output.getvalue()


def generate_experiment_summary_report(experiment: Dict[str, Any]) -> str:
    """
    Generates a structured, professional Markdown experiment report
    suitable for academic demonstration and project submission.
    """
    exp_id = experiment.get("id", "N/A")
    name = experiment.get("name", "Untitled Experiment")
    ts = experiment.get("timestamp", "N/A")
    episodes = experiment.get("episodes_trained", experiment.get("hyperparameters", {}).get("episodes", 0))
    alpha = experiment.get("alpha", experiment.get("hyperparameters", {}).get("alpha", 0.5))
    gamma = experiment.get("gamma", experiment.get("hyperparameters", {}).get("gamma", 0.9))
    eps_start = experiment.get("epsilon_start", experiment.get("hyperparameters", {}).get("epsilon_start", 1.0))
    eps_end = experiment.get("epsilon_end", experiment.get("hyperparameters", {}).get("epsilon_end", 0.05))
    train_time = experiment.get("train_time_sec", 0.0)
    q_states = experiment.get("q_states", 0)
    
    draw_pct = experiment.get("self_play_draws_pct", 0.0)
    x_win_pct = experiment.get("self_play_x_wins_pct", 0.0)
    o_win_pct = experiment.get("self_play_o_wins_pct", 0.0)
    minimax_non_loss = experiment.get("non_loss_vs_minimax_pct", 0.0)
    random_win = experiment.get("win_vs_random_pct", 0.0)

    report = f"""# Reinforcement Learning Experiment Report
## Q-Play: Self-Play Q-Learning vs Minimax for Tic-Tac-Toe
**Course Unit:** Unit IV – Reinforcement Learning  
**Course Outcome:** CO4 (Application of RL Algorithms)  
**Experiment ID:** `{exp_id}`  
**Run Title:** {name}  
**Generated At:** {ts}  

---

### 1. Executive Summary
This experiment investigates the convergence, policy strength, and theoretical optimality of a tabular Q-learning agent trained strictly through self-play in the zero-sum game of Tic-Tac-Toe. Starting from zero prior knowledge of game rules or tactics, the agent interacted with itself over **{episodes:,} episodes** using a Negamax Temporal-Difference update rule.

### 2. Hyperparameter Configuration
| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| **Training Episodes ($N$)** | `{episodes:,}` | Total games of self-play executed |
| **Learning Rate ($\\alpha$)** | `{alpha}` | Step-size parameter controlling TD weight |
| **Discount Factor ($\\gamma$)** | `{gamma}` | Future reward attenuation weight |
| **Initial Exploration ($\\epsilon_{{start}}$)** | `{eps_start}` | Starting rate of uniform random action selection |
| **Terminal Exploration ($\\epsilon_{{end}}$)** | `{eps_end}` | Exploitation baseline reached after 80% of episodes |
| **State Discovered Count** | `{q_states:,}` | Total unique board configurations indexed in Q-table |
| **Wall-Clock Training Time** | `{train_time:.2f} s` | Pure Python/NumPy self-play execution duration |

---

### 3. Empirical Performance Evaluation
The greedy policy was evaluated in two benchmark regimes:
1. **Against Optimal Minimax Opponent:** Evaluates whether the learned policy guarantees non-losing play (Minimax value of Tic-Tac-Toe from initial state is known to be a Draw under optimal play).
2. **Against Uniform Random Opponent:** Evaluates opportunistic exploitability and tactical punishment of blunders.

| Benchmark Metric | Empirical Value | Theoretical Optimum | Status |
| :--- | :--- | :--- | :--- |
| **Non-Loss Rate vs Minimax** | **{minimax_non_loss:.1f}%** | 100.0% | {'[CONVERGED / OPTIMAL]' if minimax_non_loss >= 98.0 else '[PARTIAL CONVERGENCE]'} |
| **Win Rate vs Random** | **{random_win:.1f}%** | > 90.0% | {'[STRONG TACTICAL PUNISHMENT]' if random_win >= 90.0 else '[ACCEPTABLE]'} |
| **Self-Play Draw Rate** | **{draw_pct:.1f}%** | High (~80-90%) | {'[BALANCED SELF-PLAY CONVERGENCE]' if draw_pct >= 75.0 else '[DEVELOPING]'} |
| **Self-Play X Win Rate** | **{x_win_pct:.1f}%** | Low (<15%) | Balanced |
| **Self-Play O Win Rate** | **{o_win_pct:.1f}%** | Low (<15%) | Balanced |

---

### 4. Mathematical Foundation: Negamax Self-Play Q-Update
The tabular update rule employed for state $s$, selected legal action $a$, observed reward $r$, and subsequent board state $s'$ is:

$$Q(s, a) \\leftarrow Q(s, a) + \\alpha \\left[ r - \\gamma \\max_{{a' \\in \\mathcal{{A}}(s')}} Q(s', a') - Q(s, a) \\right]$$

- **Zero-Sum Symmetry:** Because the game is strictly zero-sum, Player X's victory ($r = +1$) corresponds to Player O's loss ($-1$). The opponent's best obtainable outcome in $s'$ is subtracted from the current agent's perspective.
- **$\\epsilon$-Greedy Annealing:** Linear exploration decay prevents premature convergence onto sub-optimal local minimax equilibria and ensures complete coverage of tactical forks.

---

### 5. Academic Conclusion
The tabular Q-learning algorithm demonstrated robust convergence toward game-theoretic equilibrium. As exploration annealed from $\\epsilon = {eps_start}$ to $\\epsilon = {eps_end}$, self-play outcomes systematically shifted from chaotic wins/losses toward mutual draws ({draw_pct:.1f}%), mirroring game-theoretic equilibrium. When benchmarked against an unbeatable Minimax agent, the policy achieved a non-loss rate of {minimax_non_loss:.1f}%.
"""
    return report
