import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    org_name = Column(String, nullable=False)

    domains = relationship("Domain", back_populates="user")


class Domain(BaseModel):
    __tablename__ = "domains"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    domain_name = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    demo_mode = Column(Boolean, default=False)

    user = relationship("User", back_populates="domains")
    scans = relationship("Scan", back_populates="domain")


class Scan(BaseModel):
    __tablename__ = "scans"

    domain_id = Column(UUID(as_uuid=True), ForeignKey("domains.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    overall_score = Column(Integer, nullable=True)
    status = Column(String, default="pending")
    is_demo = Column(Boolean, default=False)

    domain = relationship("Domain", back_populates="scans")
    nodes = relationship("Node", back_populates="scan")
    edges = relationship("Edge", back_populates="scan")
    chains = relationship("Chain", back_populates="scan")
    findings = relationship("Finding", back_populates="scan")


class Node(BaseModel):
    __tablename__ = "nodes"

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    node_type = Column(String, nullable=False)
    label = Column(String, nullable=False)
    ip = Column(String, nullable=True)
    port = Column(Integer, nullable=True)
    severity = Column(String, default="low")
    raw_data = Column(JSONB, default={})

    scan = relationship("Scan", back_populates="nodes")


class Edge(BaseModel):
    __tablename__ = "edges"

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"))
    source_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    target_node_id = Column(UUID(as_uuid=True), ForeignKey("nodes.id"))
    relationship_type = Column(String, nullable=False)

    scan = relationship("Scan", back_populates="edges")


class Chain(BaseModel):
    __tablename__ = "chains"

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    rule_id = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    title = Column(String, nullable=False)
    explanation = Column(String, nullable=False)
    node_ids = Column(JSONB, default=[])

    scan = relationship("Scan", back_populates="chains")
    fixes = relationship("Fix", back_populates="chain")


class Fix(BaseModel):
    __tablename__ = "fixes"

    chain_id = Column(UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    command = Column(String, nullable=False)
    description = Column(String, nullable=False)

    chain = relationship("Chain", back_populates="fixes")


class Finding(BaseModel):
    __tablename__ = "findings"

    scan_id = Column(UUID(as_uuid=True), ForeignKey("scans.id"), nullable=False)
    chain_id = Column(UUID(as_uuid=True), ForeignKey("chains.id"), nullable=False)
    status = Column(String, default="open")
    assigned_to = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=True)
    verified_at = Column(DateTime, nullable=True)

    scan = relationship("Scan", back_populates="findings")