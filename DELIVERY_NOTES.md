# Fasal recovery delivery

This bundle was reconstructed from the public Claude conversation snapshot
provided by the user after Claude became inaccessible.

## Contents

- `sih-frontend/` — React/Vite/Tailwind frontend
- `fasal-backend/` — FastAPI/SQLAlchemy backend and tests

## Verification performed here

- Restored 102 source/config files from the snapshot.
- Fixed the recovered frontend type errors in the order lifecycle and buyer
  profile mapper.
- Confirmed `npm run build` succeeds for the frontend.
- Confirmed all recovered Python files compile with `python -m compileall`.
- The backend test suite was not run in this environment because the sandbox
  could not install its pinned Python dependencies; run it in the backend
  virtual environment before deployment.

## Fastest path to a working demo

1. Deploy the backend with PostgreSQL and run `alembic upgrade head`.
2. Set the frontend `VITE_API_BASE_URL` to the backend's public URL.
3. Set backend `CORS_ORIGINS` to the exact GitHub Pages origin.
4. Push `sih-frontend/` to GitHub; its Actions workflow publishes GitHub Pages.

The logistics and impact pages are intentionally still demo-data screens.
Route optimization and forecasting were explicitly kept out of this phase.