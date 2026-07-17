from dataclasses import dataclass
from typing import Callable,Protocol
class JobQueue(Protocol):
 def enqueue(self,name:str,handler:Callable,*args,**kwargs)->str:...
 def health(self)->bool:...
@dataclass
class InlineJobQueue:
 def enqueue(self,name,handler,*args,**kwargs):handler(*args,**kwargs);return f'inline:{name}'
 def health(self):return True
_queue=InlineJobQueue()
def get_job_queue():return _queue
