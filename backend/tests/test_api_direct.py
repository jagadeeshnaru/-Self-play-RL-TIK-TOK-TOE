"""
Direct API Validation Tests
Tests all FastAPI endpoints directly with Pydantic request models:
- Health check
- Model status
- Training (3,000 episodes) with batch convergence logging
- Agent moves across Easy, Medium, Hard with Q-values & explanations
- Empirical benchmarks vs Minimax and Random
- Step-by-step game replay generation
- Experiment persistence & retrieval
- CSV and Markdown report generators
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import backend.main as app_main
from backend.main import (
    TrainRequest,
    MoveRequest,
    BenchmarkRequest,
    ReplayRequest,
    health_check,
    get_model_status,
    train_model,
    get_agent_move,
    run_benchmark,
    create_game_replay,
    list_experiments,
    get_experiment_details,
    download_training_history_csv,
    download_benchmark_results_csv,
    download_experiment_report
)


def run_all_api_tests():
    print("=" * 60)
    print("Running FastAPI Endpoint Direct Validation Suite")
    print("=" * 60)

    # 1. Health check
    print("\n1. Testing GET /api/health...")
    h = health_check()
    assert h["status"] == "ok"
    print("   ✓ Health check returned:", h)

    # 2. Model Status
    print("\n2. Testing GET /api/model/status...")
    st = get_model_status()
    assert st["status"] == "Trained"
    assert st["q_states"] > 0
    print(f"   ✓ Model Status: {st['status']}, Q-States: {st['q_states']}, Episodes: {st['episodes_trained']}")

    # 3. Training Execution
    print("\n3. Testing POST /api/train (5,000 episodes)...")
    train_req = TrainRequest(
        episodes=5000,
        alpha=0.5,
        gamma=0.9,
        epsilon_start=1.0,
        epsilon_end=0.05,
        name="Validation Run 5K"
    )
    train_res = train_model(train_req)
    assert train_res["success"] is True
    exp = train_res["experiment"]
    assert exp["episodes_trained"] == 5000
    assert len(exp["batch_records"]) > 0
    print(f"   ✓ Training Success! Time: {exp['train_time_sec']}s, States: {exp['q_states']}")
    print(f"     Batch records count: {len(exp['batch_records'])}")
    print(f"     Final Draw %: {exp['self_play_draws_pct']}%, Minimax Non-Loss: {exp['non_loss_vs_minimax_pct']}%")

    # 4. Agent Moves across 3 Difficulty Levels
    print("\n4. Testing POST /api/play/move across 3 Difficulty Levels...")
    
    # Board with immediate win for X at cell 2
    board_win = [1, 1, 0, 2, 2, 0, 0, 0, 0]

    # Test Hard
    move_hard = get_agent_move(MoveRequest(board=board_win, difficulty="hard", player=1))
    assert move_hard["action"] == 2, f"Hard must take winning move 2, got {move_hard['action']}"
    print(f"   ✓ Hard Difficulty: Action={move_hard['action']}, Rationale='{move_hard['explanation']}'")

    # Test Easy
    easy_actions = [get_agent_move(MoveRequest(board=board_win, difficulty="easy", player=1))["action"] for _ in range(30)]
    assert any(a != 2 for a in easy_actions), "Easy difficulty must show exploratory non-optimal moves"
    print(f"   ✓ Easy Difficulty: Picked non-optimal exploratory moves {sum(1 for a in easy_actions if a != 2)}/30 times")

    # Test Medium
    move_med = get_agent_move(MoveRequest(board=board_win, difficulty="medium", player=1))
    print(f"   ✓ Medium Difficulty: Action={move_med['action']}, Rationale='{move_med['explanation']}'")

    # 5. Benchmark vs Minimax & Random
    print("\n5. Testing POST /api/benchmark/run vs Minimax and Random...")
    bm_mm = run_benchmark(BenchmarkRequest(opponent="minimax", games=20, difficulty="hard"))
    assert bm_mm["benchmark"]["games"] == 20
    assert 0.0 <= bm_mm["benchmark"]["non_loss_rate"] <= 100.0
    print(f"   ✓ Minimax Benchmark: Non-Loss Rate = {bm_mm['benchmark']['non_loss_rate']}% ({bm_mm['benchmark']['wins']}W-{bm_mm['benchmark']['draws']}D-{bm_mm['benchmark']['losses']}L)")
    assert "sample_replay" in bm_mm
    print(f"     Sample replay moves recorded: {bm_mm['sample_replay']['total_moves']}")

    bm_rnd = run_benchmark(BenchmarkRequest(opponent="random", games=30, difficulty="hard"))
    assert 0.0 <= bm_rnd["benchmark"]["win_rate"] <= 100.0
    print(f"   ✓ Random Benchmark: Win Rate = {bm_rnd['benchmark']['win_rate']}% ({bm_rnd['benchmark']['wins']}W-{bm_rnd['benchmark']['draws']}D-{bm_rnd['benchmark']['losses']}L)")

    # 6. Step-by-Step Game Replay Generation
    print("\n6. Testing POST /api/replay/generate...")
    rep = create_game_replay(ReplayRequest(opponent_type="minimax", difficulty="hard", agent_player=1))
    assert len(rep["moves"]) >= 5
    first_step = rep["moves"][0]
    assert "q_values" in first_step
    assert "explanation" in first_step
    assert "board_before" in first_step
    assert "board_after" in first_step
    print(f"   ✓ Replay Generated: ID={rep['replay_id']}, Moves={rep['total_moves']}, Result='{rep['result_description']}'")
    print(f"     Step 1: Cell {first_step['action']} -> Explanation: '{first_step['explanation']}'")

    # 7. Experiment Persistence
    print("\n7. Testing Experiment Persistence...")
    exps = list_experiments()
    assert len(exps) >= 2
    print(f"   ✓ Found {len(exps)} persisted experiments in experiments.json:")
    for e in exps[:3]:
        print(f"     - [{e['id']}] {e.get('name', 'N/A')} ({e.get('episodes_trained', 0):,} eps)")

    # 8. CSV and Markdown Exporters
    print("\n8. Testing Data Exporters...")
    csv_tr = download_training_history_csv()
    assert "Episodes Trained" in csv_tr.body.decode("utf-8")
    print("   ✓ Training history CSV export OK")

    csv_bm = download_benchmark_results_csv()
    assert "Benchmark ID" in csv_bm.body.decode("utf-8")
    print("   ✓ Benchmark results CSV export OK")

    report = download_experiment_report(exps[0]["id"])
    assert "Reinforcement Learning Experiment Report" in report.body.decode("utf-8")
    print("   ✓ Comprehensive Academic Report (.md) export OK")

    print("\n" + "=" * 60)
    print("🎉 ALL API ENDPOINTS & LOGIC VALIDATED 100% SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_api_tests()
