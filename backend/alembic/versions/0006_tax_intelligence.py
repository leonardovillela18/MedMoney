"""add tax intelligence estimations and settings"""
from alembic import op
import sqlalchemy as sa
revision='0006_tax_intelligence';down_revision='0005_invoices';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('tax_settings',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('default_percentage',sa.Numeric(6,3),nullable=False,server_default='18'),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.UniqueConstraint('user_id',name='uq_tax_settings_user'))
 op.create_index('ix_tax_settings_user_id','tax_settings',['user_id'])
 op.create_table('tax_estimations',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('shift_id',sa.Uuid(),sa.ForeignKey('shifts.id')),sa.Column('invoice_id',sa.Uuid(),sa.ForeignKey('invoices.id')),sa.Column('receivable_id',sa.Uuid(),sa.ForeignKey('receivables.id')),sa.Column('base_calculo',sa.Numeric(12,2),nullable=False),sa.Column('percentual',sa.Numeric(6,3),nullable=False),sa.Column('valor_estimado',sa.Numeric(12,2),nullable=False),sa.Column('tipo',sa.String(20),nullable=False),sa.Column('competencia',sa.Date(),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('observacoes',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
 for c in ('user_id','shift_id','invoice_id','receivable_id','tipo','competencia','status'):op.create_index(f'ix_tax_estimations_{c}','tax_estimations',[c])
def downgrade():op.drop_table('tax_estimations');op.drop_table('tax_settings')
