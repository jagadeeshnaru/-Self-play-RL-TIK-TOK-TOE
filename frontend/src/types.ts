export interface ModelStatus {
  status: string;
  episodes_trained: number;
  q_states: number;
  train_time_sec: number;
  alpha: number;
  gamma: number;
  epsilon: number;
  epsilon_start: number;
  epsilon_end: number;
  latest_metrics?: Experiment;
}

export interface BatchRecord {
  episode: number;
  draw_rate: number;
  x_win_rate: number;
  o_win_rate: number;
  non_loss_vs_minimax: number;
  win_vs_random: number;
  epsilon: number;
  q_states: number;
  [key: string]: number;
}

export interface BenchmarkMetrics {
  games: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  loss_rate: number;
  draw_rate: number;
  non_loss_rate: number;
}

export interface Experiment {
  id: string;
  name: string;
  timestamp: string;
  episodes_trained: number;
  train_time_sec: number;
  q_states: number;
  final_epsilon: number;
  alpha: number;
  gamma: number;
  epsilon_start: number;
  epsilon_end: number;
  self_play_draws_pct: number;
  self_play_x_wins_pct: number;
  self_play_o_wins_pct: number;
  non_loss_vs_minimax_pct: number;
  win_vs_random_pct: number;
  batch_records: BatchRecord[];
  benchmark_minimax?: BenchmarkMetrics;
  benchmark_random?: BenchmarkMetrics;
}

export interface ReplayMove {
  step: number;
  player: number;
  symbol: string;
  player_name: string;
  action: number;
  row: number;
  col: number;
  board_before: number[];
  board_after: number[];
  available_moves: number[];
  q_values: Record<number, number>;
  explanation: string;
  is_terminal: boolean;
  winner_so_far: number | null;
}

export interface GameReplay {
  replay_id: string;
  opponent_type: string;
  difficulty: string;
  agent_player: number;
  agent_symbol: string;
  total_moves: number;
  final_winner: number;
  result_description: string;
  moves: ReplayMove[];
  final_board: number[];
}

export interface BenchmarkRunResult {
  id: string;
  timestamp: string;
  opponent: string;
  difficulty: string;
  games: number;
  wins: number;
  losses: number;
  draws: number;
  win_rate: number;
  loss_rate: number;
  draw_rate: number;
  non_loss_rate: number;
}
