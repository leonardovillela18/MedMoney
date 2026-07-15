"""initial users and refresh tokens"""
from alembic import op
import sqlalchemy as sa
revision='0001_initial'; down_revision=None; branch_labels=None; depends_on=None
def upgrade():
    op.create_table('users',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('name',sa.String(120),nullable=False),sa.Column('crm',sa.String(30),nullable=False),sa.Column('crm_uf',sa.String(2),nullable=False),sa.Column('email',sa.String(255),nullable=False),sa.Column('password_hash',sa.String(255),nullable=False),sa.Column('cnpj',sa.String(18),nullable=False),sa.Column('phone',sa.String(30),nullable=False),sa.Column('city',sa.String(100),nullable=False),sa.Column('state',sa.String(2),nullable=False),sa.Column('specialty',sa.String(100),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)),sa.UniqueConstraint('email'),sa.UniqueConstraint('cnpj'))
    op.create_index('ix_users_email','users',['email'])
    op.create_table('refresh_tokens',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('token_hash',sa.String(64),nullable=False),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),sa.Column('revoked_at',sa.DateTime(timezone=True)),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
    op.create_index('ix_refresh_tokens_token_hash','refresh_tokens',['token_hash'],unique=True);op.create_index('ix_refresh_tokens_user_id','refresh_tokens',['user_id'])
def downgrade():
    op.drop_table('refresh_tokens');op.drop_table('users')
