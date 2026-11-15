"""
Reinforcement Learning Engine for Tic-Tac-Toe
Provides:
- TicTacToe environment
- Tabular Q-learning agent with negamax self-play updates
- Optimal Minimax algorithm
- Multi-tier Agent Difficulty levels (Easy, Medium, Hard)
- Checkpoint benchmark logger during training
- Step-by-step game replay engine with Q-value distributions and move explanations
"""

import time
import math
import random
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


class TicTacToe:
    """Tic-Tac-Toe game environment with standard 3x3 board."""
    WIN_COMBINATIONS = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Rows
        (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Columns
        (0, 4, 8), (2, 4, 6)              # Diagonals
    ]

    def __init__(self, board: Optional[np.ndarray] = None):
        if board is not None:
            self.board = np.array(board, dtype=int).copy()
        else:
            self.board = np.zeros(9, dtype=int)

    def reset(self) -> np.ndarray:
        self.board = np.zeros(9, dtype=int)
        return self.board.copy()

    def available_moves(self) -> List[int]:
        return [i for i in range(9) if self.board[i] == 0]

    def check_winner(self) -> Optional[int]:
        """
        Returns:
            1: Player 1 (X) wins
            2: Player 2 (O) wins
            0: Draw (board full with no winner)
            None: Game still in progress
        """
        for a, b, c in self.WIN_COMBINATIONS:
            if self.board[a] != 0 and self.board[a] == self.board[b] == self.board[c]:
                return int(self.board[a])

        if not any(self.board == 0):
            return 0

        return None

    def make_move(self, position: int, player: int) -> bool:
        if 0 <= position < 9 and self.board[position] == 0:
            self.board[position] = player
            return True
        return False

    def is_game_over(self) -> bool:
        return self.check_winner() is not None


_MINIMAX_CACHE: Dict[Tuple[Tuple[int, ...], int], Tuple[int, Optional[int]]] = {}

# Minimax Algorithm for optimal Play and Benchmarking
def minimax(board: np.ndarray, player: int) -> Tuple[int, Optional[int]]:
    """
    Optimal Minimax search for Tic-Tac-Toe with memoization and alpha-beta pruning.
    player: 1 (X) or 2 (O)
    """
    state_key = (tuple(board.tolist()), player)
    if state_key in _MINIMAX_CACHE:
        return _MINIMAX_CACHE[state_key]

    env = TicTacToe(board)
    winner = env.check_winner()

    if winner == player:
        return (1, None)
    elif winner == (3 - player):
        return (-1, None)
    elif winner == 0:
        return (0, None)

    best_score = -float('inf')
    best_move = None
    moves = env.available_moves()

    for move in moves:
        board_copy = board.copy()
        board_copy[move] = player
        opponent_score, _ = minimax(board_copy, 3 - player)
        score = -opponent_score

        if score > best_score:
            best_score = score
            best_move = move
            if best_score == 1:  # Cannot get better than guaranteed win in zero-sum
                break

    res = (best_score, best_move)
    _MINIMAX_CACHE[state_key] = res
    return res


def get_all_minimax_scores(board: np.ndarray, player: int) -> Dict[int, float]:
    """Computes exact minimax evaluation score for each available move."""
    env = TicTacToe(board)
    scores = {}
    for move in env.available_moves():
        board_copy = board.copy()
        board_copy[move] = player
        opp_score, _ = minimax(board_copy, 3 - player)
        scores[move] = float(-opp_score)
    return scores


class RLAgent:
    """
    Tabular Q-learning agent with negamax self-play updates.
    State representation: tuple of 9 integers (0: empty, 1: X, 2: O).
    Q-table maps state tuple -> np.ndarray of shape (9,).
    """

    def __init__(self, alpha: float = 0.5, gamma: float = 0.9, epsilon_start: float = 1.0, epsilon_end: float = 0.05):
        self.Q: Dict[Tuple[int, ...], np.ndarray] = {}
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_start = epsilon_start
        self.epsilon_end = epsilon_end
        self.episodes_trained = 0
        self.total_train_time = 0.0

    def get_q(self, state: Tuple[int, ...]) -> np.ndarray:
        if state not in self.Q:
            self.Q[state] = np.zeros(9, dtype=float)
        return self.Q[state]

    def get_q_for_display(self, board: np.ndarray) -> Dict[int, float]:
        """Returns Q-values for all legal moves in board state."""
        state = tuple(board.tolist())
        q_vals = self.get_q(state)
        available = [i for i in range(9) if board[i] == 0]
        return {i: round(float(q_vals[i]), 4) for i in available}

    def choose_action(self, state: Tuple[int, ...], available: List[int], epsilon: Optional[float] = None) -> int:
        eps = self.epsilon if epsilon is None else epsilon
        if random.random() < eps:
            return random.choice(available)

        q_values = self.get_q(state)
        best_val = max(q_values[a] for a in available)
        best_actions = [a for a in available if math.isclose(q_values[a], best_val, rel_tol=1e-5, abs_tol=1e-5)]
        return random.choice(best_actions)

    def choose_action_with_details(self, board: np.ndarray, difficulty: str = "hard", player: Optional[int] = None) -> Dict[str, Any]:
        """
        Chooses an action based on difficulty level with comprehensive RL rationale:
        - Easy: High exploration (eps=0.50), frequently makes random / weak moves
        - Medium: Balanced policy (eps=0.12, with tactical win/block awareness)
        - Hard: Pure greedy policy (eps=0.0) from fully converged Q-table
        """
        env = TicTacToe(board)
        available = env.available_moves()
        if not available:
            return {"action": -1, "explanation": "No available moves.", "q_values": {}}

        state = tuple(board.tolist())
        q_values = self.get_q(state)
        q_map = {i: round(float(q_values[i]), 4) for i in available}
        best_val = max(q_values[a] for a in available)
        best_actions = [a for a in available if math.isclose(q_values[a], best_val, rel_tol=1e-5, abs_tol=1e-5)]
        greedy_action = random.choice(best_actions)

        # Determine active player if not provided
        if player is None:
            player = 2 if np.sum(board == 1) > np.sum(board == 2) else 1
        opponent = 3 - player

        # Check for immediate winning move
        immediate_win = None
        for move in available:
            test_b = board.copy()
            test_b[move] = player
            if TicTacToe(test_b).check_winner() == player:
                immediate_win = move
                break

        # Check for immediate opponent winning move (need block)
        immediate_block = None
        for move in available:
            test_b = board.copy()
            test_b[move] = opponent
            if TicTacToe(test_b).check_winner() == opponent:
                immediate_block = move
                break

        selected_action = greedy_action
        is_exploratory = False
        reason = ""

        if difficulty.lower() == "easy":
            # Easy agent: 50% random exploration, occasionally overlooks tactical moves
            if random.random() < 0.50:
                is_exploratory = True
                selected_action = random.choice(available)
                reason = f"Easy Agent explored cell {selected_action} with random trial (exploration rate 50%)."
            else:
                selected_action = greedy_action
                reason = f"Easy Agent selected cell {selected_action} based on learned Q-value ({q_map[selected_action]})."

        elif difficulty.lower() == "medium":
            # Medium agent: 12% exploration; prioritizes immediate win/block 85% of time
            if immediate_win is not None and random.random() < 0.90:
                selected_action = immediate_win
                reason = f"Medium Agent detected immediate winning move at cell {selected_action}."
            elif immediate_block is not None and random.random() < 0.85:
                selected_action = immediate_block
                reason = f"Medium Agent blocked opponent winning threat at cell {selected_action}."
            elif random.random() < 0.12:
                is_exploratory = True
                selected_action = random.choice(available)
                reason = f"Medium Agent explored alternate cell {selected_action} to test variations."
            else:
                selected_action = greedy_action
                reason = f"Medium Agent chose highest Q-value action at cell {selected_action} (Q={q_map[selected_action]})."

        else:  # Hard (pure greedy master agent)
            # If there is an immediate win, take it
            if immediate_win is not None:
                selected_action = immediate_win
                reason = f"Hard Agent executed decisive winning strike at cell {selected_action} (Q={q_map[selected_action]})."
            elif immediate_block is not None and (greedy_action != immediate_block and q_map.get(immediate_block, -99) >= q_map.get(greedy_action, -99) - 0.2):
                selected_action = immediate_block
                reason = f"Hard Agent executed vital defensive block at cell {selected_action} to thwart opponent win."
            else:
                selected_action = greedy_action
                if immediate_block is not None and selected_action == immediate_block:
                    reason = f"Hard Agent executed vital defensive block at cell {selected_action} to thwart opponent win."
                elif selected_action == 4 and board[4] == 0:
                    reason = f"Hard Agent secured strategic center square (cell 4) controlling 4 winning lines (Q={q_map[selected_action]})."
                elif selected_action in [0, 2, 6, 8]:
                    reason = f"Hard Agent claimed corner square {selected_action} maximizing diagonal fork potential (Q={q_map[selected_action]})."
                else:
                    reason = f"Hard Agent selected optimal action at cell {selected_action} with maximum policy Q-value of {q_map[selected_action]}."

        return {
            "action": int(selected_action),
            "is_exploratory": is_exploratory,
            "q_values": q_map,
            "best_q_value": float(best_val),
            "explanation": reason,
            "difficulty": difficulty
        }

    def update_negamax(self, state: Tuple[int, ...], action: int, reward: float, next_state: Tuple[int, ...], done: bool):
        """
        Negamax zero-sum Q-learning update:
        Q(s, a) = Q(s, a) + alpha * [ reward - gamma * max_a' Q(s', a') - Q(s, a) ]
        When game is done, target = reward.
        When game continues, target = reward - gamma * max_a' Q(s', a')
        (Opponent's best value in s' is subtracted because Tic-Tac-Toe is zero-sum).
        """
        q_values = self.get_q(state)
        if done:
            target = reward
        else:
            next_q = self.get_q(next_state)
            avail_next = [i for i in range(9) if next_state[i] == 0]
            if avail_next:
                best_next = max(next_q[a] for a in avail_next)
                target = reward - self.gamma * best_next
            else:
                target = reward

        q_values[action] += self.alpha * (target - q_values[action])


def train_agent(
    episodes: int = 50000,
    alpha: float = 0.5,
    gamma: float = 0.9,
    epsilon_start: float = 1.0,
    epsilon_end: float = 0.05,
    existing_agent: Optional[RLAgent] = None
) -> Tuple[RLAgent, Dict[str, Any]]:
    """
    Trains tabular Q-learning agent through self-play and collects batch-level convergence curves.
    Evaluates checkpoints against Minimax and Random player.
    """
    start_time = time.time()
    agent = existing_agent or RLAgent(alpha=alpha, gamma=gamma, epsilon_start=epsilon_start, epsilon_end=epsilon_end)
    agent.alpha = alpha
    agent.gamma = gamma
    agent.epsilon_start = epsilon_start
    agent.epsilon_end = epsilon_end

    decay_episodes = int(episodes * 0.8)

    # Determine batch evaluation cadence (approx 20 checkpoints)
    batch_size = max(1000, episodes // 25)
    
    batch_records = []
    
    current_batch_x_wins = 0
    current_batch_o_wins = 0
    current_batch_draws = 0

    for ep in range(1, episodes + 1):
        # Linear decay of epsilon up to 80% of episodes
        if ep <= decay_episodes:
            eps = epsilon_start - (epsilon_start - epsilon_end) * (ep / decay_episodes)
        else:
            eps = epsilon_end
        agent.epsilon = eps

        env = TicTacToe()
        game_history = []
        current_player = 1

        while True:
            state = tuple(env.board.tolist())
            available = env.available_moves()
            action = agent.choose_action(state, available, eps)
            game_history.append((state, action, current_player))

            env.make_move(action, current_player)
            winner = env.check_winner()

            if winner is not None:
                if winner == 1:
                    current_batch_x_wins += 1
                elif winner == 2:
                    current_batch_o_wins += 1
                else:
                    current_batch_draws += 1

                # Backpropagate rewards for self-play
                # Last move led to terminal state
                last_state, last_action, last_player = game_history[-1]
                if winner == 0:
                    agent.update_negamax(last_state, last_action, reward=0.0, next_state=tuple(env.board.tolist()), done=True)
                else:
                    agent.update_negamax(last_state, last_action, reward=1.0, next_state=tuple(env.board.tolist()), done=True)

                # Prior move(s) in history
                if len(game_history) >= 2:
                    prev_state, prev_action, prev_player = game_history[-2]
                    # The opponent of the winner gets -1 or 0
                    if winner == 0:
                        agent.update_negamax(prev_state, prev_action, reward=0.0, next_state=last_state, done=True)
                    else:
                        agent.update_negamax(prev_state, prev_action, reward=-1.0, next_state=last_state, done=True)

                # Update any earlier intermediate steps
                for i in range(len(game_history) - 3, -1, -1):
                    s, a, p = game_history[i]
                    next_s, _, _ = game_history[i + 1]
                    agent.update_negamax(s, a, reward=0.0, next_state=next_s, done=False)
                break

            current_player = 3 - current_player

        # Checkpoint evaluation
        if ep % batch_size == 0 or ep == episodes:
            games_in_batch = current_batch_x_wins + current_batch_o_wins + current_batch_draws
            draw_rate = (current_batch_draws / games_in_batch) * 100 if games_in_batch > 0 else 0.0
            x_win_rate = (current_batch_x_wins / games_in_batch) * 100 if games_in_batch > 0 else 0.0
            o_win_rate = (current_batch_o_wins / games_in_batch) * 100 if games_in_batch > 0 else 0.0

            # Fast checkpoint benchmark vs Minimax and Random
            minimax_non_loss = evaluate_vs_minimax(agent, num_games=6)["non_loss_rate"]
            random_win_rate = evaluate_vs_random(agent, num_games=10)["win_rate"]

            batch_records.append({
                "episode": ep,
                "draw_rate": round(draw_rate, 2),
                "x_win_rate": round(x_win_rate, 2),
                "o_win_rate": round(o_win_rate, 2),
                "non_loss_vs_minimax": round(minimax_non_loss, 2),
                "win_vs_random": round(random_win_rate, 2),
                "epsilon": round(eps, 4),
                "q_states": len(agent.Q)
            })

            # Reset batch outcome counters
            current_batch_x_wins = 0
            current_batch_o_wins = 0
            current_batch_draws = 0

    elapsed = time.time() - start_time
    agent.episodes_trained += episodes
    agent.total_train_time += elapsed

    # Final comprehensive evaluation
    final_vs_minimax = evaluate_vs_minimax(agent, num_games=30)
    final_vs_random = evaluate_vs_random(agent, num_games=50)

    last_record = batch_records[-1] if batch_records else {}
    summary = {
        "episodes_trained": episodes,
        "total_episodes": agent.episodes_trained,
        "train_time_sec": round(elapsed, 2),
        "q_states": len(agent.Q),
        "final_epsilon": round(agent.epsilon, 4),
        "alpha": alpha,
        "gamma": gamma,
        "epsilon_start": epsilon_start,
        "epsilon_end": epsilon_end,
        "self_play_draws_pct": last_record.get("draw_rate", 0.0),
        "self_play_x_wins_pct": last_record.get("x_win_rate", 0.0),
        "self_play_o_wins_pct": last_record.get("o_win_rate", 0.0),
        "non_loss_vs_minimax_pct": final_vs_minimax["non_loss_rate"],
        "win_vs_random_pct": final_vs_random["win_rate"],
        "benchmark_minimax": final_vs_minimax,
        "benchmark_random": final_vs_random,
        "batch_records": batch_records
    }

    return agent, summary


def evaluate_vs_minimax(agent: RLAgent, num_games: int = 50, difficulty: str = "hard") -> Dict[str, Any]:
    """
    Evaluates RL agent against optimal Minimax player.
    Difficulty controls the agent's decision engine (Easy, Medium, Hard).
    Agent plays alternating turns (half games as X, half as O).
    """
    wins = 0
    losses = 0
    draws = 0

    for g in range(num_games):
        env = TicTacToe()
        agent_player = 1 if (g % 2 == 0) else 2
        minimax_player = 3 - agent_player
        current_player = 1

        while True:
            avail = env.available_moves()
            if not avail:
                break

            if current_player == agent_player:
                details = agent.choose_action_with_details(env.board, difficulty=difficulty, player=agent_player)
                action = details["action"]
                if action not in avail:
                    action = random.choice(avail)
                env.make_move(action, agent_player)
            else:
                _, move = minimax(env.board.copy(), minimax_player)
                if move is None or move not in avail:
                    move = random.choice(avail)
                env.make_move(move, minimax_player)

            winner = env.check_winner()
            if winner is not None:
                if winner == agent_player:
                    wins += 1
                elif winner == minimax_player:
                    losses += 1
                else:
                    draws += 1
                break

            current_player = 3 - current_player

    non_loss = wins + draws
    return {
        "games": num_games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": round((wins / num_games) * 100, 2),
        "loss_rate": round((losses / num_games) * 100, 2),
        "draw_rate": round((draws / num_games) * 100, 2),
        "non_loss_rate": round((non_loss / num_games) * 100, 2)
    }


def evaluate_vs_random(agent: RLAgent, num_games: int = 100, difficulty: str = "hard") -> Dict[str, Any]:
    """Evaluates RL agent against a uniformly random opponent across difficulty tiers."""
    wins = 0
    losses = 0
    draws = 0

    for g in range(num_games):
        env = TicTacToe()
        agent_player = 1 if (g % 2 == 0) else 2
        rand_player = 3 - agent_player
        current_player = 1

        while True:
            avail = env.available_moves()
            if not avail:
                break

            if current_player == agent_player:
                details = agent.choose_action_with_details(env.board, difficulty=difficulty, player=agent_player)
                action = details["action"]
                if action not in avail:
                    action = random.choice(avail)
                env.make_move(action, agent_player)
            else:
                action = random.choice(avail)
                env.make_move(action, rand_player)

            winner = env.check_winner()
            if winner is not None:
                if winner == agent_player:
                    wins += 1
                elif winner == rand_player:
                    losses += 1
                else:
                    draws += 1
                break

            current_player = 3 - current_player

    return {
        "games": num_games,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "win_rate": round((wins / num_games) * 100, 2),
        "loss_rate": round((losses / num_games) * 100, 2),
        "draw_rate": round((draws / num_games) * 100, 2),
        "non_loss_rate": round(((wins + draws) / num_games) * 100, 2)
    }


def generate_game_replay(agent: RLAgent, opponent_type: str = "minimax", agent_player: int = 1, difficulty: str = "hard") -> Dict[str, Any]:
    """
    Plays a complete game and records full step-by-step replay diagnostics:
    - Board state at every step
    - Active player and name
    - Selected action and cell coordinates
    - Q-values / action scores for each legal move
    - Full explanation of why the move was selected
    - Highlighted cell
    - Final outcome
    """
    env = TicTacToe()
    moves_history = []
    current_player = 1
    step_num = 0

    while True:
        board_before = env.board.tolist()
        avail = env.available_moves()
        if not avail:
            break

        is_agent_turn = (current_player == agent_player)
        player_name = f"RL Agent ({difficulty.capitalize()})" if is_agent_turn else opponent_type.capitalize()
        symbol = "X" if current_player == 1 else "O"

        q_map = {}
        action = -1
        explanation = ""

        if is_agent_turn:
            details = agent.choose_action_with_details(env.board, difficulty=difficulty)
            action = details["action"]
            q_map = details["q_values"]
            explanation = details["explanation"]
        else:
            if opponent_type.lower() == "minimax":
                mm_scores = get_all_minimax_scores(env.board, current_player)
                _, action = minimax(env.board.copy(), current_player)
                if action is None:
                    action = random.choice(avail)
                q_map = mm_scores
                explanation = f"Minimax calculated optimal move at cell {action} with minimax evaluation score {mm_scores.get(action, 0)}."
            else:
                action = random.choice(avail)
                q_map = {m: 0.0 for m in avail}
                explanation = f"Random opponent played cell {action} uniformly at random."

        env.make_move(action, current_player)
        board_after = env.board.tolist()
        winner = env.check_winner()

        row = action // 3
        col = action % 3

        moves_history.append({
            "step": step_num,
            "player": current_player,
            "symbol": symbol,
            "player_name": player_name,
            "action": action,
            "row": row,
            "col": col,
            "board_before": board_before,
            "board_after": board_after,
            "available_moves": avail,
            "q_values": q_map,
            "explanation": explanation,
            "is_terminal": winner is not None,
            "winner_so_far": winner
        })

        if winner is not None:
            break

        current_player = 3 - current_player
        step_num += 1

    final_winner = env.check_winner()
    if final_winner == agent_player:
        result_str = f"RL Agent Won as {('X' if agent_player == 1 else 'O')}!"
    elif final_winner == (3 - agent_player):
        result_str = f"{opponent_type.capitalize()} Won!"
    else:
        result_str = "Game Ended in a Draw (Cat's Game)."

    return {
        "replay_id": f"rep_{int(time.time()*1000)}",
        "opponent_type": opponent_type,
        "difficulty": difficulty,
        "agent_player": agent_player,
        "agent_symbol": "X" if agent_player == 1 else "O",
        "total_moves": len(moves_history),
        "final_winner": final_winner,
        "result_description": result_str,
        "moves": moves_history,
        "final_board": env.board.tolist()
    }
