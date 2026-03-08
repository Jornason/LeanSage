"""
SQLAlchemy ORM models for LeanProve AI
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users
    display_name = Column(String(100), nullable=False)
    avatar_url = Column(Text)
    github_id = Column(String(50), unique=True)
    role = Column(String(20), nullable=False, default="free")
    locale = Column(String(5), nullable=False, default="en")
    usage_count_month = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    proof_sessions = relationship("ProofSession", back_populates="user")
    search_logs = relationship("SearchLog", back_populates="user")
    error_diagnoses = relationship("ErrorDiagnosis", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    plan = Column(String(20), nullable=False, default="free")
    stripe_customer_id = Column(String(50))
    stripe_subscription_id = Column(String(50))
    status = Column(String(20), nullable=False, default="active")
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="subscription")


class ProofSession(Base):
    __tablename__ = "proof_sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    current_code = Column(Text)
    compilation_status = Column(String(20), default="pending")
    last_error = Column(Text)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="proof_sessions")
    snippets = relationship("LeanSnippet", back_populates="session")


class LeanSnippet(Base):
    __tablename__ = "lean_snippets"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    session_id = Column(UUID(as_uuid=False), ForeignKey("proof_sessions.id", ondelete="CASCADE"), nullable=False)
    version = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    source = Column(String(20), nullable=False, default="user_input")
    compilation_result = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ProofSession", back_populates="snippets")


class MathlibTheorem(Base):
    __tablename__ = "mathlib_theorems"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(300), unique=True, nullable=False)
    short_name = Column(String(100), nullable=False)
    type_signature = Column(Text, nullable=False)
    module_path = Column(String(300), nullable=False)
    doc_string = Column(Text)
    source_url = Column(Text)
    # embedding stored in Chroma; this column is for pgvector backup
    # embedding = Column(Vector(1536))  # requires pgvector extension
    mathlib_version = Column(String(20), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    query = Column(Text, nullable=False)
    results_count = Column(Integer)
    top_result = Column(String(300))
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="search_logs")


class ErrorDiagnosis(Base):
    __tablename__ = "error_diagnoses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="SET NULL"))
    input_code = Column(Text, nullable=False)
    error_message = Column(Text)
    diagnosis = Column(JSON, nullable=False, default=dict)
    fix_applied = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="error_diagnoses")
