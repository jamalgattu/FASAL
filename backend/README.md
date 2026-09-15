# Fasal Backend (SIH Problem 26033)

FastAPI + PostgreSQL backend for the Fasal farmer-buyer-logistics
coordination platform. Implements real auth, CRUD, a rule-based
supply-demand matching engine, and a strict order lifecycle with
atomic inventory handling. No ML, no route optimization yet — both are
explicitly out of scope for this phase.

## Quick start

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit DATABASE_URL / SECRET_KEY
alembic upgrade head            # creates all tables
uvicorn app.main:app --reload
```

Interactive API docs: `http://localhost:8000/docs` (Swagger) or
`/redoc`. Health check: `GET /`.

Run the test suite (uses a throwaway SQLite file per test, not your
real Postgres DB):

```bash
pytest -v
```

> I built and reviewed every file by hand but could not actually run
> `pip install` / `pytest` myself — no network access in the sandbox
> this was written in. Run the test suite yourself before building
> further on top of this; there's a decent chance something needs a
> small fix on first run.

## 1. Folder structure

```
app/
  main.py                 FastAPI app, CORS, exception handlers, router mount
  config.py                Settings from environment variables
  database.py               Engine/session/Base
  core/
    security.py              Password hashing, JWT
    exceptions.py             Domain exceptions -> HTTP responses
  models/                   SQLAlchemy ORM models, grouped by domain
    enums.py                  Every enum (roles, statuses, grades, ...)
    identity.py                User, Farmer (also represents FPOs), Buyer
    catalog.py                  Crop, ProduceListing, BuyerRequirement
    matching.py                  Match
    orders.py                     Order, OrderStatusHistory (audit trail)
    logistics.py                   Vehicle, Delivery
  schemas/                  Pydantic request/response models (mirrors models/)
  crud/                      DB access functions, one module per domain
  services/
    matching_engine.py        Supply-demand scoring + allocation
    order_state_machine.py     Transition validation + audit trail
    inventory.py                 Atomic reserve/release/finalize
  api/v1/                   One router per API group (see below)
alembic/                    Migrations (0001_initial creates everything)
tests/                      pytest — matching engine, state machine, concurrency
```

## 2. Database schema

**users** — id, email (unique), hashed_password, full_name, phone,
role (farmer/buyer/admin), is_active, timestamps

**farmers** — id, user_id (FK, unique), is_fpo, org_name, village,
district, state, lat, lng
*Farmers and FPOs share one table — `is_fpo` distinguishes them. The
`/fpos` API is a filtered view over this same table, not a separate
entity, since an FPO is operationally a farmer account that aggregates
produce on behalf of members.*

**buyers** — id, user_id (FK, unique), buyer_type, org_name, district,
state, lat, lng

**crops** — id, name (unique), default_unit

**produce_listings** — id, farmer_id (FK), crop_id (FK), variety,
quantity, quantity_reserved, quantity_sold, unit, price_per_unit,
quality_grade, harvest_date, available_date, location fields, status,
notes
*`available_quantity` is a computed property (`quantity -
quantity_reserved - quantity_sold`), never stored. DB-level
`CHECK` constraints additionally enforce `quantity_reserved +
quantity_sold <= quantity` and all three columns `>= 0` as a
defense-in-depth backstop under the application-level checks.*

**buyer_requirements** — id, buyer_id (FK), crop_id (FK), variety,
required_quantity, fulfilled_quantity, unit, acceptable_price,
required_quality, delivery location fields, required_delivery_date,
status
*`remaining_quantity` is likewise computed, with a `CHECK
(fulfilled_quantity <= required_quantity)` constraint.*

**matches** — id, listing_id (FK), requirement_id (FK),
allocated_quantity, match_score + the 5 individual factor scores,
distance_km, reasons (JSON), explanation, status
*One requirement can have many Match rows — one per supplier, when the
engine splits it across multiple suppliers.*

**orders** — id, match_id (FK, unique, nullable), listing_id,
requirement_id, farmer_id, buyer_id, crop_id, variety, quantity, unit,
agreed_price, total_value, quality_grade, pickup/delivery location
fields, required_delivery_date, status, version, created_by_user_id

**order_status_history** — id, order_id (FK), from_status, to_status,
changed_by_user_id, note, created_at
*Immutable audit trail — one row per transition, never updated or
deleted.*

**vehicles** — id, registration_no (unique), vehicle_type,
capacity_kg, current_load_kg, is_active

**deliveries** — id, order_id (FK, unique), vehicle_id (FK, nullable),
status, sequence, picked_up_at, delivered_at, notes

## 3. API contract (summary)

All routes are under `/api/v1`. Full request/response schemas are in
the auto-generated `/docs`.

| Group | Routes |
|---|---|
| `/auth` | `POST /register/farmer`, `POST /register/buyer`, `POST /login` (OAuth2 form), `GET /me` |
| `/farmers` | `GET /`, `GET /me`, `PATCH /me`, `GET /{id}` |
| `/fpos` | `GET /`, `GET /{id}` — same table as `/farmers`, filtered to `is_fpo=true` |
| `/buyers` | `GET /`, `GET /me`, `PATCH /me`, `GET /{id}` |
| `/crops` | `GET /`, `POST /` |
| `/produce` | `POST /`, `GET /` (filters: farmer_id, crop_id, status, only_available), `GET /{id}`, `PATCH /{id}` |
| `/requirements` | `POST /`, `GET /` (filters: buyer_id, crop_id, status), `GET /{id}`, `PATCH /{id}` |
| `/matches` | `GET /preview/{requirement_id}` (read-only, runs the engine live), `POST /generate/{requirement_id}` (persists proposals), `GET /`, `GET /{id}`, `POST /{id}/accept`, `POST /{id}/reject` |
| `/orders` | `POST /` (from an accepted match), `GET /` (own orders), `GET /{id}`, `POST /{id}/transition` |
| `/vehicles` | `POST /` (admin), `GET /`, `GET /{id}`, `PATCH /{id}` (admin) |
| `/deliveries` | `POST /{order_id}/assign` (admin), `GET /{order_id}`, `PATCH /{order_id}/status` (admin) |

**Auth**: JWT bearer tokens, 24h expiry by default. Registration
creates the `User` row and the role-specific profile (`Farmer` or
`Buyer`) together in one call.

**Ownership enforcement**: every write endpoint checks the resource
belongs to the caller (or the caller is `admin`) before allowing a
change — implemented as an explicit check in each router, not a
blanket middleware, so the rule is visible at each call site.

## Business rules — where they live

- **Inventory can't go negative** — `services/inventory.py`, backed by
  a DB `CHECK` constraint as a second line of defense.
- **Orders can partially fulfill requirements** — `BuyerRequirement.fulfilled_quantity`
  accumulates across multiple Orders/Matches; a requirement can sit at
  `MATCHED` (partially filled) before reaching `FULFILLED`.
- **Users can't modify others' resources** — ownership checks in every
  `PATCH`/transition endpoint in `api/v1/`.
- **Cancelled orders release reserved inventory** — `order_state_machine.py`
  calls `inventory.release()` whenever a reserved-or-later order moves
  to `CANCELLED`/`REJECTED`.
- **Completed orders can't be arbitrarily modified** — `COMPLETED`,
  `CANCELLED`, and `REJECTED` are terminal in `ALLOWED_TRANSITIONS`;
  attempting any transition out of them raises `InvalidStateTransitionError`.

## Matching engine

`services/matching_engine.py`. Five weighted factors — price (25%),
distance (20%), quality (20%), availability (20%), reliability (15%)
by default, all configurable per-request via query params on
`GET /matches/preview/{id}` or by constructing `MatchWeights`
programmatically. Weights are auto-normalized if they don't sum to 1.

Crop mismatch, below-minimum quality, and can't-be-ready-in-time are
hard exclusions; everything else is scored, not filtered, which is
what keeps this from just picking the cheapest supplier — see
`test_does_not_simply_pick_the_cheapest_supplier` in the test suite.

`allocate_supply()` greedily fills a requirement from
highest-scoring candidates first, splitting across as many suppliers
as needed — this is what makes the "2000kg across 3 suppliers" example
from the spec work.

## Order lifecycle

```
MATCHED -> ACCEPTED -> RESERVED -> CONFIRMED -> PICKUP_ASSIGNED
  -> PICKED_UP -> IN_TRANSIT -> DELIVERED -> COMPLETED
```
Plus `CANCELLED`, `REJECTED`, `PARTIALLY_FULFILLED`, `DISPUTED` as
side branches — see `ALLOWED_TRANSITIONS` in
`services/order_state_machine.py` for the exact graph.

Every transition locks the Order row (`SELECT ... FOR UPDATE`),
re-validates against the *current* status (not whatever the caller
assumed), applies any inventory side effect in the same transaction,
and writes one audit row — all committed together or not at all.

## Known limitations / what's next

- Matching + route optimization here are rule-based, not ML — by
  design, per this phase's scope.
- No refresh-token flow — access tokens just expire after 24h and the
  user logs in again.
- Role-per-transition permissions are simplified: any party to an
  order (farmer or buyer) can currently perform any valid transition.
  Tightening this (e.g. only a farmer can mark `PICKED_UP`) is a
  straightforward follow-up in `order_state_machine._check_authorization`.
- Concurrency tests run against SQLite with `isolation_level="IMMEDIATE"`
  (whole-database lock) as a stand-in for Postgres's `SELECT ... FOR
  UPDATE` (per-row lock) — same code path, coarser granularity. Worth
  re-running the same scenarios against a real Postgres instance once
  one's available.
