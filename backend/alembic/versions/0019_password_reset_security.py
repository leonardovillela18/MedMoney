"""single-use password reset tokens"""
from alembic import op
import sqlalchemy as sa
revision='0019_password_reset_security';down_revision='0018_financial_ledger';branch_labels=None;depends_on=None
def upgrade():
    op.create_table('password_reset_tokens',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('token_hash',sa.String(64),nullable=False,unique=True),sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),sa.Column('used_at',sa.DateTime(timezone=True)),sa.Column('revoked_at',sa.DateTime(timezone=True)),sa.Column('request_ip',sa.String(64)),sa.Column('user_agent',sa.String(500)),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
    for c in ('user_id','token_hash','expires_at'):op.create_index(f'ix_password_reset_tokens_{c}','password_reset_tokens',[c])
def downgrade():op.drop_table('password_reset_tokens')
