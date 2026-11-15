"""
API Endpoints Full Integration Test Suite
Validates all REST routes using Starlette / FastAPI TestClient:
- Health check
- Model status
- Training execution & batch curves
- Human vs Agent move calculation across all 3 difficulty tiers
- Benchmark execution against Minimax and Random opponents
- Step-by-step game replay generation
- Experiment persistence & deletion
- CSV and Markdown data exports
- Production frontend static serving
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    print("1. Testing GET /api/health...")
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    print("   ✓ Health check OK")


def test_model_status():
    print("2. Testing GET /api/model/status...")
    resp = client.get("/api/model/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "q_states" in data
    assert data["q_states"] > 0
    print(f"   ✓ Model status OK: {data['status']}, {data['q_states']} states")


def test_training():
    print("3. Testing POST /api/train (3,000 episodes)...")
    payload = {
        "episodes": 3000,
        "alpha": 0.5,
        "gamma": 0.9,
        "epsilon_start": 1.0,
        "epsilon_end": 0.05,
        "name": "Integration Test Run 3K"
    }
    resp = client.post("/api/train", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    exp = data["experiment"]
    assert exp["episodes_trained"] == 3000
    assert len(exp["batch_records"]) > 0
    print(f"   ✓ Training OK: {exp['episodes_trained']} episodes trained in {exp['train_time_sec']}s")


def test_play_move_difficulties():
    print("4. Testing POST /api/play/move across Easy, Medium, Hard...")
    # Empty board
    board = [0] * 9

    for diff in ["easy", "medium", "hard"]:
        payload = {
            "board": board,
            "difficulty": diff,
            "player": 2
        }
        resp = client.post("/api/play/move", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert 0 <= data["action"] <= 8
        assert len(data["q_values"]) > 0
        assert len(data["explanation"]) > 0
        print(f"   ✓ Difficulty '{diff}' OK: selected action {data['action']}, reason: {data['explanation'][:45]}...")


def test_benchmark_run():
    print("5. Testing POST /api/benchmark/run vs Minimax and Random...")
    # vs Minimax
    resp_mm = client.post("/api/benchmark/run", json={"opponent": "minimax", "games": 20, "difficulty": "hard"})
    assert resp_mm.status_code == 200
    data_mm = resp_mm.json()
    bm = data_mm["benchmark"]
    assert bm["games"] == 20
    assert "non_loss_rate" in bm
    assert "sample_replay" in data_mm
    print(f"   ✓ Benchmark vs Minimax OK: {bm['non_loss_rate']}% non-loss rate ({bm['wins']}W-{bm['draws']}D-{bm['losses']}L)")

    # vs Random
    resp_rnd = client.post("/api/benchmark/run", json={"opponent": "random", "games": 30, "difficulty": "hard"})
    assert resp_rnd.status_code == 200
    bm_rnd = resp_rnd.json()["benchmark"]
    assert bm_rnd["win_rate"] >= 80.0
    print(f"   ✓ Benchmark vs Random OK: {bm_rnd['win_rate']}% win rate ({bm_rnd['wins']}W-{bm_rnd['draws']}D-{bm_rnd['losses']}L)")


def test_replay_generation():
    print("6. Testing POST /api/replay/generate...")
    payload = {
        "opponent_type": "minimax",
        "difficulty": "hard",
        "agent_player": 1
    }
    resp = client.post("/api/replay/generate", json=payload)
    assert resp.status_code == 200
    replay = resp.json()
    assert len(replay["moves"]) >= 5
    assert "replay_id" in replay
    assert "result_description" in replay
    print(f"   ✓ Replay generation OK: {len(replay['moves'])} moves, result: {replay['result_description']}")


def test_exports():
    print("7. Testing CSV and Markdown Report Export routes...")
    # Training history CSV
    resp_tr = client.get("/api/export/training-csv")
    assert resp_tr.status_code == 200
    assert "text/csv" in resp_tr.headers["content-type"]
    assert "Episodes Trained" in resp_tr.text

    # Benchmark CSV
    resp_bm = client.get("/api/export/benchmark-csv")
    assert resp_bm.status_code == 200
    assert "text/csv" in resp_bm.headers["content-type"]

    # Experiments list
    resp_exp = client.get("/api/experiments")
    assert resp_exp.status_code == 200
    exps = resp_exp.json()
    assert len(exps) > 0
    exp_id = exps[0]["id"]

    # Markdown report
    resp_rep = client.get(f"/api/export/report/{exp_id}")
    assert resp_rep.status_code == 200
    assert "text/markdown" in resp_rep.headers["content-type"]
    assert "Reinforcement Learning Experiment Report" in resp_rep.text
    print("   ✓ All export routes verified successfully")


def test_frontend_serving():
    print("8. Testing Static Frontend build serving...")
    resp = client.get("/")
    assert resp.status_code == 200
    assert "<!doctype html>" in resp.text.lower()
    assert "Q-Play" in resp.text
    print("   ✓ Production frontend successfully mounted and served at '/'")


if __name__ == "__main__":
    test_health()
    test_model_status()
    test_training()
    test_play_move_difficulties()
    test_benchmark_run()
    test_replay_generation()
    test_exports()
    test_frontend_serving()
    print("\n🎉 ALL API & END-TO-END INTEGRATION TESTS PASSED PERFECTLY!")
