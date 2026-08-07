import React, { useCallback, useMemo, useReducer } from "react";

const BOARD_SIZE = 30;
const WIN_LENGTH = 5;

type Player = "X" | "0";
type Cell = Player | null;
type Coord = { r: number; c: number };
type GameState = {
  size: number;
  board: Cell[][];
  current: Player;
  winner: Player | null;
  winningLine: Coord[] | null;
  moves: number;
};
type Action = { type: "PLAY"; r: number; c: number } | { type: "NEW_GAME" };

/* Game logic: pure functions. */
function createEmptyBoard(size: number): Cell[][] {
  return Array.from({ length: size }, () => Array<Cell>(size).fill(null));
}

function inBounds(size: number, r: number, c: number): boolean {
  return r >= 0 && r < size && c >= 0 && c < size;
}

function getCell(board: Cell[][], r: number, c: number): Cell {
  return board[r]![c] ?? null;
}

function setCellImmutable(board: Cell[][], r: number, c: number, value: Cell): Cell[][] {
  const next = board.slice();
  const nextRow = next[r]!.slice();
  nextRow[c] = value;
  next[r] = nextRow;
  return next;
}

function findWinningLineFromLastMove(
  board: Cell[][],
  r: number,
  c: number,
  player: Player,
  winLength: number,
): Coord[] | null {
  const size = board.length;
  const directions: Array<[number, number]> = [[0, 1], [1, 0], [1, 1], [1, -1]];

  for (const [dr, dc] of directions) {
    const line: Coord[] = [];
    let rr = r;
    let cc = c;
    while (inBounds(size, rr - dr, cc - dc) && getCell(board, rr - dr, cc - dc) === player) {
      rr -= dr;
      cc -= dc;
    }
    while (inBounds(size, rr, cc) && getCell(board, rr, cc) === player) {
      line.push({ r: rr, c: cc });
      rr += dr;
      cc += dc;
    }
    if (line.length >= winLength) {
      const index = line.findIndex((point) => point.r === r && point.c === c);
      if (index === -1) continue;
      let start = Math.max(0, index - (winLength - 1));
      start = Math.min(start, line.length - winLength);
      return line.slice(start, start + winLength);
    }
  }
  return null;
}

/* State management: reducer-owned state transitions. */
function initialState(size: number): GameState {
  return {
    size,
    board: createEmptyBoard(size),
    current: "X",
    winner: null,
    winningLine: null,
    moves: 0,
  };
}

function reducer(state: GameState, action: Action): GameState {
  if (action.type === "NEW_GAME") return initialState(state.size);
  if (state.winner || !inBounds(state.size, action.r, action.c)) return state;
  if (state.board[action.r]![action.c] !== null) return state;

  const player = state.current;
  const board = setCellImmutable(state.board, action.r, action.c, player);
  const winningLine = findWinningLineFromLastMove(board, action.r, action.c, player, WIN_LENGTH);
  return {
    ...state,
    board,
    current: winningLine ? player : player === "X" ? "0" : "X",
    winner: winningLine ? player : null,
    winningLine,
    moves: state.moves + 1,
  };
}

/* Rendering: presentational board and cell components. */
type CellViewProps = {
  value: Cell;
  isWinning: boolean;
  disabled: boolean;
  onClick: () => void;
};

const CellView = React.memo(function CellView({ value, isWinning, disabled, onClick }: CellViewProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      aria-label={value ? `Cell ${value}` : "Empty cell"}
      style={{
        width: 22, height: 22, lineHeight: "22px", padding: 0,
        border: "1px solid rgba(0,0,0,0.15)",
        background: isWinning ? "rgba(255, 215, 0, 0.45)" : "white",
        cursor: disabled ? "default" : "pointer",
        fontFamily: "ui-sans-serif, system-ui, sans-serif", fontSize: 14,
        fontWeight: 700, userSelect: "none",
      }}
    >
      {value ?? ""}
    </button>
  );
});

type BoardViewProps = {
  board: Cell[][];
  winningSet: Set<string>;
  locked: boolean;
  onPlay: (r: number, c: number) => void;
};

function BoardView({ board, winningSet, locked, onPlay }: BoardViewProps) {
  return (
    <div style={{
      display: "grid", gridTemplateColumns: `repeat(${board.length}, 22px)`, gap: 0,
      background: "rgba(0,0,0,0.06)", padding: 6, borderRadius: 10, width: "max-content",
    }}>
      {board.map((row, r) => row.map((value, c) => {
        const key = `${r},${c}`;
        return <CellView key={key} value={value} isWinning={winningSet.has(key)}
          disabled={locked || value !== null} onClick={() => onPlay(r, c)} />;
      }))}
    </div>
  );
}

/* Event handling and composition. */
export default function App() {
  const [state, dispatch] = useReducer(reducer, undefined, () => initialState(BOARD_SIZE));
  const onPlay = useCallback((r: number, c: number) => dispatch({ type: "PLAY", r, c }), []);
  const onNewGame = useCallback(() => dispatch({ type: "NEW_GAME" }), []);
  const locked = state.winner !== null;
  const winningSet = useMemo(() => new Set((state.winningLine ?? []).map(({ r, c }) => `${r},${c}`)),
    [state.winningLine]);
  const status = state.winner ? `Winner: ${state.winner} (5 in a row)` : `Turn: ${state.current}`;

  return (
    <div style={{ padding: 16, display: "grid", gap: 12, fontFamily: "ui-sans-serif, system-ui, sans-serif" }}>
      <header style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <h1 style={{ margin: 0, fontSize: 18 }}>5-in-a-row Tic-Tac-Toe (30×30)</h1>
        <button type="button" onClick={onNewGame} style={{
          padding: "8px 12px", borderRadius: 10, border: "1px solid rgba(0,0,0,0.15)",
          background: "white", cursor: "pointer", fontWeight: 700,
        }}>Start new game</button>
        <div role="status" aria-live="polite" style={{
          padding: "8px 12px", borderRadius: 10, border: "1px solid rgba(0,0,0,0.10)",
          background: locked ? "rgba(34,197,94,0.10)" : "rgba(59,130,246,0.10)", fontWeight: 700,
        }}>{status}</div>
        <div style={{ opacity: 0.7, fontWeight: 600 }}>Moves: {state.moves}</div>
      </header>
      <div style={{ maxWidth: "100%", overflow: "auto", border: "1px solid rgba(0,0,0,0.10)",
        borderRadius: 12, padding: 10, background: "rgba(0,0,0,0.02)" }}>
        <BoardView board={state.board} winningSet={winningSet} locked={locked} onPlay={onPlay} />
      </div>
      <footer style={{ opacity: 0.75, fontSize: 13 }}>
        Click to place <b>X</b> / <b>0</b>. First to get <b>5</b> consecutive marks wins
        (horizontal, vertical, or diagonal).
      </footer>
    </div>
  );
}
