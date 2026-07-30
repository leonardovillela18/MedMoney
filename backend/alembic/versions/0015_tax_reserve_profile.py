"""tax reserve snapshots and accountant-provided profile"""
from alembic import op
import sqlalchemy as sa

revision='0015_tax_reserve_profile';down_revision='0014_contractor_default_value';branch_labels=None;depends_on=None

def upgrade():
    op.add_column('shifts',sa.Column('tax_reserve_percentage',sa.Numeric(6,3),nullable=True))
    op.add_column('shifts',sa.Column('tax_treatment',sa.String(20),nullable=False,server_default='PJ_TAXABLE'))
    op.create_index('ix_shifts_tax_treatment','shifts',['tax_treatment'])
    op.add_column('tax_settings',sa.Column('simples_nacional',sa.Boolean(),nullable=True))
    op.add_column('tax_settings',sa.Column('simples_annex',sa.String(10),nullable=False,server_default='UNKNOWN'))
    op.add_column('tax_settings',sa.Column('fator_r',sa.Numeric(6,3),nullable=True))
    op.add_column('tax_settings',sa.Column('rbt12',sa.Numeric(14,2),nullable=True))
    op.add_column('tax_settings',sa.Column('das_effective_percentage',sa.Numeric(6,3),nullable=True))
    op.add_column('tax_settings',sa.Column('iss_effective_percentage',sa.Numeric(6,3),nullable=True))
    op.add_column('tax_settings',sa.Column('has_separate_darfs',sa.Boolean(),nullable=False,server_default=sa.false()))
    op.add_column('tax_settings',sa.Column('separate_darfs_json',sa.Text(),nullable=True))
    op.add_column('tax_settings',sa.Column('recommended_reserve_percentage',sa.Numeric(6,3),nullable=False,server_default='15'))
    op.add_column('tax_settings',sa.Column('effective_from',sa.Date(),nullable=True))
    op.add_column('tax_settings',sa.Column('accountant_notes',sa.Text(),nullable=True))
    op.execute('UPDATE tax_settings SET recommended_reserve_percentage = default_percentage')

def downgrade():
    for name in ('accountant_notes','effective_from','recommended_reserve_percentage','separate_darfs_json','has_separate_darfs','iss_effective_percentage','das_effective_percentage','rbt12','fator_r','simples_annex','simples_nacional'):op.drop_column('tax_settings',name)
    op.drop_index('ix_shifts_tax_treatment',table_name='shifts');op.drop_column('shifts','tax_treatment');op.drop_column('shifts','tax_reserve_percentage')
