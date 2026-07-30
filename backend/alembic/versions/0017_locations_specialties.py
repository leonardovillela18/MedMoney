"""normalized locations and medical specialties"""
import re,uuid,unicodedata
from alembic import op
import sqlalchemy as sa
revision='0017_locations_specialties';down_revision='0016_recurring_incomes';branch_labels=None;depends_on=None
NAMES=['Clínica Médica','Cirurgia Geral','Cardiologia','Pediatria','Anestesiologia','Ortopedia e Traumatologia','Ginecologia e Obstetrícia','Medicina Intensiva','Medicina de Emergência','Neurologia','Neurocirurgia','Psiquiatria','Dermatologia','Radiologia e Diagnóstico por Imagem','Oftalmologia','Otorrinolaringologia','Urologia','Nefrologia','Endocrinologia e Metabologia','Gastroenterologia','Pneumologia','Reumatologia','Hematologia e Hemoterapia','Oncologia Clínica','Infectologia','Medicina de Família e Comunidade']
def slug(name):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()).strip('-')
def upgrade():
    op.create_table('medical_specialties',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('code',sa.String(80),nullable=False,unique=True),sa.Column('name',sa.String(120),nullable=False,unique=True),sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column('updated_at',sa.DateTime(timezone=True),server_default=sa.func.now()))
    for c in ('code','name','active'):op.create_index(f'ix_medical_specialties_{c}','medical_specialties',[c])
    table=sa.table('medical_specialties',sa.column('id',sa.Uuid()),sa.column('code',sa.String()),sa.column('name',sa.String()),sa.column('active',sa.Boolean()))
    op.bulk_insert(table,[{'id':uuid.uuid5(uuid.NAMESPACE_URL,f'crmoney:specialty:{slug(n)}'),'code':slug(n),'name':n,'active':True} for n in NAMES])
    op.create_table('user_specialties',sa.Column('id',sa.Uuid(),primary_key=True),sa.Column('user_id',sa.Uuid(),sa.ForeignKey('users.id'),nullable=False),sa.Column('specialty_id',sa.Uuid(),sa.ForeignKey('medical_specialties.id'),nullable=False),sa.Column('priority',sa.String(12),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),server_default=sa.func.now()),sa.UniqueConstraint('user_id','priority',name='uq_user_specialty_priority'),sa.UniqueConstraint('user_id','specialty_id',name='uq_user_specialty_pair'))
    op.create_index('ix_user_specialties_user_id','user_specialties',['user_id']);op.create_index('ix_user_specialties_specialty_id','user_specialties',['specialty_id'])
    op.add_column('users',sa.Column('city_ibge_code',sa.String(7)));op.create_index('ix_users_city_ibge_code','users',['city_ibge_code'])
    op.add_column('contractors',sa.Column('city_ibge_code',sa.String(7)));op.create_index('ix_contractors_city_ibge_code','contractors',['city_ibge_code'])
    op.add_column('shifts',sa.Column('city_ibge_code',sa.String(7)))
    with op.batch_alter_table('shifts') as batch:
        batch.add_column(sa.Column('specialty_id',sa.Uuid()))
        batch.create_foreign_key('fk_shifts_specialty_id','medical_specialties',['specialty_id'],['id'])
    op.create_index('ix_shifts_city_ibge_code','shifts',['city_ibge_code']);op.create_index('ix_shifts_specialty_id','shifts',['specialty_id'])
def downgrade():
    op.drop_index('ix_shifts_specialty_id',table_name='shifts');op.drop_index('ix_shifts_city_ibge_code',table_name='shifts')
    with op.batch_alter_table('shifts') as batch:
        batch.drop_constraint('fk_shifts_specialty_id',type_='foreignkey')
        batch.drop_column('specialty_id')
    op.drop_column('shifts','city_ibge_code');op.drop_index('ix_contractors_city_ibge_code',table_name='contractors');op.drop_column('contractors','city_ibge_code');op.drop_index('ix_users_city_ibge_code',table_name='users');op.drop_column('users','city_ibge_code');op.drop_table('user_specialties');op.drop_table('medical_specialties')
