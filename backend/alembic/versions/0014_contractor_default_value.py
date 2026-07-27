"""optional default value for contractor appointments"""
from alembic import op
import sqlalchemy as sa
revision='0014_contractor_default_value';down_revision='0013_medical_assistants';branch_labels=None;depends_on=None
def upgrade():op.add_column('contractors',sa.Column('default_shift_value',sa.Numeric(12,2),nullable=True))
def downgrade():op.drop_column('contractors','default_shift_value')
