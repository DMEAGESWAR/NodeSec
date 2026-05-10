import asyncio
import json
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db, AsyncSessionLocal
from auth.jwt_handler import get_current_user
from models.models import User
from services.scan_service import DomainService, ScanRepository, GraphRepository
from workers.scan_worker import run_full_scan
from schemas import ScanStartRequest, ScanStartResponse, ScanResultResponse

router = APIRouter(prefix="/scan", tags=["scan"])


async def _run_scan_with_own_session(scan_id: UUID, domain_name: str, is_demo: bool):
    """Wrapper that gives the background scan worker its own DB session."""
    async with AsyncSessionLocal() as db:
        try:
            await run_full_scan(scan_id, domain_name, is_demo, db)
            await db.commit()
        except Exception:
            await db.rollback()
            raise


@router.post("/start", response_model=ScanStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_scan(
    request: ScanStartRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a new scan for a verified domain."""
    domain = await DomainService.get_user_domain(request.domain_id, current_user.id, db)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    if not request.is_demo and not domain.verified:
        raise HTTPException(status_code=422, detail="Domain not verified")

    scan = await ScanRepository.create_scan(domain.id, request.is_demo, db)

    asyncio.create_task(_run_scan_with_own_session(scan.id, domain.domain_name, request.is_demo))

    return ScanStartResponse(scan_id=scan.id, status="running")


@router.get("/{scan_id}/stream")
async def stream_scan(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """SSE endpoint that streams scan progress events."""
    scan = await ScanRepository.get_scan(UUID(scan_id), current_user.id, db)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    async def generate_events():
        from workers.scan_worker import get_event_queue, create_event_queue
        queue = get_event_queue(UUID(scan_id))
        if queue is None:
            queue = create_event_queue(UUID(scan_id))

        yield f"data: {json.dumps({'event': 'connected', 'data': {'scan_id': str(scan_id)}})}\n\n"

        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("event") == "complete" or event.get("event") == "error":
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'event': 'heartbeat', 'data': {}})}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.get("/{scan_id}/result")
async def get_scan_result(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get final scan results with graph data."""
    scan = await ScanRepository.get_scan(UUID(scan_id), current_user.id, db)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    graph = await GraphRepository.get_graph_data(scan.id, db)

    return {
        "id": str(scan.id),
        "domain_id": str(scan.domain_id),
        "status": scan.status,
        "overall_score": scan.overall_score,
        "started_at": scan.started_at.isoformat() if scan.started_at else None,
        "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "is_demo": scan.is_demo,
        "nodes": graph["nodes"],
        "edges": graph["edges"],
        "chains": graph["chains"],
    }


@router.get("/history/{domain_id}")
async def get_scan_history(
    domain_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get scan history for a domain."""
    domain = await DomainService.get_user_domain(UUID(domain_id), current_user.id, db)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    scans = await ScanRepository.get_scans_for_domain(domain.id, db)
    return [
        {
            "id": str(s.id),
            "status": s.status,
            "overall_score": s.overall_score,
            "started_at": s.started_at.isoformat() if s.started_at else None,
            "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            "is_demo": s.is_demo,
        }
        for s in scans
    ]