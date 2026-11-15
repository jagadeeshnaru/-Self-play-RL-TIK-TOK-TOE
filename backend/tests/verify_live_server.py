"""
Live HTTP Server End-to-End Validation Script
Tests all HTTP endpoints on http://127.0.0.1:8000 via urllib.
"""

import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"


def make_request(path, data=None, method="GET"):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
        encoded_data = json.dumps(data).encode("utf-8")
        with urllib.request.urlopen(req, data=encoded_data, timeout=30) as response:
            return response.status, response.read().decode("utf-8")
    else:
        with urllib.request.urlopen(req, timeout=30) as response:
            return response.status, response.read().decode("utf-8")


def main():
    print("=" * 60)
    print("Verifying Live Server on http://127.0.0.1:8000")
    print("=" * 60)

    # 1. Health
    status, body = make_request("/api/health")
    print(f"1. GET /api/health -> Status: {status}, Response: {body}")
    assert status == 200

    # 2. Model Status
    status, body = make_request("/api/model/status")
    model_st = json.loads(body)
    print(f"2. GET /api/model/status -> Status: {status}, Q-States: {model_st['q_states']}, Status: {model_st['status']}")
    assert status == 200

    # 3. Training
    train_data = {
        "episodes": 3000,
        "alpha": 0.5,
        "gamma": 0.9,
        "epsilon_start": 1.0,
        "epsilon_end": 0.05,
        "name": "Live HTTP Validation 3K"
    }
    t0 = time.time()
    status, body = make_request("/api/train", data=train_data, method="POST")
    train_resp = json.loads(body)
    exp = train_resp["experiment"]
    print(f"3. POST /api/train -> Status: {status}, Trained in: {time.time()-t0:.2f}s, States: {exp['q_states']}, Final Draw %: {exp['self_play_draws_pct']}%")
    assert status == 200

    # 4. Play Move across Difficulties
    # Board with immediate win for X at cell 2
    board = [1, 1, 0, 2, 2, 0, 0, 0, 0]
    for diff in ["hard", "medium", "easy"]:
        move_req = {"board": board, "difficulty": diff, "player": 1}
        status, body = make_request("/api/play/move", data=move_req, method="POST")
        move_resp = json.loads(body)
        print(f"4. POST /api/play/move ({diff.upper()}) -> Action: {move_resp['action']}, Rationale: '{move_resp['explanation'][:50]}...'")
        assert status == 200

    # 5. Benchmark vs Minimax
    bm_req = {"opponent": "minimax", "games": 20, "difficulty": "hard"}
    status, body = make_request("/api/benchmark/run", data=bm_req, method="POST")
    bm_resp = json.loads(body)
    bm = bm_resp["benchmark"]
    print(f"5. POST /api/benchmark/run -> Non-Loss Rate: {bm['non_loss_rate']}% ({bm['wins']}W-{bm['draws']}D-{bm['losses']}L)")
    assert status == 200

    # 6. Replay Generation
    rep_req = {"opponent_type": "minimax", "difficulty": "hard", "agent_player": 1}
    status, body = make_request("/api/replay/generate", data=rep_req, method="POST")
    rep = json.loads(body)
    print(f"6. POST /api/replay/generate -> Total Moves: {rep['total_moves']}, Result: '{rep['result_description']}'")
    assert status == 200

    # 7. List Experiments
    status, body = make_request("/api/experiments")
    exps = json.loads(body)
    print(f"7. GET /api/experiments -> Found {len(exps)} saved experiments")
    assert status == 200

    # 8. CSV Exports
    status, body = make_request("/api/export/training-csv")
    print(f"8. GET /api/export/training-csv -> Status: {status}, Size: {len(body)} chars, Header line: {body.splitlines()[0]}")
    assert status == 200
    assert "Episodes Trained" in body

    status, body = make_request("/api/export/benchmark-csv")
    print(f"   GET /api/export/benchmark-csv -> Status: {status}, Size: {len(body)} chars, Header line: {body.splitlines()[0]}")
    assert status == 200
    assert "Benchmark ID" in body

    # 9. Markdown Academic Report Export
    status, body = make_request(f"/api/export/report/{exps[0]['id']}")
    print(f"   GET /api/export/report/{exps[0]['id']} -> Status: {status}, Title: {body.splitlines()[0]}")
    assert status == 200
    assert "Reinforcement Learning Experiment Report" in body

    # 10. Frontend Production HTML Serving
    status, body = make_request("/")
    print(f"10. GET / (Frontend root) -> Status: {status}, Contains title: {'Q-Play' in body}")
    assert status == 200
    assert "Q-Play" in body

    print("\n" + "=" * 60)
    print("✅ LIVE END-TO-END VERIFICATION COMPLETED WITH ZERO ERRORS!")
    print("=" * 60)


if __name__ == "__main__":
    main()
