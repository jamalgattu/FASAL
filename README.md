# AgriSetu — Frontend (SIH Problem 26033 MVP)

React + TypeScript + Tailwind CSS frontend for the AgriSetu SIH MVP. The
farmer and buyer services now include the real FastAPI client path, while
logistics and impact analytics intentionally remain simulated demo screens.
The mock data layer is still available for those screens and for offline UI
development.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL. To type-check / build:

```bash
npm run build
```

## Connect the FastAPI backend

Copy `.env.example` to `.env` and point it at the backend:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

The frontend calls the versioned API under `/api/v1`. The backend project is
in the sibling `fasal-backend/` directory in the recovered delivery bundle.

## Folder structure

```
src/
  types/index.ts        # Data contracts the future backend must implement
  data/mockData.ts       # Realistic mock dataset (listings, requirements,
                          # matches, orders, routes, impact metrics)
  services/               # Mock "API" layer — swap the function bodies for
                          # real fetch() calls later; signatures don't change
    farmerService.ts
    buyerService.ts
    logisticsService.ts
    analyticsService.ts
  components/             # Reusable UI
    ui.tsx                # Card, Button, Badge, StatCard, Field, etc.
    Layout.tsx             # App shell, role tabs, sub-navigation
    MatchCard.tsx          # Match score + reasons card (farmer & buyer)
    OrderTimeline.tsx       # Order status timeline
    RouteMapSVG.tsx         # Schematic (non-geographic) route diagram
  pages/
    common/Home.tsx         # Landing / role picker
    farmer/                 # Dashboard, AddProduce, MyListings,
                             # BuyerMatches, Orders, OrderDetails
    buyer/                  # Dashboard, PostRequirement, MyRequirements,
                             # AvailableSupply, RecommendedMatches, Orders,
                             # OrderDetails
    logistics/RoutePage.tsx # Baseline vs optimized route comparison
    analytics/ImpactDashboard.tsx
  App.tsx                  # Routes
  main.tsx / index.css     # Entry point, Tailwind

```

## What's real vs. simulated

- Matching, route optimization, and impact numbers are all **mock data**,
  clearly labeled in the UI where relevant.
- Route optimization will later use an established VRP/routing algorithm —
  **not AI**. AI is reserved for demand forecasting only (also mocked here).
- This is a coordination layer, not a generic e-commerce site, and not a
  claimed replacement for e-NAM.

## GitHub Pages deployment

The workflow in `.github/workflows/deploy.yml` builds and publishes this
frontend to GitHub Pages on every push to `main`. In the repository settings,
set Pages → Source to **GitHub Actions**. This app uses `HashRouter`, so routes
look like `https://<user>.github.io/<repo>/#/farmer`.

If the backend is hosted elsewhere, add the deployed frontend origin to the
backend's `CORS_ORIGINS` setting and set `VITE_API_BASE_URL` before the
workflow builds.

## Service boundary

Each function in `src/services/*.ts` returns a `Promise` shaped like the
types in `src/types/index.ts`. `farmerService.ts` and `buyerService.ts` use
the API client; logistics and analytics intentionally continue to use
synthetic data until those backend areas are implemented.
