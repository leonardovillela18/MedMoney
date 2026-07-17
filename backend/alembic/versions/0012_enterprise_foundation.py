"""enterprise sessions rbac and audit foundation"""
from alembic import op
import sqlalchemy as sa
revision='0012_enterprise_foundation';down_revision='0011_alerts';branch_labels=None;depends_on=None
def upgrade():
 for name,size in [('ip_address',64),('user_agent',500),('session_name',120)]:op.add_column('refresh_tokens',sa.Column(name,sa.String(size)))
 op.add_column('refresh_tokens',sa.Column('last_used_at',sa.DateTime(timezone=True)));op.add_column('refresh_tokens',sa.Column('rotated_from_id',sa.Uuid(),sa.ForeignKey('refresh_tokens.id')));op.create_index('ix_refresh_tokens_user_active','refresh_tokens',['user_id','revoked_at','expires_at'])
 op.create_table('roles',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('name',sa.String(40),nullable=False,unique=True),sa.Column('description',sa.String(200)));op.create_index('ix_roles_name','roles',['name'],unique=True)
 op.create_table('permissions',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('name',sa.String(80),nullable=False,unique=True),sa.Column('description',sa.String(200)));op.create_index('ix_permissions_name','permissions',['name'],unique=True)
 op.create_table('user_roles',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('role_id',sa.Uuid(),sa.ForeignKey('roles.id'),nullable=False),sa.UniqueConstraint('user_id','role_id',name='uq_user_role'));op.create_index('ix_user_roles_user_id','user_roles',['user_id']);op.create_index('ix_user_roles_role_id','user_roles',['role_id'])
 op.create_table('role_permissions',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('role_id',sa.Uuid(),sa.ForeignKey('roles.id'),nullable=False),sa.Column('permission_id',sa.Uuid(),sa.ForeignKey('permissions.id'),nullable=False),sa.UniqueConstraint('role_id','permission_id',name='uq_role_permission'));op.create_index('ix_role_permissions_role_id','role_permissions',['role_id']);op.create_index('ix_role_permissions_permission_id','role_permissions',['permission_id'])
 op.create_table('audit_logs',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id')),sa.Column('ip_address',sa.String(64)),sa.Column('user_agent',sa.String(500)),sa.Column('action',sa.String(80),nullable=False),sa.Column('entity',sa.String(80),nullable=False),sa.Column('entity_id',sa.String(80)),sa.Column('request_id',sa.String(80)),sa.Column('metadata_json',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
 for c in ('user_id','action','entity','entity_id','request_id','created_at'):op.create_index(f'ix_audit_logs_{c}','audit_logs',[c])
 import uuid
 roles=sa.table('roles',sa.column('id',sa.Uuid()),sa.column('name',sa.String()),sa.column('description',sa.String()))
 permissions=sa.table('permissions',sa.column('id',sa.Uuid()),sa.column('name',sa.String()),sa.column('description',sa.String()))
 user_roles=sa.table('user_roles',sa.column('id',sa.Uuid()),sa.column('user_id',sa.Uuid()),sa.column('role_id',sa.Uuid()))
 role_permissions=sa.table('role_permissions',sa.column('id',sa.Uuid()),sa.column('role_id',sa.Uuid()),sa.column('permission_id',sa.Uuid()))
 role_ids={name:uuid.uuid4() for name in ('USER','ADMIN','FINANCEIRO','CONTADOR','ASSISTENTE')}
 permission_names=('finance.read','finance.write','reports.read','settings.manage','users.manage','audit.read')
 permission_ids={name:uuid.uuid4() for name in permission_names}
 op.bulk_insert(roles,[{'id':value,'name':name,'description':f'Role {name}'} for name,value in role_ids.items()])
 op.bulk_insert(permissions,[{'id':value,'name':name,'description':name.replace('.',' ').title()} for name,value in permission_ids.items()])
 grants={'USER':('finance.read','finance.write','reports.read'),'FINANCEIRO':('finance.read','finance.write','reports.read'),'CONTADOR':('finance.read','reports.read'),'ASSISTENTE':('finance.read','finance.write'),'ADMIN':permission_names}
 op.bulk_insert(role_permissions,[{'id':uuid.uuid4(),'role_id':role_ids[role],'permission_id':permission_ids[permission]} for role,names in grants.items() for permission in names])
 existing_users=op.get_bind().execute(sa.text('SELECT id FROM users')).fetchall()
 if existing_users:op.bulk_insert(user_roles,[{'id':uuid.uuid4(),'user_id':row[0],'role_id':role_ids['USER']} for row in existing_users])
def downgrade():
 op.drop_table('audit_logs');op.drop_table('role_permissions');op.drop_table('user_roles');op.drop_table('permissions');op.drop_table('roles');op.drop_index('ix_refresh_tokens_user_active',table_name='refresh_tokens')
 for name in ('rotated_from_id','last_used_at','session_name','user_agent','ip_address'):op.drop_column('refresh_tokens',name)
