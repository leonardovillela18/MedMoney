"""add intelligent cashflow projection"""
from alembic import op
import sqlalchemy as sa
revision='0007_cashflow_projection';down_revision='0006_tax_intelligence';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('cashflow_projection',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('data',sa.Date(),nullable=False),sa.Column('tipo',sa.String(30),nullable=False),sa.Column('origem',sa.String(30),nullable=False),sa.Column('origem_id',sa.Uuid(),nullable=False),sa.Column('descricao',sa.String(200),nullable=False),sa.Column('categoria',sa.String(80),nullable=False),sa.Column('valor',sa.Numeric(12,2),nullable=False),sa.Column('saldo_projetado',sa.Numeric(14,2),nullable=False,server_default='0'),sa.Column('status',sa.String(20),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)),sa.UniqueConstraint('user_id','origem','origem_id',name='uq_cashflow_source'))
 for c in ('user_id','data','tipo','origem','categoria','status'):op.create_index(f'ix_cashflow_projection_{c}','cashflow_projection',[c])
def downgrade():op.drop_table('cashflow_projection')
