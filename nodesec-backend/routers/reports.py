from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.jwt_handler import get_current_user
from models.models import User
from services.scan_service import ScanRepository
from reports.pdf_generator import generate_pdf

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{scan_id}/pdf")
async def get_pdf_report(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate and download a PDF report for a scan."""
    scan = await ScanRepository.get_scan(UUID(scan_id), current_user.id, db)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    pdf_bytes = await generate_pdf(scan, db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=scan-{scan_id[:8]}.pdf"},
    )