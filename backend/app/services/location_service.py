import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from fastapi import HTTPException

STATES={'AC':'Acre','AL':'Alagoas','AP':'Amapá','AM':'Amazonas','BA':'Bahia','CE':'Ceará','DF':'Distrito Federal','ES':'Espírito Santo','GO':'Goiás','MA':'Maranhão','MT':'Mato Grosso','MS':'Mato Grosso do Sul','MG':'Minas Gerais','PA':'Pará','PB':'Paraíba','PR':'Paraná','PE':'Pernambuco','PI':'Piauí','RJ':'Rio de Janeiro','RN':'Rio Grande do Norte','RS':'Rio Grande do Sul','RO':'Rondônia','RR':'Roraima','SC':'Santa Catarina','SP':'São Paulo','SE':'Sergipe','TO':'Tocantins'}
ALIASES={re.sub(r'[^a-z]','',unicodedata.normalize('NFKD',name).encode('ascii','ignore').decode().lower()):uf for uf,name in STATES.items()}
def normalize_text(value):return ''.join(c for c in unicodedata.normalize('NFKD',value or '') if not unicodedata.combining(c)).casefold()
def normalize_state(value):
    if not value:return None
    normalized=value.strip().upper()
    if normalized in STATES:return normalized
    alias=re.sub(r'[^a-z]','',normalize_text(value))
    return ALIASES.get(alias)
def validate_state(value):
    normalized=normalize_state(value)
    if not normalized:raise HTTPException(422,'UF inválida.')
    return normalized
@lru_cache
def municipalities():
    # Dataset oficial IBGE, versionado para funcionamento offline.
    # Fonte: https://servicodados.ibge.gov.br/api/v1/localidades/municipios
    data=json.loads((Path(__file__).parents[1]/'data'/'ibge_municipalities.json').read_text(encoding='utf-8'))
    result=[]
    for item in data:
        region=item.get('regiao-imediata') or {};uf=((region.get('regiao-intermediaria') or {}).get('UF') or {}).get('sigla')
        if not uf:uf=((((item.get('microrregiao') or {}).get('mesorregiao') or {}).get('UF') or {}).get('sigla'))
        result.append({'ibge_code':str(item['id']),'name':item['nome'],'state':uf,'normalized_name':normalize_text(item['nome'])})
    return result
def find_city(state,ibge_code):return next((x for x in municipalities() if x['state']==state and x['ibge_code']==str(ibge_code)),None)
def validate_location(state,city=None,ibge_code=None):
    uf=validate_state(state) if state else None
    if ibge_code:
        found=find_city(uf,ibge_code)
        if not found:raise HTTPException(422,'A cidade não pertence à UF informada.')
        if city and normalize_text(city)!=found['normalized_name']:raise HTTPException(422,'Nome da cidade incompatível com o código IBGE.')
        return uf,found['name'],found['ibge_code']
    return uf,city,None
