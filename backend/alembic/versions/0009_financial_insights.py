"""add cached financial insights"""
from alembic import op
import sqlalchemy as sa
revision='0009_financial_insights';down_revision='0008_expenses';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('financial_insights',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('tipo',sa.String(60),nullable=False),sa.Column('titulo',sa.String(180),nullable=False),sa.Column('descricao',sa.Text(),nullable=False),sa.Column('categoria',sa.String(40),nullable=False),sa.Column('severidade',sa.String(20),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('prioridade',sa.Integer(),nullable=False),sa.Column('acao_recomendada',sa.String(200),nullable=False),sa.Column('referencia',sa.String(200),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('dismissed_at',sa.DateTime(timezone=True)),sa.UniqueConstraint('user_id','referencia',name='uq_financial_insight_reference'))
 for c in ('user_id','tipo','categoria','severidade','status','prioridade'):op.create_index(f'ix_financial_insights_{c}','financial_insights',[c])
def downgrade():op.drop_table('financial_insights')
