from __future__ import annotations
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base, db_session


class UserModel(Base):
    __tablename__ = 'user'

    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, server_default=sa.func.now(), nullable=False)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False)

    username = sa.Column(sa.String, nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)

    admin = sa.Column(sa.Boolean, default=False, server_default='false')


    @classmethod
    async def get_by_username(cls, username: str):
        async with db_session() as session:
            user = (await session.scalars(
                sa.select(UserModel)
                .where(UserModel.username == username)
            )).one_or_none()
        return user

    async def check_password(self, password: str):
        return self.password == password
