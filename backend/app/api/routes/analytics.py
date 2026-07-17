import csv,io,uuid
from datetime import date
from fastapi import APIRouter,Depends,Query
from fastapi.responses import Response,StreamingResponse
from sqlalchemy.orm import Session
from app.api.dependencies import current_user
from app.database.session import get_db
from app.models.user import User
from app.services.analytics_service import AnalyticsService
from app.services.insights import FinancialInsightsService
router=APIRouter(prefix='/analytics',tags=['Analytics e Business Intelligence'])
def filters(date_from:date|None=None,date_to:date|None=None,contractor_id:uuid.UUID|None=None,specialty:str|None=None,city:str|None=None,type:str|None=None,category_id:uuid.UUID|None=None,status:str|None=None):return locals()
@router.get('')
def executive(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).executive()
@router.get('/revenue')
def revenue(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).revenue()
@router.get('/shifts')
def shifts(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).shifts_analysis()
@router.get('/expenses')
def expenses(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).expense_analysis()
@router.get('/profit')
def profit(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).profit()
@router.get('/contractors')
def contractors(f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):return AnalyticsService(db,user.id,f).contractors_analysis()
@router.get('/export')
def export(format:str=Query('csv',pattern='^(csv|xlsx|pdf|svg)$'),f:dict=Depends(filters),user:User=Depends(current_user),db:Session=Depends(get_db)):
 data=AnalyticsService(db,user.id,f).executive();insights=FinancialInsightsService(db).dashboard(user.id)['highlights'];kpis=data['kpis'];rows=[('Indicador','Valor'),*[(k,v) for k,v in kpis.items()]]
 if format=='csv':
  output=io.StringIO();writer=csv.writer(output);writer.writerows(rows);return Response('\ufeff'+output.getvalue(),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=medmoney-analytics.csv'})
 if format=='xlsx':
  from openpyxl import Workbook
  book=Workbook();sheet=book.active;sheet.title='Resumo Executivo'
  for row in rows:sheet.append(row)
  sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions;binary=io.BytesIO();book.save(binary);binary.seek(0);return StreamingResponse(binary,media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',headers={'Content-Disposition':'attachment; filename=medmoney-analytics.xlsx'})
 if format=='pdf':
  from reportlab.lib.pagesizes import A4
  from reportlab.pdfgen import canvas
  binary=io.BytesIO();pdf=canvas.Canvas(binary,pagesize=A4);pdf.setTitle('Relatório Executivo MedMoney');pdf.setFont('Helvetica-Bold',18);pdf.drawString(45,800,'MedMoney — Relatório Executivo');pdf.setFont('Helvetica',9);pdf.drawString(45,782,f'Gerado em {date.today().strftime("%d/%m/%Y")}');y=750
  for label,value in rows[1:]:pdf.setFont('Helvetica-Bold',9);pdf.drawString(45,y,str(label).replace('_',' ').title());pdf.setFont('Helvetica',9);pdf.drawRightString(550,y,str(value));y-=22
  pdf.setFont('Helvetica-Bold',12);pdf.drawString(45,y-10,'Insights prioritários');y-=30
  for insight in insights:pdf.setFont('Helvetica',8);pdf.drawString(45,y,insight.titulo[:80]);y-=16
  pdf.setFont('Helvetica-Bold',12);pdf.drawString(45,y-10,'Comparativos');y-=34
  for x in data['comparisons']:pdf.setFont('Helvetica',8);pdf.drawString(45,y,f"{x['label']}: receita R$ {x['revenue']:.2f} · {x['shifts']} plantões · {x['hours']:.1f}h");bar=min(300,max(0,x['revenue']/max([z['revenue'] for z in data['comparisons']]+[1])*300));pdf.setFillColorRGB(.15,.4,.9);pdf.rect(250,y-2,bar,7,fill=1,stroke=0);pdf.setFillColorRGB(0,0,0);y-=18
  pdf.save();binary.seek(0);return StreamingResponse(binary,media_type='application/pdf',headers={'Content-Disposition':'attachment; filename=medmoney-relatorio.pdf'})
 values=[float(x['value']) for x in data['revenue']['monthly']];maximum=max(values+[1]);bars=''.join(f'<rect x="{30+i*24}" y="{180-v/maximum*140}" width="16" height="{v/maximum*140}" rx="3" fill="#2563eb"/>' for i,v in enumerate(values[-20:]));svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="220"><rect width="100%" height="100%" fill="white"/><text x="20" y="24" font-family="Arial" font-size="16">MedMoney — Receita mensal</text>{bars}</svg>';return Response(svg,media_type='image/svg+xml',headers={'Content-Disposition':'attachment; filename=medmoney-grafico.svg'})
