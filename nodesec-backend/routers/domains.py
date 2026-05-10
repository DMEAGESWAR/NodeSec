from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.jwt_handler import get_current_user
from models.models import User
from services.scan_service import DomainService
from schemas import DomainAddRequest, DomainResponse

router = APIRouter(prefix="/domains", tags=["domains"])


@router.post("/add", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def add_domain(
    request: DomainAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new domain to monitor."""
    return await DomainService.add_domain(request, current_user.id, db)


@router.get("/", response_model=list[DomainResponse])
async def list_domains(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all domains for the current user."""
    return await DomainService.list_user_domains(current_user.id, db)


@router.post("/{domain_id}/verify")
async def verify_domain(
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a domain as verified for scanning."""
    from uuid import UUID
    domain = await DomainService.get_user_domain(UUID(domain_id), current_user.id, db)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    domain.verified = True
    await db.flush()
    return {"status": "ok", "message": f"Domain {domain.domain_name} verified"}