# TypeScript Tic-Tac-Toe: Five in a Row

This Vite, React, and TypeScript project is a realistic sample workload for
manually evaluating DevCapsule configurations and for future automated IDE
end-to-end tests.

The baseline scaffold and game implementation were adapted from the shared
[ChatGPT conversation](https://chatgpt.com/share/6a535857-79b8-83ed-8c7a-ab0e41de05f9)
provided by the project owner. The implementation keeps its separation between
pure game logic, reducer-based state transitions, event handlers, and rendering.

## Run It

```bash
npm install
npm run dev
```

For a production build:

```bash
npm run build
```

To exercise the VSCodium and Claude Code configuration from the repository root:

```bash
devcapsule codium_with_claude run \
  --project devcapsule-src/tests/resources/sample_projects/typescript_tictactoe_5inrow
```

The application presents a 30×30 board. Two local players alternate `X` and
`0`; five contiguous marks win horizontally, vertically, or diagonally. The
winning segment is highlighted and the board locks until **Start new game** is
selected.
