import json
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models.tax import TaxEstimation, TaxSetting
from app.repositories.tax_repository import TaxRepository
from app.schemas.tax import STATUSES, TYPES

class TaxService:
    """Creates non-official projections and manages suggested tax reserves."""
    def __init__(self,db:Session):self.db=db;self.repo=TaxRepository(db)
    @staticmethod
    def calculate_reserve(base,percentage):
        base=Decimal(base);percentage=Decimal(percentage)
        if percentage<0 or percentage>100:raise HTTPException(422,'O percentual deve estar entre 0 e 100.')
        reserve=(base*percentage/Decimal(100)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
        return reserve,(base-reserve).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
    @staticmethod
    def estimated(base,percentage):return TaxService.calculate_reserve(base,percentage)[0]
    def percentage(self,user_id):
        setting=self.repo.setting(user_id);return setting.recommended_reserve_percentage if setting else Decimal('15')
    def validate(self,data):
        if data.get('tipo') not in TYPES:raise HTTPException(422,'Tipo de estimativa inválido.')
        if data.get('status') not in STATUSES:raise HTTPException(422,'Status de estimativa inválido.')
    def list(self,*args):return self.repo.list(*args)
    def create(self,user_id,data):
        self.validate(data);data['valor_estimado']=self.estimated(data['base_calculo'],data['percentual']);x=TaxEstimation(user_id=user_id,**data);self.db.add(x);self.db.commit();self.db.refresh(x);return x
    def update(self,user_id,item_id,data):
        x=self.repo.get(user_id,item_id)
        if not x:raise HTTPException(404,'Estimativa não encontrada.')
        values={k:v for k,v in data.items() if v is not None};self.validate({'tipo':values.get('tipo',x.tipo),'status':values.get('status',x.status)})
        for k,v in values.items():setattr(x,k,v)
        x.valor_estimado=self.estimated(x.base_calculo,x.percentual);self.db.commit();self.db.refresh(x)
        if x.status in ('Reservado','Pago'):
            from app.services.cashflow_service import CashflowService
            service=CashflowService(self.db);service.sync_source(user_id,'Reserva Tributária',x.id,x.competencia,'Reserva Tributária',f'Reserva sugerida — {x.tipo}','Impostos',-abs(x.valor_estimado),'Confirmado');self.db.commit();service.recalculate(user_id)
            from app.services.insights.events import refresh_insights
            refresh_insights(self.db,user_id)
        return x
    def sync(self,user_id,base,competence,shift_id=None,invoice_id=None,receivable_id=None,percentage=None,tax_treatment='PJ_TAXABLE'):
        source_filter=TaxEstimation.shift_id==shift_id if shift_id else TaxEstimation.invoice_id==invoice_id if invoice_id else TaxEstimation.receivable_id==receivable_id
        x=self.db.scalar(select(TaxEstimation).where(TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None),source_filter));pct=Decimal(percentage) if percentage is not None else x.percentual if x else self.percentage(user_id)
        if not x:x=TaxEstimation(user_id=user_id,tipo='Outro',status='Estimado');self.db.add(x)
        if shift_id:x.shift_id=shift_id
        if invoice_id:x.invoice_id=invoice_id
        if receivable_id:x.receivable_id=receivable_id
        if x.status in ('Estimado','Ignorado'):
            x.base_calculo=base;x.percentual=pct;x.valor_estimado=self.estimated(base,pct);x.competencia=competence.replace(day=1);x.status='Ignorado' if tax_treatment=='NON_PJ' else 'Estimado';x.observacoes='Reserva sugerida para planejamento. Não representa apuração tributária oficial.'
        self.db.commit();return x
    def setting(self,user_id):
        x=self.repo.setting(user_id)
        return {'simples_nacional':x.simples_nacional if x else None,'simples_annex':x.simples_annex if x else 'UNKNOWN','fator_r':float(x.fator_r) if x and x.fator_r is not None else None,'rbt12':float(x.rbt12) if x and x.rbt12 is not None else None,'das_effective_percentage':float(x.das_effective_percentage) if x and x.das_effective_percentage is not None else None,'iss_effective_percentage':float(x.iss_effective_percentage) if x and x.iss_effective_percentage is not None else None,'has_separate_darfs':x.has_separate_darfs if x else False,'separate_darfs':json.loads(x.separate_darfs_json or '[]') if x else [],'recommended_reserve_percentage':float(self.percentage(user_id)),'default_percentage':float(self.percentage(user_id)),'effective_from':str(x.effective_from) if x and x.effective_from else None,'accountant_notes':x.accountant_notes if x else None,'disclaimer':'Os valores apresentados são estimativas para planejamento financeiro. A apuração e o recolhimento devem seguir as orientações do seu contador.'}
    def save_setting(self,user_id,data):
        x=self.repo.setting(user_id)
        if not x:x=TaxSetting(user_id=user_id);self.db.add(x)
        for key,value in data.items():
            if key=='separate_darfs':x.separate_darfs_json=json.dumps(value)
            else:setattr(x,key,value)
        x.default_percentage=data['recommended_reserve_percentage']
        self.db.commit();return self.setting(user_id)
    def dashboard(self,user_id):
        today=date.today();start=today.replace(day=1);end=self.repo.next_month(start);active=[TaxEstimation.user_id==user_id,TaxEstimation.deleted_at.is_(None),TaxEstimation.status!='Ignorado']
        total=lambda extra:Decimal(self.db.scalar(select(func.coalesce(func.sum(TaxEstimation.valor_estimado),0)).where(*active,*extra)) or 0)
        month=total([TaxEstimation.competencia>=start,TaxEstimation.competencia<end]);reserved=total([TaxEstimation.status.in_(['Reservado','Pago'])]);needed=total([TaxEstimation.status=='Estimado']);gross=Decimal(self.db.scalar(select(func.coalesce(func.sum(TaxEstimation.base_calculo),0)).where(*active,TaxEstimation.competencia>=start,TaxEstimation.competencia<end)) or 0)
        series_by_month={}
        for item in self.db.scalars(select(TaxEstimation).where(*active).order_by(TaxEstimation.competencia)):
            key=item.competencia.strftime('%Y-%m');bucket=series_by_month.setdefault(key,[Decimal(0),Decimal(0)]);bucket[0]+=item.base_calculo;bucket[1]+=item.valor_estimado
        rows=[(key,*values) for key,values in list(series_by_month.items())[-12:]]
        coverage=float((reserved/(reserved+needed)*100) if reserved+needed else 100);insights=[]
        if needed:insights.append(f'Sua reserva tributária estimada está abaixo do recomendado. Você reservou {coverage:.0f}% do necessário.')
        insights.append(f'Seu disponível após a reserva sugerida no mês é de R$ {gross-month:,.2f}.')
        return {'estimated_month':float(month),'reserved_total':float(reserved),'not_reserved':float(needed),'estimated_net_profit':float(gross-month),'gross_month':float(gross),'coverage':coverage,'series':[{'month':m,'gross':float(g or 0),'tax':float(t or 0),'net':float((g or 0)-(t or 0))} for m,g,t in rows],'insights':insights,'disclaimer':'Valores apresentados são estimativas e não substituem cálculo tributário oficial.'}
