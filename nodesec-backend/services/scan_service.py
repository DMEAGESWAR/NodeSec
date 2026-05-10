import logging
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from models.models import Domain, Scan, Node, Edge, Chain, Fix, Finding
from schemas import DomainAddRequest, DomainResponse

logger = logging.getLogger("nodesec.services")


class DomainService:

    @staticmethod
    async def get_user_domain(domain_id: UUID, user_id: UUID, db: AsyncSession) -> Domain | None:
        result = await db.execute(
            select(Domain).where(Domain.id == domain_id, Domain.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def add_domain(request: DomainAddRequest, user_id: UUID, db: AsyncSession) -> DomainResponse:
        existing = await db.execute(
            select(Domain).where(Domain.domain_name == request.domain_name, Domain.user_id == user_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Domain already added")

        domain = Domain(
            user_id=user_id,
            domain_name=request.domain_name,
            verified=False,
        )
        db.add(domain)
        await db.flush()
        await db.refresh(domain)
        return DomainResponse.model_validate(domain)

    @staticmethod
    async def list_user_domains(user_id: UUID, db: AsyncSession) -> list[DomainResponse]:
        result = await db.execute(
            select(Domain).where(Domain.user_id == user_id).order_by(Domain.created_at.desc())
        )
        return [DomainResponse.model_validate(d) for d in result.scalars().all()]


class ScanRepository:

    @staticmethod
    async def create_scan(domain_id: UUID, is_demo: bool, db: AsyncSession) -> Scan:
        scan = Scan(domain_id=domain_id, is_demo=is_demo, status="running")
        db.add(scan)
        await db.flush()
        await db.refresh(scan)
        return scan

    @staticmethod
    async def get_scan(scan_id: UUID, user_id: UUID, db: AsyncSession) -> Scan | None:
        result = await db.execute(
            select(Scan)
            .join(Domain, Scan.domain_id == Domain.id)
            .where(Scan.id == scan_id, Domain.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def finalize_scan(
        scan_id: UUID, overall_score: int, status: str, db: AsyncSession
    ) -> None:
        result = await db.execute(select(Scan).where(Scan.id == scan_id))
        scan = result.scalar_one_or_none()
        if scan:
            scan.overall_score = overall_score
            scan.status = status
            scan.completed_at = datetime.utcnow()

    @staticmethod
    async def get_scans_for_domain(domain_id: UUID, db: AsyncSession) -> list[Scan]:
        result = await db.execute(
            select(Scan)
            .where(Scan.domain_id == domain_id)
            .order_by(Scan.created_at.desc())
            .limit(20)
        )
        return list(result.scalars().all())


class FindingRepository:

    @staticmethod
    async def create_findings(scan_id: UUID, chains: list[dict], db: AsyncSession) -> list[Finding]:
        findings = []
        for chain in chains:
            finding = Finding(scan_id=scan_id, chain_id=chain["chain_id"], status="open")
            db.add(finding)
            findings.append(finding)
        await db.flush()
        return findings

    @staticmethod
    async def get_findings_for_scan(scan_id: UUID, db: AsyncSession) -> list[Finding]:
        result = await db.execute(
            select(Finding).where(Finding.scan_id == scan_id).order_by(Finding.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_finding(finding_id: UUID, updates: dict, db: AsyncSession) -> Finding | None:
        result = await db.execute(select(Finding).where(Finding.id == finding_id))
        finding = result.scalar_one_or_none()
        if finding:
            for key, value in updates.items():
                if value is not None:
                    setattr(finding, key, value)
            await db.flush()
        return finding


class GraphRepository:

    @staticmethod
    async def save_nodes(scan_id: UUID, nodes_data: list[dict], db: AsyncSession) -> list[Node]:
        nodes = []
        for nd in nodes_data:
            node = Node(
                scan_id=scan_id,
                node_type=nd["node_type"],
                label=nd["label"],
                ip=nd.get("ip"),
                port=nd.get("port"),
                severity=nd.get("severity", "low"),
                raw_data=nd.get("raw_data", {}),
            )
            db.add(node)
            nodes.append(node)
        await db.flush()
        return nodes

    @staticmethod
    async def save_edges(scan_id: UUID, edges_data: list[dict], db: AsyncSession) -> list[Edge]:
        edges = []
        for ed in edges_data:
            edge = Edge(
                scan_id=scan_id,
                source_node_id=ed["source_node_id"],
                target_node_id=ed["target_node_id"],
                relationship_type=ed["relationship_type"],
            )
            db.add(edge)
            edges.append(edge)
        await db.flush()
        return edges

    @staticmethod
    async def save_chains(scan_id: UUID, chains_data: list[dict], fixes_map: dict, db: AsyncSession) -> list[Chain]:
        chains = []
        for i, cd in enumerate(chains_data):
            chain = Chain(
                scan_id=scan_id,
                rule_id=cd["rule_id"],
                severity=cd["severity"],
                title=cd["title"],
                explanation=cd["explanation"],
                node_ids=cd.get("node_ids", []),
            )
            db.add(chain)
            await db.flush()
            chains.append(chain)

            for fix in fixes_map.get(cd["rule_id"], []):
                f = Fix(
                    chain_id=chain.id,
                    step_number=fix["step_number"],
                    command=fix["command"],
                    description=fix["description"],
                )
                db.add(f)
            cd["chain_id"] = str(chain.id)
        await db.flush()
        return chains

    @staticmethod
    async def get_graph_data(scan_id: UUID, db: AsyncSession) -> dict:
        nodes_result = await db.execute(select(Node).where(Node.scan_id == scan_id))
        edges_result = await db.execute(select(Edge).where(Edge.scan_id == scan_id))
        chains_result = await db.execute(select(Chain).where(Chain.scan_id == scan_id))

        nodes = nodes_result.scalars().all()
        chains = chains_result.scalars().all()

        chain_dicts = []
        for c in chains:
            fixes_result = await db.execute(select(Fix).where(Fix.chain_id == c.id))
            fixes = fixes_result.scalars().all()
            chain_dicts.append({
                "id": str(c.id),
                "rule_id": c.rule_id,
                "severity": c.severity,
                "title": c.title,
                "explanation": c.explanation,
                "node_ids": c.node_ids,
                "fixes": [
                    {"step_number": f.step_number, "command": f.command, "description": f.description}
                    for f in fixes
                ],
            })

        return {
            "nodes": [
                {
                    "id": str(n.id), "node_type": n.node_type, "label": n.label,
                    "ip": n.ip, "port": n.port, "severity": n.severity,
                    "raw_data": n.raw_data,
                }
                for n in nodes
            ],
            "edges": [
                {
                    "id": str(e.id), "source_node_id": str(e.source_node_id),
                    "target_node_id": str(e.target_node_id),
                    "relationship_type": e.relationship_type,
                }
                for e in edges_result.scalars().all()
            ],
            "chains": chain_dicts,
        }