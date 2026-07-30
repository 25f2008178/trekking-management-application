from sqlalchemy.orm import DeclarativeBase
from flask_security.models import sqla

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

class Model(DeclarativeBase):
    pass

sqla.FsModels.set_db_info(base_model=Model)

class Role(Model, sqla.FsRoleMixin):
    __tablename__ = "role"

class User(Model, sqla.FsUserMixin):
    __tablename__ = "user"
    name: Mapped[str] = mapped_column(String(255), nullable=False)