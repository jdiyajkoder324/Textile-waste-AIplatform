# TextileIntel — Textile Waste Intelligence Platform (TWIP)

A full-stack platform for tracking, classifying, and generating sustainability intelligence from textile waste — built as a B.Tech final year major project.

TWIP helps **Industry**, **Recycler**, and **Admin** users log textile waste batches, automatically classify waste using ML models (damage detection, pattern/texture, waste category), and get actionable sustainability insights — carbon impact, circular economy scoring, resource recovery potential, and benchmarking — through role-based dashboards.

---

## ✨ Features

- **Role-Based Access Control (RBAC)** — Industry, Recycler, and Admin roles with tailored dashboards and permissions
- **Waste Batch Management** — Full CRUD for textile waste inventory with image upload
- **AI-Powered Waste Classification**
  - Damage Detection (CNN, EfficientNet-B0)
  - Pattern/Texture Recognition (CNN, EfficientNet-B0)
  - Waste Category Classification (proxy model)
  - Heuristic fallback when trained models aren't available
- **Sustainability Intelligence Engine**
  - Carbon impact calculator
  - Waste diversion tracking
  - Circular economy scoring
  - Resource recovery estimation
  - Environmental impact analysis
  - Industry benchmarking
  - Rules-based recommendation engine
- **Reporting** — Downloadable PDF (ReportLab) and Excel (OpenPyXL) reports via a Reports Center
- **Notifications** — Real-time-ish notification bell with polling
- **Modern UI** — React + Vite + Tailwind CSS with a custom eco green/mint design system

---

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python)
- PostgreSQL
- SQLAlchemy ORM
- Pydantic (schema validation)
- JWT-based authentication
- PyTorch (EfficientNet-B0 models, trained in Google Colab)
- Pytest (test suite)

**Frontend**
- React + Vite
- Tailwind CSS
- Custom design system (`GlassCard`, `StatCard` components; `paper` / `ink` / `fiber-*` design tokens)

**Deployment**
- Render (backend + frontend)

---

## 📁 Project Structure

```
TextileWasteIntelligencePltfrm/
├── backend/
│   ├── app/
│   │   ├── api/              # Route handlers (auth, users, waste, image, analytics...)
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Sustainability engine (carbon, diversion, circularity, etc.)
│   │   └── ml/                 # ML model registry + inference (with heuristic fallback)
│   ├── tests/                  # Pytest test suite
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Shared UI components (GlassCard, StatCard, NotificationBell...)
│   │   ├── pages/               # Role-based dashboards (Admin, Recycler, Manufacturer/Industry)
│   │   ├── layouts/             # DashboardLayout, sidebar navigation
│   │   └── api/                 # API client (uses VITE_API_BASE_URL)
│   └── package.json
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

# Set up environment variables (see below)
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

**Backend (`backend/.env`)**
```
DATABASE_URL=postgresql://user:password@localhost:5432/twip_db
JWT_SECRET_KEY=your-secret-key-here
```

**Frontend (`frontend/.env`)**
```
VITE_API_BASE_URL=http://localhost:8000
```

> ⚠️ In production (Render), set `VITE_API_BASE_URL` to your deployed backend URL, and ensure `JWT_SECRET_KEY` is set as a secure environment variable — never hardcoded.

---

## 🧪 Running Tests

```bash
cd backend
pytest
```

---

## 👥 User Roles

| Role | Capabilities |
|------|---------------|
| **Industry** | Log waste batches, upload images, view classification results, access sustainability insights |
| **Recycler** | View available waste batches, track recovery, access recycler-specific dashboard |
| **Admin** | Manage users, oversee all batches, access platform-wide analytics |

---

## 📊 ML Models

Three CNN models (built on EfficientNet-B0, trained in Google Colab with PyTorch) power the classification pipeline:

1. **Damage Detection** — assesses the condition/damage level of textile waste
2. **Pattern/Texture Recognition** — identifies fabric pattern and texture
3. **Waste Category Classification** — proxy model for categorizing waste type

If trained `.pth` weights aren't present, the system falls back to a heuristic-based classifier so the pipeline remains functional.

---

## 📄 Deployment

TWIP is deployed on [Render](https://render.com):
- **Backend**: FastAPI service connected to a managed PostgreSQL instance
- **Frontend**: Static site build (Vite) configured with SPA rewrite rules to handle client-side routing

---

## 📝 License

This project was built as a final year academic major project.

---

## 🙋 Author

**Diya J Koder**
GitHub: [jdiyajkoder324](https://github.com/jdiyajkoder324)
