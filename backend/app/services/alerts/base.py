import uuid
from dataclasses import dataclass
from typing import Protocol
NAMESPACE=uuid.UUID('9e41243e-76f4-49fc-9c53-66df0eb7a714')
@dataclass(frozen=True)
class AlertCandidate:
 tipo:str;categoria:str;titulo:str;descricao:str;prioridade:str;acao:str;url_destino:str;origem:str;reference:str
 @property
 def referencia_id(self):return uuid.uuid5(NAMESPACE,self.reference)
class AlertRule(Protocol):
 def evaluate(self,context)->list[AlertCandidate]:...
