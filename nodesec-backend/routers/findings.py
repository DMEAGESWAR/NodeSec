from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.jwt_handler import get_current_user
from models.models import User
from services.scan_service import FindingRepository, ScanRepository
from schemas import FindingUpdateRequest, FindingResponse

router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/{scan_id}", response_model=list[FindingResponse])
async def get_findings(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all findings for a scan."""
    scan = await ScanRepository.get_scan(UUID(scan_id), current_user.id, db)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    findings = await FindingRepository.get_findings_for_scan(scan.id, db)
    return [FindingResponse.model_validate(f) for f in findings]


@router.patch("/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: str,
    request: FindingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a finding's status or assignment."""
    updates = request.model_dump(exclude_none=True)
    finding = await FindingRepository.update_finding(UUID(finding_id), updates, db)
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingResponse.model_validate(finding)