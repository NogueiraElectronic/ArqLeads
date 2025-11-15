"""
Admin Dashboard Routes.
Serves admin dashboard for lead management.
"""
from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
async def admin_dashboard():
    """Serve the admin dashboard HTML."""
    template_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "templates",
        "admin_dashboard.html"
    )
    return FileResponse(template_path)
