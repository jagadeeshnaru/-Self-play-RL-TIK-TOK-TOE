"""
FastAPI Backend Application for Tic-Tac-Toe RL Platform
Exposes REST endpoints for:
- Self-play training and live convergence logging
- Human vs Agent gameplay with 3 distinct difficulty levels
- Minimax benchmarking
- Step-by-step game replays with Q-value heatmaps & explanations
- Experiment persistence & side-by-side run comparison
- CSV and Markdown data exports
"""

import time
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
import numpy as np
import os

from backend.rl_engine import (
    RLAgent,
    TicTacToe,
    train_agent,
    evaluate_vs_minimax,
    evaluate_vs_random,
    generate_game_replay
)
import backend.experiments as exp_store
import backend.export_service as exporter


app = FastAPI(
    title="Q-Play: Tic-Tac-Toe Reinforcement Learning API",
    description="Full-stack RL experimentation platform for academic demonstration & evaluation.",
    version="2.0.0"
)

# Enable CORS for frontend Vite dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global active agent in memory
ACTIVE_AGENT: RLAgent = RLAgent(alpha=0.5, gamma=0.9, epsilon_start=1.0, epsilon_end=0.05)
ACTIVE_EXPERIMENT_SUMMARY: Dict[str, Any] = {}
CACHED_BENCHMARKS: List[Dict[str, Any]] = []
CACHED_REPLAYS: Dict[str, Dict[str, Any]] = {}


def _initialize_baseline_agent():
    """Initializes the active agent using stored experiments if present."""
    global ACTIVE_AGENT, ACTIVE_EXPERIMENT_SUMMARY
    existing = exp_store.load_experiments()
    if not existing:
        print("Pre-training initial baseline model (10,000 episodes)...")
        agent, summary = train_agent(episodes=10000, alpha=0.5, gamma=0.9, epsilon_start=1.0, epsilon_end=0.05)
        ACTIVE_AGENT = agent
        summary["id"] = "baseline_10k"
        summary["name"] = "Initial Baseline (10K episodes)"
        summary["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        exp_store.add_experiment(summary)
        ACTIVE_EXPERIMENT_SUMMARY = summary
        print("Initial baseline ready! Q-states:", len(agent.Q))
    else:
        ACTIVE_EXPERIMENT_SUMMARY = existing[0]
        # Train active agent to match the latest saved experiment
        episodes = existing[0].get("episodes_trained", 50000)
        agent, _ = train_agent(
            episodes=episodes,
            alpha=existing[0].get("alpha", 0.5),
            gamma=existing[0].get("gamma", 0.9),
            epsilon_start=existing[0].get("epsilon_start", 1.0),
            epsilon_end=existing[0].get("epsilon_end", 0.05)
        )
        ACTIVE_AGENT = agent


# Initialize agent on module load
_initialize_baseline_agent()


# ---------------------------------------------------------
# Request / Response Pydantic Models with validation
# ---------------------------------------------------------

class TrainRequest(BaseModel):
    episodes: int = Field(50000, ge=1000, le=500000, description="Number of self-play games")
    alpha: float = Field(0.5, ge=0.01, le=1.0, description="Learning rate alpha")
    gamma: float = Field(0.9, ge=0.01, le=1.0, description="Discount factor gamma")
    epsilon_start: float = Field(1.0, ge=0.0, le=1.0, description="Initial exploration rate")
    epsilon_end: float = Field(0.05, ge=0.0, le=1.0, description="Final exploration rate")
    name: Optional[str] = Field(None, max_length=100, description="Experiment title")


class MoveRequest(BaseModel):
    board: List[int] = Field(..., description="Current 9-cell board list (0: empty, 1: X, 2: O)")
    difficulty: str = Field("hard", description="easy, medium, or hard")
    player: int = Field(2, ge=1, le=2, description="Agent's player index: 1 (X) or 2 (O)")

    @field_validator("board")
    def validate_board(cls, v):
        if len(v) != 9:
            raise ValueError("Board must have exactly 9 elements.")
        for val in v:
            if val not in (0, 1, 2):
                raise ValueError("Board cells must be 0 (empty), 1 (X), or 2 (O).")
        return v

    @field_validator("difficulty")
    def validate_difficulty(cls, v):
        if v.lower() not in ("easy", "medium", "hard"):
            raise ValueError("Difficulty must be 'easy', 'medium', or 'hard'.")
        return v.lower()


class BenchmarkRequest(BaseModel):
    opponent: str = Field("minimax", description="'minimax' or 'random'")
    games: int = Field(50, ge=10, le=500, description="Number of evaluation games")
    difficulty: str = Field("hard", description="'easy', 'medium', or 'hard'")


class ReplayRequest(BaseModel):
    opponent_type: str = Field("minimax", description="'minimax', 'random', or 'self-play'")
    difficulty: str = Field("hard", description="'easy', 'medium', or 'hard'")
    agent_player: int = Field(1, ge=1, le=2, description="1 for X, 2 for O")


# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "Q-Play RL Platform", "version": "2.0.0"}


@app.get("/api/model/status")
def get_model_status():
    """Returns active model metadata, parameters, and latest metrics."""
    return {
        "status": "Trained" if len(ACTIVE_AGENT.Q) > 0 else "Untrained",
        "episodes_trained": ACTIVE_AGENT.episodes_trained,
        "q_states": len(ACTIVE_AGENT.Q),
        "train_time_sec": round(ACTIVE_AGENT.total_train_time, 2),
        "alpha": ACTIVE_AGENT.alpha,
        "gamma": ACTIVE_AGENT.gamma,
        "epsilon": round(ACTIVE_AGENT.epsilon, 4),
        "epsilon_start": ACTIVE_AGENT.epsilon_start,
        "epsilon_end": ACTIVE_AGENT.epsilon_end,
        "latest_metrics": ACTIVE_EXPERIMENT_SUMMARY
    }


@app.post("/api/train")
def train_model(req: TrainRequest):
    """
    Executes actual self-play training of the Q-learning agent.
    Collects batch records, evaluates checkpoints, saves run to persistent storage.
    """
    global ACTIVE_AGENT, ACTIVE_EXPERIMENT_SUMMARY

    agent, summary = train_agent(
        episodes=req.episodes,
        alpha=req.alpha,
        gamma=req.gamma,
        epsilon_start=req.epsilon_start,
        epsilon_end=req.epsilon_end
    )
    ACTIVE_AGENT = agent

    run_name = req.name or f"Run-{req.episodes//1000}K-α{req.alpha}-γ{req.gamma}"
    exp_record = {
        "id": f"exp_{int(time.time()*1000)}",
        "name": run_name,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        **summary
    }

    # Persist in storage
    exp_store.add_experiment(exp_record)
    ACTIVE_EXPERIMENT_SUMMARY = exp_record

    return {
        "success": True,
        "message": f"Successfully trained for {req.episodes:,} episodes.",
        "experiment": exp_record
    }


@app.post("/api/play/move")
def get_agent_move(req: MoveRequest):
    """
    Calculates agent's move for human vs agent gameplay.
    Returns:
    - selected action
    - Q-value distribution across all 9 cells
    - explanation of why the action was selected
    - difficulty level used
    """
    board_np = np.array(req.board, dtype=int)
    env = TicTacToe(board_np)
    
    winner = env.check_winner()
    if winner is not None:
        return {
            "game_over": True,
            "winner": winner,
            "action": -1,
            "q_values": {},
            "explanation": "Game is already over."
        }

    move_details = ACTIVE_AGENT.choose_action_with_details(board_np, difficulty=req.difficulty, player=req.player)
    action = move_details["action"]

    # Also calculate board after this move
    test_board = board_np.copy()
    if action >= 0:
        test_board[action] = req.player
    new_winner = TicTacToe(test_board).check_winner()

    return {
        "game_over": new_winner is not None,
        "winner": new_winner,
        "action": action,
        "row": action // 3 if action >= 0 else -1,
        "col": action % 3 if action >= 0 else -1,
        "q_values": move_details["q_values"],
        "explanation": move_details["explanation"],
        "difficulty": req.difficulty,
        "is_exploratory": move_details.get("is_exploratory", False)
    }


@app.post("/api/benchmark/run")
def run_benchmark(req: BenchmarkRequest):
    """
    Runs actual empirical benchmark games between the active agent and Minimax or Random.
    Computes genuine win, loss, and draw counts and generates a step-by-step game replay.
    """
    if req.opponent.lower() == "minimax":
        result = evaluate_vs_minimax(ACTIVE_AGENT, num_games=req.games, difficulty=req.difficulty)
    else:
        result = evaluate_vs_random(ACTIVE_AGENT, num_games=req.games, difficulty=req.difficulty)

    bm_record = {
        "id": f"bm_{int(time.time()*1000)}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "opponent": req.opponent.capitalize(),
        "difficulty": req.difficulty.capitalize(),
        **result
    }
    CACHED_BENCHMARKS.insert(0, bm_record)

    # Generate a sample game replay for step-by-step inspection
    sample_replay = generate_game_replay(
        agent=ACTIVE_AGENT,
        opponent_type=req.opponent.lower(),
        agent_player=1,
        difficulty=req.difficulty
    )
    CACHED_REPLAYS[sample_replay["replay_id"]] = sample_replay

    return {
        "benchmark": bm_record,
        "sample_replay": sample_replay
    }


@app.post("/api/replay/generate")
def create_game_replay(req: ReplayRequest):
    """Generates an on-demand step-by-step game replay with Q-values and explanations."""
    replay = generate_game_replay(
        agent=ACTIVE_AGENT,
        opponent_type=req.opponent_type.lower(),
        agent_player=req.agent_player,
        difficulty=req.difficulty
    )
    CACHED_REPLAYS[replay["replay_id"]] = replay
    return replay


@app.get("/api/replay/{replay_id}")
def get_game_replay(replay_id: str):
    """Retrieves cached game replay by ID."""
    if replay_id in CACHED_REPLAYS:
        return CACHED_REPLAYS[replay_id]
    raise HTTPException(status_code=404, detail="Replay not found.")


# ---------------------------------------------------------
# Experiment Comparison & Persistence Endpoints
# ---------------------------------------------------------

@app.get("/api/experiments")
def list_experiments():
    """Lists all stored experiments for comparison."""
    return exp_store.load_experiments()


@app.get("/api/experiments/{exp_id}")
def get_experiment_details(exp_id: str):
    """Retrieves full details of a specific training run."""
    exp = exp_store.get_experiment_by_id(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return exp


@app.delete("/api/experiments/{exp_id}")
def delete_experiment(exp_id: str):
    """Deletes an experiment by ID."""
    success = exp_store.delete_experiment_by_id(exp_id)
    if not success:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    return {"success": True, "message": f"Deleted experiment {exp_id}"}


# ---------------------------------------------------------
# Data Export Endpoints (CSV & Reports)
# ---------------------------------------------------------

@app.get("/api/export/training-csv")
def download_training_history_csv():
    """Generates and downloads training history CSV."""
    experiments = exp_store.load_experiments()
    csv_content = exporter.export_training_history_csv(experiments)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=training_history.csv"}
    )


@app.get("/api/export/batch-curves-csv/{exp_id}")
def download_batch_curves_csv(exp_id: str):
    """Downloads batch-by-batch learning curves for an experiment as CSV."""
    exp = exp_store.get_experiment_by_id(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    csv_content = exporter.export_batch_curves_csv(exp)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=curves_{exp_id}.csv"}
    )


@app.get("/api/export/benchmark-csv")
def download_benchmark_results_csv():
    """Downloads benchmark results CSV."""
    csv_content = exporter.export_benchmark_results_csv(CACHED_BENCHMARKS)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=benchmark_results.csv"}
    )


@app.get("/api/export/replay-csv/{replay_id}")
def download_replay_csv(replay_id: str):
    """Downloads step-by-step game replay as CSV."""
    replay = CACHED_REPLAYS.get(replay_id)
    if not replay:
        # Generate one on the fly if not found
        replay = generate_game_replay(ACTIVE_AGENT, "minimax", 1, "hard")
    csv_content = exporter.export_replay_csv(replay)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=replay_{replay_id}.csv"}
    )


@app.get("/api/export/report/{exp_id}")
def download_experiment_report(exp_id: str):
    """Generates and downloads academic experiment report as Markdown."""
    exp = exp_store.get_experiment_by_id(exp_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found.")
    report_md = exporter.generate_experiment_summary_report(exp)
    return Response(
        content=report_md,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=experiment_report_{exp_id}.md"}
    )


# Serve frontend production build if available
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

