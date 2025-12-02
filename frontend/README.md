# Frontend (React)

Status: scaffolded only. Planned stack: React + (later) Vite or other build tool; styling to be decided (could add Tailwind/Chakra/MUI later).

Structure:
- `src/index.tsx` entry
- `src/App.tsx` root component
- `public/index.html` template

Next steps:
1) Initialize tooling (e.g., `npm create vite@latest frontend -- --template react-ts` or wire existing package.json).
2) Add API client targeting FastAPI backend (proxy to http://localhost:8000).
3) Add base layout/theme and routing once endpoints stabilize.
