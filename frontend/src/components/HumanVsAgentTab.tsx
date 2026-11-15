import React, { useState } from 'react';
import { RotateCcw, Sparkles, Brain, Cpu } from 'lucide-react';

interface HumanVsAgentProps {
  onAgentMove: (board: number[], difficulty: string, player: number) => Promise<{
    action: number;
    q_values: Record<number, number>;
    explanation: string;
    game_over: boolean;
    winner: number | null;
  }>;
}

export const HumanVsAgentTab: React.FC<HumanVsAgentProps> = ({ onAgentMove }) => {
  const [board, setBoard] = useState<number[]>(Array(9).fill(0));
  const [humanPlayer, setHumanPlayer] = useState<number>(1); // 1 = X (plays first), 2 = O (plays second)
  const [difficulty, setDifficulty] = useState<string>('hard');
  const [currentTurn, setCurrentTurn] = useState<number>(1);
  const [winner, setWinner] = useState<number | null>(null);
  const [isGameOver, setIsGameOver] = useState<boolean>(false);
  const [agentThinking, setAgentThinking] = useState<boolean>(false);
  const [lastAgentExplanation, setLastAgentExplanation] = useState<string>('');
  const [activeQValues, setActiveQValues] = useState<Record<number, number>>({});
  const [showQOverlay, setShowQOverlay] = useState<boolean>(true);
  const [lastMoveIndex, setLastMoveIndex] = useState<number | null>(null);

  // Scoreboard
  const [humanWins, setHumanWins] = useState<number>(0);
  const [agentWins, setAgentWins] = useState<number>(0);
  const [draws, setDraws] = useState<number>(0);

  const agentPlayer = 3 - humanPlayer;

  const checkWinnerSync = (b: number[]): number | null => {
    const lines = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],
      [0, 3, 6], [1, 4, 7], [2, 5, 8],
      [0, 4, 8], [2, 4, 6]
    ];
    for (const [x, y, z] of lines) {
      if (b[x] !== 0 && b[x] === b[y] && b[x] === b[z]) {
        return b[x];
      }
    }
    if (!b.includes(0)) return 0;
    return null;
  };

  const handleCellClick = async (index: number) => {
    if (board[index] !== 0 || isGameOver || agentThinking || currentTurn !== humanPlayer) {
      return;
    }

    // Make human move
    const newBoard = [...board];
    newBoard[index] = humanPlayer;
    setBoard(newBoard);
    setLastMoveIndex(index);

    const winCheck = checkWinnerSync(newBoard);
    if (winCheck !== null) {
      handleGameOver(winCheck);
      return;
    }

    // Agent's turn
    setCurrentTurn(agentPlayer);
    setAgentThinking(true);

    try {
      const resp = await onAgentMove(newBoard, difficulty, agentPlayer);
      if (resp.action >= 0) {
        newBoard[resp.action] = agentPlayer;
        setBoard([...newBoard]);
        setLastMoveIndex(resp.action);
        setActiveQValues(resp.q_values || {});
        setLastAgentExplanation(resp.explanation || '');

        const finalWin = checkWinnerSync(newBoard);
        if (finalWin !== null) {
          handleGameOver(finalWin);
        } else {
          setCurrentTurn(humanPlayer);
        }
      }
    } catch (err) {
      console.error('Agent move error:', err);
    } finally {
      setAgentThinking(false);
    }
  };

  const handleGameOver = (winResult: number) => {
    setIsGameOver(true);
    setWinner(winResult);
    if (winResult === humanPlayer) {
      setHumanWins((w) => w + 1);
    } else if (winResult === agentPlayer) {
      setAgentWins((w) => w + 1);
    } else if (winResult === 0) {
      setDraws((d) => d + 1);
    }
  };

  const resetGame = async (newHumanPlayer = humanPlayer) => {
    const emptyBoard = Array(9).fill(0);
    setBoard(emptyBoard);
    setWinner(null);
    setIsGameOver(false);
    setLastAgentExplanation('');
    setActiveQValues({});
    setLastMoveIndex(null);
    setCurrentTurn(1);

    // If human chose O (plays 2nd), Agent (plays 1st as X) makes first move
    if (newHumanPlayer === 2) {
      setAgentThinking(true);
      try {
        const resp = await onAgentMove(emptyBoard, difficulty, 1);
        if (resp.action >= 0) {
          emptyBoard[resp.action] = 1;
          setBoard([...emptyBoard]);
          setLastMoveIndex(resp.action);
          setActiveQValues(resp.q_values || {});
          setLastAgentExplanation(resp.explanation || '');
          setCurrentTurn(2);
        }
      } catch (err) {
        console.error('First agent move error:', err);
      } finally {
        setAgentThinking(false);
      }
    }
  };

  // If human player changes, restart
  const switchPlayer = (player: number) => {
    setHumanPlayer(player);
    resetGame(player);
  };

  return (
    <div className="human-play-tab">
      <div className="play-grid-layout">
        {/* Left Side: Game Board & Direct Controls */}
        <div className="board-pane card">
          <div className="board-top-bar">
            <div className="turn-indicator">
              {isGameOver ? (
                <span className="game-over-tag">
                  {winner === humanPlayer && '🎉 Victory! You won.'}
                  {winner === agentPlayer && '🤖 Agent Won! Better luck next time.'}
                  {winner === 0 && '🤝 Draw! Perfect theoretical play.'}
                </span>
              ) : agentThinking ? (
                <span className="turn-tag thinking">
                  <Cpu size={15} className="spin text-cyan" />
                  <span>Agent calculating Q-values...</span>
                </span>
              ) : currentTurn === humanPlayer ? (
                <span className="turn-tag human">
                  <span className="turn-dot pulse-green" />
                  <span>Your Turn ({humanPlayer === 1 ? 'X' : 'O'})</span>
                </span>
              ) : (
                <span className="turn-tag agent">
                  <span className="turn-dot pulse-blue" />
                  <span>Agent Turn</span>
                </span>
              )}
            </div>

            <button
              onClick={() => resetGame()}
              className="btn btn-secondary btn-sm"
              title="Reset Board"
            >
              <RotateCcw size={14} />
              <span>New Game</span>
            </button>
          </div>

          {/* 3x3 Tic Tac Toe Grid */}
          <div className="board-matrix-container">
            <div className="tictactoe-grid">
              {board.map((cell, idx) => {
                const isSelected = lastMoveIndex === idx;
                const qVal = activeQValues[idx];
                const isEmpty = cell === 0;

                return (
                  <button
                    key={idx}
                    className={`grid-cell ${cell === 1 ? 'cell-x' : cell === 2 ? 'cell-o' : 'cell-empty'} ${
                      isSelected ? 'cell-selected' : ''
                    }`}
                    onClick={() => handleCellClick(idx)}
                    disabled={!isEmpty || isGameOver || agentThinking || currentTurn !== humanPlayer}
                  >
                    {cell === 1 && <span className="cell-symbol x-mark">X</span>}
                    {cell === 2 && <span className="cell-symbol o-mark">O</span>}

                    {isEmpty && showQOverlay && qVal !== undefined && (
                      <div className={`cell-q-badge ${qVal > 0 ? 'q-pos' : qVal < 0 ? 'q-neg' : 'q-zero'}`}>
                        Q: {qVal > 0 ? `+${qVal.toFixed(2)}` : qVal.toFixed(2)}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="board-bottom-controls">
            <label className="checkbox-control">
              <input
                type="checkbox"
                checked={showQOverlay}
                onChange={(e) => setShowQOverlay(e.target.checked)}
              />
              <span>Display learned Q-values on available squares</span>
            </label>
          </div>
        </div>

        {/* Right Side: Difficulty, Scoreboard & Explanations */}
        <div className="details-pane">
          {/* Difficulty Selection Card */}
          <div className="card control-box">
            <div className="card-header">
              <div className="card-title-group">
                <Brain size={16} className="text-cyan" />
                <h3 className="card-title">Agent Strength & Behavior</h3>
              </div>
            </div>

            <div className="difficulty-selector">
              <div
                className={`difficulty-pill ${difficulty === 'easy' ? 'active easy' : ''}`}
                onClick={() => setDifficulty('easy')}
              >
                <div className="diff-header">
                  <span className="diff-title">Easy</span>
                  <span className="diff-badge">50% Random</span>
                </div>
                <div className="diff-desc">
                  Frequent exploratory mistakes, misses blocks, friendly for learning.
                </div>
              </div>

              <div
                className={`difficulty-pill ${difficulty === 'medium' ? 'active medium' : ''}`}
                onClick={() => setDifficulty('medium')}
              >
                <div className="diff-header">
                  <span className="diff-title">Medium</span>
                  <span className="diff-badge">Balanced</span>
                </div>
                <div className="diff-desc">
                  Tactically sound (85% threat blocks), moderate exploration (12%).
                </div>
              </div>

              <div
                className={`difficulty-pill ${difficulty === 'hard' ? 'active hard' : ''}`}
                onClick={() => setDifficulty('hard')}
              >
                <div className="diff-header">
                  <span className="diff-title">Hard (Master)</span>
                  <span className="diff-badge">0% Exploration</span>
                </div>
                <div className="diff-desc">
                  Pure greedy policy from fully converged Q-table. Flawless defense.
                </div>
              </div>
            </div>

            {/* Play as X or O */}
            <div className="player-choice-section">
              <span className="section-label">Your Symbol:</span>
              <div className="choice-btn-group">
                <button
                  className={`btn-choice ${humanPlayer === 1 ? 'active' : ''}`}
                  onClick={() => switchPlayer(1)}
                  disabled={agentThinking}
                >
                  Play as X (First)
                </button>
                <button
                  className={`btn-choice ${humanPlayer === 2 ? 'active' : ''}`}
                  onClick={() => switchPlayer(2)}
                  disabled={agentThinking}
                >
                  Play as O (Second)
                </button>
              </div>
            </div>
          </div>

          {/* Match Scoreboard */}
          <div className="card scoreboard-card">
            <div className="scoreboard-title">Session Record</div>
            <div className="scoreboard-row">
              <div className="score-item">
                <div className="score-num text-green">{humanWins}</div>
                <div className="score-lbl">You (Wins)</div>
              </div>
              <div className="score-item">
                <div className="score-num text-white">{draws}</div>
                <div className="score-lbl">Draws</div>
              </div>
              <div className="score-item">
                <div className="score-num text-red">{agentWins}</div>
                <div className="score-lbl">Agent (Wins)</div>
              </div>
            </div>
          </div>

          {/* Move Rationale / Explanations */}
          <div className="card rationale-card">
            <div className="card-header">
              <div className="card-title-group">
                <Sparkles size={16} className="text-amber" />
                <h4 className="card-title">Agent Decision Rationale</h4>
              </div>
            </div>

            {lastAgentExplanation ? (
              <div className="rationale-content">
                <p className="explanation-text">{lastAgentExplanation}</p>
                {Object.keys(activeQValues).length > 0 && (
                  <div className="q-mini-table">
                    <span className="table-caption">Legal Move Q-Values:</span>
                    <div className="q-tag-list">
                      {Object.entries(activeQValues).map(([move, val]) => (
                        <span key={move} className="q-tag">
                          Cell {move}: <strong>{val > 0 ? `+${val.toFixed(2)}` : val.toFixed(2)}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-rationale">
                Make your move on the board to see the agent's real-time Q-value evaluation and strategic rationale.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
