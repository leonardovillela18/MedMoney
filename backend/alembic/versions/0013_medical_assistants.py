"""medical assistants and doctor ownership"""
from alembic import op
import sqlalchemy as sa

revision='0013_medical_assistants';down_revision='0012_enterprise_foundation';branch_labels=None;depends_on=None

def upgrade():
 op.create_table('assistant_links',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('assistant_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False,unique=True),sa.Column('doctor_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
 op.create_index('ix_assistant_links_assistant_id','assistant_links',['assistant_id'],unique=True);op.create_index('ix_assistant_links_doctor_id','assistant_links',['doctor_id'])
 op.execute(sa.text("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE name='ASSISTENTE')"))

def downgrade():
 op.drop_index('ix_assistant_links_doctor_id',table_name='assistant_links');op.drop_index('ix_assistant_links_assistant_id',table_name='assistant_links');op.drop_table('assistant_links')
