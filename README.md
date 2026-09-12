# AgriSetu — Frontend (SIH Problem 26033 MVP)

Frontend-only prototype: React + TypeScript + Tailwind CSS. No backend, no
auth, no real APIs, no ML — all data comes from a mock service layer in
`src/services/` backed by `src/data/mockData.ts`.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL. To type-check / build:

```bash
npm run build
```

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

## Swapping in a real backend later

Each function in `src/services/*.ts` returns a `Promise` shaped exactly like
the types in `src/types/index.ts`. Replace the function bodies with
`fetch('/api/...')` calls returning the same shapes — no component code
needs to change.
