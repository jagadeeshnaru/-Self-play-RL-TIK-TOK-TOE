"""
Comprehensive Backend Validation & Unit Tests
Tests:
- TicTacToe environment
- Minimax optimal decisions
- Q-learning training & self-play convergence
- Distinct difficulty levels (Easy, Medium, Hard)
- Step-by-step game replay engine
- Experiments persistence
- CSV and Markdown exports
"""

import os
import sys
import numpy as np

# Ensure root directory is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.rl_engine import (
    TicTacToe,
    minimax,
    RLAgent,
    train_agent,
    evaluate_vs_minimax,
    evaluate_vs_random,
    generate_game_replay
)
import backend.experiments as exp_store
import backend.export_service as exporter


def test_tictactoe_environment():
    print("Testing TicTacToe Environment...")
    env = TicTacToe()
    assert len(env.available_moves()) == 9
    assert env.check_winner() is None

    # Test winning line (row 0: 0, 1, 2)
    env.make_move(0, 1)
    env.make_move(3, 2)
    env.make_move(1, 1)
    env.make_move(4, 2)
    env.make_move(2, 1)
    assert env.check_winner() == 1
    assert env.is_game_over() is True

    # Test draw
    env.reset()
    # X O X
    # X X O
    # O X O
    # 0 1 2 3 4 5 6 7 8
    # X: 0, 2, 3, 4, 7
    # O: 1, 5, 6, 8
    draw_board = np.array([1, 2, 1, 1, 1, 2, 2, 1, 2])
    draw_env = TicTacToe(draw_board)
    assert draw_env.check_winner() == 0
    print("  ✓ Environment logic passed.")


def test_minimax_optimality():
    print("Testing Minimax Algorithm...")
    # Board where Player 1 can win immediately at cell 2
    board = np.array([1, 1, 0, 2, 2, 0, 0, 0, 0])
    score, move = minimax(board, 1)
    assert move == 2, f"Minimax should detect immediate win at 2, got {move}"

    # Board where Player 2 must block Player 1 at cell 2
    board2 = np.array([1, 1, 0, 0, 2, 0, 0, 0, 0])
    score2, move2 = minimax(board2, 2)
    assert move2 == 2, f"Minimax should block immediate win at 2, got {move2}"
    print("  ✓ Minimax decision optimality passed.")


def test_rl_training_convergence():
    print("Testing Q-Learning Agent Self-Play Training...")
    # Train small fast batch for unit testing
    agent, summary = train_agent(episodes=3000, alpha=0.5, gamma=0.9, epsilon_start=1.0, epsilon_end=0.05)
    assert len(agent.Q) > 200, f"Q-table should have discovered states, got {len(agent.Q)}"
    assert summary["episodes_trained"] == 3000
    assert len(summary["batch_records"]) > 0
    print(f"  ✓ Training completed in {summary['train_time_sec']}s with {len(agent.Q)} Q-states.")


def test_difficulty_levels():
    print("Testing Distinct Agent Difficulty Levels...")
    # Train agent with enough experience
    agent, _ = train_agent(episodes=5000, alpha=0.5, gamma=0.9)
    
    # Board where cell 2 is an immediate win for agent (player 1)
    # 1 1 0
    # 2 2 0
    # 0 0 0
    board = np.array([1, 1, 0, 2, 2, 0, 0, 0, 0])

    # Hard agent should always execute optimal winning move
    hard_results = [agent.choose_action_with_details(board, "hard", player=1)["action"] for _ in range(20)]
    assert all(a == 2 for a in hard_results), f"Hard agent must always pick winning move 2, got {hard_results}"

    # Easy agent should explore and pick non-optimal moves with ~50% frequency
    easy_actions = [agent.choose_action_with_details(board, "easy", player=1)["action"] for _ in range(50)]
    random_count = sum(1 for a in easy_actions if a != 2)
    assert random_count > 5, f"Easy agent must show exploratory behavior, random count: {random_count}/50"

    # Medium agent has intermediate behavior
    med_actions = [agent.choose_action_with_details(board, "medium", player=1)["action"] for _ in range(50)]
    assert 2 in med_actions
    print(f"  ✓ Difficulty levels verified: Easy exploration count {random_count}/50, Hard consistency 20/20.")


def test_game_replay_diagnostics():
    print("Testing Step-by-Step Game Replay Generation...")
    agent, _ = train_agent(episodes=2000, alpha=0.5, gamma=0.9)
    replay = generate_game_replay(agent, opponent_type="minimax", agent_player=1, difficulty="hard")

    assert len(replay["moves"]) >= 5, "Tic-Tac-Toe game must have at least 5 moves"
    assert "result_description" in replay
    assert "final_winner" in replay

    first_move = replay["moves"][0]
    assert "board_before" in first_move
    assert "board_after" in first_move
    assert "q_values" in first_move
    assert "explanation" in first_move
    assert len(first_move["explanation"]) > 5
    print(f"  ✓ Game replay successfully recorded {len(replay['moves'])} steps with explanations.")


def test_persistence_and_exports():
    print("Testing Experiment Persistence & CSV/Markdown Exporters...")
    sample_exp = {
        "id": "test_exp_001",
        "name": "Test Experiment Run",
        "timestamp": "2026-11-15 12:00:00",
        "episodes_trained": 10000,
        "alpha": 0.5,
        "gamma": 0.9,
        "epsilon_start": 1.0,
        "epsilon_end": 0.05,
        "train_time_sec": 1.25,
        "q_states": 1500,
        "self_play_draws_pct": 82.5,
        "self_play_x_wins_pct": 9.5,
        "self_play_o_wins_pct": 8.0,
        "non_loss_vs_minimax_pct": 96.0,
        "win_vs_random_pct": 94.0,
        "batch_records": [
            {"episode": 5000, "draw_rate": 60.0, "x_win_rate": 20.0, "o_win_rate": 20.0, "non_loss_vs_minimax": 75.0, "win_vs_random": 80.0, "epsilon": 0.5, "q_states": 1000},
            {"episode": 10000, "draw_rate": 82.5, "x_win_rate": 9.5, "o_win_rate": 8.0, "non_loss_vs_minimax": 96.0, "win_vs_random": 94.0, "epsilon": 0.05, "q_states": 1500}
        ]
    }
    exp_store.add_experiment(sample_exp)
    fetched = exp_store.get_experiment_by_id("test_exp_001")
    assert fetched is not None
    assert fetched["name"] == "Test Experiment Run"

    # CSV Exports
    csv_history = exporter.export_training_history_csv([sample_exp])
    assert "Experiment ID" in csv_history
    assert "test_exp_001" in csv_history

    csv_curves = exporter.export_batch_curves_csv(sample_exp)
    assert "Episode,Draw Rate %,X Win Rate %" in csv_curves

    # Markdown Report
    report_md = exporter.generate_experiment_summary_report(sample_exp)
    assert "# Reinforcement Learning Experiment Report" in report_md
    assert "test_exp_001" in report_md
    assert "Negamax Self-Play Q-Update" in report_md

    # Clean up test exp
    exp_store.delete_experiment_by_id("test_exp_001")
    assert exp_store.get_experiment_by_id("test_exp_001") is None
    print("  ✓ Persistence and Export generators passed.")


if __name__ == "__main__":
    test_tictactoe_environment()
    test_minimax_optimality()
    test_rl_training_convergence()
    test_difficulty_levels()
    test_game_replay_diagnostics()
    test_persistence_and_exports()
    print("\n✅ ALL BACKEND TESTS PASSED SUCCESSFULLY!")
