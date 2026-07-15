"""add shifts"""
from alembic import op
import sqlalchemy as sa
revision='0003_shifts';down_revision='0002_contractors';branch_labels=None;depends_on=None
def upgrade():
 op.create_table('shifts',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('contractor_id',sa.Uuid(),sa.ForeignKey('contractors.id'),nullable=False),sa.Column('title',sa.String(160)),sa.Column('type',sa.String(40),nullable=False),sa.Column('specialty',sa.String(100)),sa.Column('hospital_sector',sa.String(160)),sa.Column('city',sa.String(100)),sa.Column('state',sa.String(2)),sa.Column('date',sa.Date(),nullable=False),sa.Column('start_time',sa.Time(),nullable=False),sa.Column('end_time',sa.Time(),nullable=False),sa.Column('duration_hours',sa.Numeric(6,2),nullable=False),sa.Column('gross_value',sa.Numeric(12,2),nullable=False),sa.Column('estimated_net_value',sa.Numeric(12,2),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('payment_method',sa.String(30)),sa.Column('expected_payment_date',sa.Date()),sa.Column('notes',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
 for name,col in [('ix_shifts_user_id','user_id'),('ix_shifts_contractor_id','contractor_id'),('ix_shifts_date','date'),('ix_shifts_status','status'),('ix_shifts_city','city')]:op.create_index(name,'shifts',[col])
def downgrade():op.drop_table('shifts')
