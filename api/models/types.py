import enum
import uuid
from typing import Generic, TypeVar

from sqlalchemy import CHAR, JSON, VARCHAR, TypeDecorator
from sqlalchemy.dialects import mysql, postgresql

from configs import dify_config

from .engine import db


class StringUUID(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name in {"postgresql", "mysql"}:
            return str(value)
        else:
            return value.hex

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(postgresql.UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return str(value)


def adjusted_array(type):
    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return db.ARRAY(type)
    else:
        # Vanilla MySQL don't support array, we adapt it to JSON
        return JSON


def adjusted_jsonb():
    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return postgresql.JSONB
    else:
        return JSON


def adjusted_json_index(index_name, column_name):
    index_name = index_name or f"{column_name}_idx"

    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return db.Index(index_name, column_name, postgresql_using="gin")
    else:
        return None


def no_length_string():
    if "mysql" in dify_config.SQLALCHEMY_DATABASE_URI_SCHEME:
        return db.String(255)
    else:
        return db.String


def adjusted_text():
    if "mysql" in dify_config.SQLALCHEMY_DATABASE_URI_SCHEME:
        return mysql.LONGTEXT
    else:
        return db.TEXT


def uuid_default():
    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return {"server_default": db.text("uuid_generate_v4()")}
    else:
        return {"default": lambda: uuid.uuid4()}


def varchar_default(varchar):
    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return {"server_default": db.text(f"'{varchar}'::character varying")}
    else:
        return {"default": varchar}


def text_default(varchar):
    if dify_config.SQLALCHEMY_DATABASE_URI_SCHEME == "postgresql":
        return {"server_default": db.text(f"'{varchar}'::text")}
    else:
        return {"default": varchar}


_E = TypeVar("_E", bound=enum.StrEnum)


class EnumText(TypeDecorator, Generic[_E]):
    impl = VARCHAR
    cache_ok = True

    _length: int
    _enum_class: type[_E]

    def __init__(self, enum_class: type[_E], length: int | None = None):
        self._enum_class = enum_class
        max_enum_value_len = max(len(e.value) for e in enum_class)
        if length is not None:
            if length < max_enum_value_len:
                raise ValueError("length should be greater than enum value length.")
            self._length = length
        else:
            # leave some rooms for future longer enum values.
            self._length = max(max_enum_value_len, 20)

    def process_bind_param(self, value: _E | str | None, dialect):
        if value is None:
            return value
        if isinstance(value, self._enum_class):
            return value.value
        elif isinstance(value, str):
            self._enum_class(value)
            return value
        else:
            raise TypeError(f"expected str or {self._enum_class}, got {type(value)}")

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(VARCHAR(self._length))

    def process_result_value(self, value, dialect) -> _E | None:
        if value is None:
            return value
        if not isinstance(value, str):
            raise TypeError(f"expected str, got {type(value)}")
        return self._enum_class(value)

    def compare_values(self, x, y):
        if x is None or y is None:
            return x is y
        return x == y
