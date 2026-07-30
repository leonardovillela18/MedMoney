"""recurring income rules and generalized receivables"""
from alembic import op
import sqlalchemy as sa

revision='0016_recurring_incomes';down_revision='0015_tax_reserve_profile';branch_labels=None;depends_on=None
def upgrade():
    op.create_table('recurring_incomes',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('description',sa.String(160),nullable=False),sa.Column('income_type',sa.String(30),nullable=False),sa.Column('amount',sa.Numeric(12,2),nullable=False),sa.Column('frequency',sa.String(20),nullable=False),sa.Column('start_date',sa.Date(),nullable=False),sa.Column('end_date',sa.Date()),sa.Column('day_of_month',sa.Integer()),sa.Column('next_occurrence_date',sa.Date(),nullable=False),sa.Column('tax_treatment',sa.String(20),nullable=False),sa.Column('tax_reserve_percentage',sa.Numeric(6,3)),sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('notes',sa.Text()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
    for c in ('user_id','active','next_occurrence_date','income_type','tax_treatment','created_at'):op.create_index(f'ix_recurring_incomes_{c}','recurring_incomes',[c])
    with op.batch_alter_table('receivables') as batch:
        batch.alter_column('shift_id',existing_type=sa.Uuid(),nullable=True);batch.alter_column('contractor_id',existing_type=sa.Uuid(),nullable=True)
        batch.add_column(sa.Column('recurring_income_id',sa.Uuid()))
        batch.create_foreign_key('fk_receivables_recurring_income','recurring_incomes',['recurring_income_id'],['id'])
        batch.add_column(sa.Column('competence',sa.Date(),nullable=True));batch.add_column(sa.Column('tax_treatment',sa.String(20),nullable=True));batch.add_column(sa.Column('tax_reserve_percentage',sa.Numeric(6,3)))
    op.execute("UPDATE receivables SET competence = expected_date, tax_treatment = 'PJ_TAXABLE' WHERE competence IS NULL")
    with op.batch_alter_table('receivables') as batch:
        batch.alter_column('competence',existing_type=sa.Date(),nullable=False);batch.alter_column('tax_treatment',existing_type=sa.String(20),nullable=False,server_default='PJ_TAXABLE');batch.create_unique_constraint('uq_receivable_recurring_date',['recurring_income_id','expected_date'])
    for c in ('recurring_income_id','competence','tax_treatment'):op.create_index(f'ix_receivables_{c}','receivables',[c])
def downgrade():
    for c in ('tax_treatment','competence','recurring_income_id'):op.drop_index(f'ix_receivables_{c}',table_name='receivables')
    with op.batch_alter_table('receivables') as batch:
        batch.drop_constraint('uq_receivable_recurring_date',type_='unique');batch.drop_constraint('fk_receivables_recurring_income',type_='foreignkey');batch.drop_column('tax_reserve_percentage');batch.drop_column('tax_treatment');batch.drop_column('competence');batch.drop_column('recurring_income_id');batch.alter_column('contractor_id',existing_type=sa.Uuid(),nullable=False);batch.alter_column('shift_id',existing_type=sa.Uuid(),nullable=False)
    op.drop_table('recurring_incomes')
