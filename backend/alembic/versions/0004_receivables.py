"""add receivables"""
from alembic import op
import sqlalchemy as sa
revision='0004_receivables';down_revision='0003_shifts';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('receivables',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('shift_id',sa.Uuid(),sa.ForeignKey('shifts.id'),nullable=False),sa.Column('contractor_id',sa.Uuid(),sa.ForeignKey('contractors.id'),nullable=False),sa.Column('expected_value',sa.Numeric(12,2),nullable=False),sa.Column('received_value',sa.Numeric(12,2),nullable=False,server_default='0'),sa.Column('remaining_balance',sa.Numeric(12,2),nullable=False),sa.Column('expected_date',sa.Date(),nullable=False),sa.Column('received_date',sa.Date()),sa.Column('status',sa.String(30),nullable=False),sa.Column('receipt_method',sa.String(30)),sa.Column('receipt_url',sa.String(500)),sa.Column('notes',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
 for n,c in [('ix_receivables_user_id','user_id'),('ix_receivables_shift_id','shift_id'),('ix_receivables_contractor_id','contractor_id'),('ix_receivables_status','status')]:op.create_index(n,'receivables',[c])
def downgrade():op.drop_table('receivables')
