"""financial accounts and real versus forecast ledger"""
from alembic import op
import sqlalchemy as sa

revision='0018_financial_ledger';down_revision='0017_locations_specialties';branch_labels=None;depends_on=None

def upgrade():
    op.create_table('financial_accounts',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('institution_name',sa.String(120)),sa.Column('institution_code',sa.String(20)),sa.Column('account_name',sa.String(120),nullable=False),sa.Column('account_type',sa.String(20),nullable=False),sa.Column('last4',sa.String(4)),sa.Column('status',sa.String(20),nullable=False,server_default='ACTIVE'),sa.Column('is_manual',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('is_default',sa.Boolean(),nullable=False,server_default=sa.false()),sa.Column('integration_provider',sa.String(50)),sa.Column('external_account_id',sa.String(160)),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('deleted_at',sa.DateTime(timezone=True)))
    for c in ('user_id','account_type','status','deleted_at'):op.create_index(f'ix_financial_accounts_{c}','financial_accounts',[c])
    with op.batch_alter_table('cashflow_projection') as batch:
        batch.add_column(sa.Column('account_id',sa.Uuid()));batch.create_foreign_key('fk_cashflow_account','financial_accounts',['account_id'],['id'])
        batch.add_column(sa.Column('transaction_type',sa.String(20),nullable=False,server_default='OPERATING'));batch.add_column(sa.Column('direction',sa.String(10),nullable=False,server_default='INFLOW'));batch.add_column(sa.Column('notes',sa.String(500)));batch.add_column(sa.Column('transfer_group_id',sa.Uuid()))
    op.execute("UPDATE cashflow_projection SET direction = CASE WHEN valor < 0 THEN 'OUTFLOW' ELSE 'INFLOW' END")
    for c in ('account_id','transaction_type','direction','transfer_group_id'):op.create_index(f'ix_cashflow_projection_{c}','cashflow_projection',[c])
    op.create_table('bank_transactions',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('financial_account_id',sa.Uuid(),sa.ForeignKey('financial_accounts.id'),nullable=False),sa.Column('provider',sa.String(50),nullable=False),sa.Column('external_id',sa.String(160),nullable=False),sa.Column('transaction_date',sa.Date(),nullable=False),sa.Column('description',sa.String(200),nullable=False),sa.Column('raw_description',sa.Text()),sa.Column('amount',sa.Numeric(14,2),nullable=False),sa.Column('direction',sa.String(10),nullable=False),sa.Column('status',sa.String(20),nullable=False),sa.Column('matched_cashflow_id',sa.Uuid(),sa.ForeignKey('cashflow_projection.id')),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.UniqueConstraint('provider','external_id',name='uq_bank_transaction_external'))
    for c in ('user_id','financial_account_id','external_id','transaction_date','status'):op.create_index(f'ix_bank_transactions_{c}','bank_transactions',[c])

def downgrade():
    op.drop_table('bank_transactions')
    for c in ('transfer_group_id','direction','transaction_type','account_id'):op.drop_index(f'ix_cashflow_projection_{c}',table_name='cashflow_projection')
    with op.batch_alter_table('cashflow_projection') as batch:
        batch.drop_constraint('fk_cashflow_account',type_='foreignkey');batch.drop_column('transfer_group_id');batch.drop_column('notes');batch.drop_column('direction');batch.drop_column('transaction_type');batch.drop_column('account_id')
    op.drop_table('financial_accounts')
