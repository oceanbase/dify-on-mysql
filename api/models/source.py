import json

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from models.base import Base

from .engine import db
from .types import StringUUID, adjusted_json_index, adjusted_jsonb, uuid_default, adjusted_text


class DataSourceOauthBinding(Base):
    __tablename__ = "data_source_oauth_bindings"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="source_binding_pkey"),
        db.Index("source_binding_tenant_id_idx", "tenant_id"),
        adjusted_json_index("source_info_idx", "source_info"),
    )

    id = mapped_column(StringUUID, **uuid_default())
    tenant_id = mapped_column(StringUUID, nullable=False)
    access_token = mapped_column(db.String(255), nullable=False)
    provider = mapped_column(db.String(255), nullable=False)
    source_info = mapped_column(adjusted_jsonb(), nullable=False)
    created_at = mapped_column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = mapped_column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    disabled = mapped_column(db.Boolean, nullable=True, server_default=db.text("false"))


class DataSourceApiKeyAuthBinding(Base):
    __tablename__ = "data_source_api_key_auth_bindings"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="data_source_api_key_auth_binding_pkey"),
        db.Index("data_source_api_key_auth_binding_tenant_id_idx", "tenant_id"),
        db.Index("data_source_api_key_auth_binding_provider_idx", "provider"),
    )

    id = mapped_column(StringUUID, **uuid_default())
    tenant_id = mapped_column(StringUUID, nullable=False)
    category = mapped_column(db.String(255), nullable=False)
    provider = mapped_column(db.String(255), nullable=False)
    credentials = mapped_column(adjusted_text(), nullable=True)  # JSON
    created_at = mapped_column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    updated_at = mapped_column(db.DateTime, nullable=False, server_default=func.current_timestamp())
    disabled = mapped_column(db.Boolean, nullable=True, server_default=db.text("false"))

    def to_dict(self):
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "category": self.category,
            "provider": self.provider,
            "credentials": json.loads(self.credentials),
            "created_at": self.created_at.timestamp(),
            "updated_at": self.updated_at.timestamp(),
            "disabled": self.disabled,
        }
