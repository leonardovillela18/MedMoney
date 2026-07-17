"""add intelligent alert center"""
from alembic import op
import sqlalchemy as sa
revision='0011_alerts';down_revision='0010_financial_goals';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('alerts',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('tipo',sa.String(70),nullable=False),sa.Column('categoria',sa.String(40),nullable=False),sa.Column('titulo',sa.String(180),nullable=False),sa.Column('descricao',sa.Text(),nullable=False),sa.Column('prioridade',sa.String(20),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('acao',sa.String(180),nullable=False),sa.Column('url_destino',sa.String(300),nullable=False),sa.Column('referencia_id',sa.Uuid(),nullable=False),sa.Column('origem',sa.String(50),nullable=False),sa.Column('lido_em',sa.DateTime(timezone=True)),sa.Column('resolvido_em',sa.DateTime(timezone=True)),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.UniqueConstraint('user_id','tipo','origem','referencia_id',name='uq_alert_rule_reference'))
 for c in ('user_id','tipo','categoria','prioridade','status','referencia_id','origem'):op.create_index(f'ix_alerts_{c}','alerts',[c])
def downgrade():op.drop_table('alerts')
