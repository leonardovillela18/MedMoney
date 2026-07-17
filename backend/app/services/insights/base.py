from dataclasses import dataclass
from typing import Protocol
@dataclass(frozen=True)
class InsightCandidate:
 tipo:str;titulo:str;descricao:str;categoria:str;severidade:str;prioridade:int;acao_recomendada:str;referencia:str
class InsightAnalyzer(Protocol):
 def analyze(self,context)->list[InsightCandidate]:...
