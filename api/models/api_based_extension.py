import enum
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .types import StringUUID, uuid_default, adjusted_text


class APIBasedExtensionPoint(enum.Enum):
    APP_EXTERNAL_DATA_TOOL_QUERY = "app.external_data_tool.query"
    PING = "ping"
    APP_MODERATION_INPUT = "app.moderation.input"
    APP_MODERATION_OUTPUT = "app.moderation.output"


class APIBasedExtension(Base):
    __tablename__ = "api_based_extensions"
    __table_args__ = (
        sa.PrimaryKeyConstraint("id", name="api_based_extension_pkey"),
        sa.Index("api_based_extension_tenant_idx", "tenant_id"),
    )

    id = mapped_column(StringUUID, **uuid_default())
    tenant_id = mapped_column(StringUUID, nullable=False)
    name = mapped_column(String(255), nullable=False)
    api_endpoint = mapped_column(String(255), nullable=False)
    api_key = mapped_column(adjusted_text(), nullable=False)
    created_at = mapped_column(DateTime, nullable=False, server_default=func.current_timestamp())
