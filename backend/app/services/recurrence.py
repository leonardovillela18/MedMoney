import calendar
from datetime import date, timedelta

MONTHS={'Mensal':1,'Trimestral':3,'Semestral':6,'Anual':12}
FREQUENCIES={'Semanal',*MONTHS}
def next_occurrence(value:date,frequency:str,anchor_day:int|None=None)->date:
    if frequency=='Semanal':return value+timedelta(days=7)
    if frequency not in MONTHS:raise ValueError('Frequência inválida.')
    absolute=value.year*12+value.month-1+MONTHS[frequency];year,month=divmod(absolute,12);month+=1
    return date(year,month,min(anchor_day or value.day,calendar.monthrange(year,month)[1]))

def first_occurrence(start:date,frequency:str,day_of_month:int|None=None)->date:
    if frequency=='Semanal' or day_of_month is None:return start
    return date(start.year,start.month,min(day_of_month,calendar.monthrange(start.year,start.month)[1]))
