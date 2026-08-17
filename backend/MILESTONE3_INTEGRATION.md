# Milestone 3 — Integration Steps

All files here are **additive** (same pattern as Milestone 2) — nothing in your
existing Milestone 1 / Milestone 2 code is modified.

## 1. Copy files into your project

Copy into `backend/app/`:

```
services/sustainability_engine.py
services/environmental_impact_engine.py
services/waste_scoring_engine.py
services/recommendation_engine.py
schemas/sustainability_schemas.py
models/sustainability_models.py
routers/sustainability_router.py
utils/sustainability_config.py
```

Copy into `backend/` (root, next to `main.py`):

```
create_milestone3_tables.py
```

## 2. Fix two import paths (only if needed)

Open these two files and confirm the imports match your actual paths:

- `app/models/sustainability_models.py` → `from app.database.database import Base`
- `app/routers/sustainability_router.py` → `from app.database.database import get_db`
  and `from app.utils.auth import get_current_user`

If your Milestone 1 `get_db` / `get_current_user` / `Base` live somewhere else
(e.g. `app/core/database.py`), just update these two lines — nothing else
needs touching.

## 3. Create the new tables

From `backend/` with venv activated:

```powershell
.\venv\Scripts\Activate.ps1
python create_milestone3_tables.py
```

## 4. Register the router in `main.py`

Add these two lines near your other router includes:

```python
from app.routers.sustainability_router import router as sustainability_router
app.include_router(sustainability_router)
```

## 5. Start the server

```powershell
uvicorn app.main:app --reload
```

Test endpoints:

- `POST http://127.0.0.1:8000/api/sustainability/analyze`
- `GET  http://127.0.0.1:8000/api/dashboard/summary`
- `GET  http://127.0.0.1:8000/health`

Sample body for `/api/sustainability/analyze`:

```json
{
  "material_type": "cotton",
  "weight_kg": 15.5,
  "is_recycled": true,
  "distance_km": 120,
  "recycled_kg": 10,
  "reused_kg": 2,
  "recovered_kg": 1,
  "landfilled_kg": 2.5,
  "material_purity": 80,
  "contamination_level": 15,
  "damage_level": 20,
  "fabric_condition": 75,
  "durability": 70,
  "usability": 80,
  "environmental_benefit": 70,
  "recoverability": 75,
  "recycling_efficiency": 65,
  "fiber_recovery": 70,
  "fabric_quality": 72,
  "resource_value": 65,
  "processing_feasibility": 68
}
```

## 6. Frontend

See `frontend/MILESTONE3_FRONTEND.md` for wiring the six new pages + routes.
