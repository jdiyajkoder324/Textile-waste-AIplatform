from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, require_role
from app.models.user import User
from app.schemas.analytics import (
    RecyclerDashboardResponse, SustainabilityDashboardResponse,
    ManufacturerDashboardResponse, AdminDashboardResponse,
)
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Dashboards"])


@router.get("/recycler", response_model=RecyclerDashboardResponse)
def recycler_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    material_type: Optional[str] = Query(None),
    waste_category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Recycler", "Admin")),
):
    return analytics_service.get_recycler_dashboard(db, start_date, end_date, material_type, waste_category)


@router.get("/sustainability", response_model=SustainabilityDashboardResponse)
def sustainability_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # any authenticated role
):
    return analytics_service.get_sustainability_dashboard(db, start_date, end_date)


@router.get("/manufacturer", response_model=ManufacturerDashboardResponse)
def manufacturer_dashboard(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Industry", "Admin")),
):
    return analytics_service.get_manufacturer_dashboard(db, current_user.id, start_date, end_date)


@router.get("/admin", response_model=AdminDashboardResponse)
def admin_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("Admin")),
):
    return analytics_service.get_admin_dashboard(db)