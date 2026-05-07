import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ImportStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    success = "success"
    failed = "failed"


class DataImportBatch(Base):
    __tablename__ = "data_import_batches"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)

    source_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("external_data_sources.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    uploaded_by_id: Mapped[UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[ImportStatus] = mapped_column(
        Enum(ImportStatus, name="import_status"),
        default=ImportStatus.pending,
        nullable=False,
        index=True,
    )

    rows_total: Mapped[int] = mapped_column(default=0, nullable=False)
    rows_success: Mapped[int] = mapped_column(default=0, nullable=False)
    rows_failed: Mapped[int] = mapped_column(default=0, nullable=False)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    source = relationship("ExternalDataSource", back_populates="import_batches")
    uploaded_by = relationship("User", back_populates="import_batches")
    feature_snapshots = relationship("RiskFeatureSnapshot", back_populates="import_batch")