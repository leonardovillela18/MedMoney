import uuid
from datetime import datetime
from sqlalchemy import DateTime,ForeignKey,String,Text,UniqueConstraint,func
from sqlalchemy.orm import Mapped,mapped_column
from app.database.session import Base
class Role(Base):
 __tablename__='roles';id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);name:Mapped[str]=mapped_column(String(40),unique=True,index=True);description:Mapped[str|None]=mapped_column(String(200))
class Permission(Base):
 __tablename__='permissions';id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);name:Mapped[str]=mapped_column(String(80),unique=True,index=True);description:Mapped[str|None]=mapped_column(String(200))
class UserRole(Base):
 __tablename__='user_roles';__table_args__=(UniqueConstraint('user_id','role_id',name='uq_user_role'),);id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id'),index=True);role_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('roles.id'),index=True)
class RolePermission(Base):
 __tablename__='role_permissions';__table_args__=(UniqueConstraint('role_id','permission_id',name='uq_role_permission'),);id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);role_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('roles.id'),index=True);permission_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('permissions.id'),index=True)
class AuditLog(Base):
 __tablename__='audit_logs';id:Mapped[uuid.UUID]=mapped_column(primary_key=True,default=uuid.uuid4);user_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('users.id'),index=True);ip_address:Mapped[str|None]=mapped_column(String(64));user_agent:Mapped[str|None]=mapped_column(String(500));action:Mapped[str]=mapped_column(String(80),index=True);entity:Mapped[str]=mapped_column(String(80),index=True);entity_id:Mapped[str|None]=mapped_column(String(80),index=True);request_id:Mapped[str|None]=mapped_column(String(80),index=True);metadata_json:Mapped[str|None]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),index=True)
