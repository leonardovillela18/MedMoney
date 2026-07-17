import json,time
from abc import ABC,abstractmethod
class CachePort(ABC):
 @abstractmethod
 def get(self,key:str):...
 @abstractmethod
 def set(self,key:str,value,ttl:int=60):...
 @abstractmethod
 def delete_prefix(self,prefix:str):...
 @abstractmethod
 def health(self)->bool:...
class MemoryCache(CachePort):
 def __init__(self):self.data={}
 def get(self,key):
  item=self.data.get(key)
  if not item or item[0]<time.monotonic():self.data.pop(key,None);return None
  return item[1]
 def set(self,key,value,ttl=60):self.data[key]=(time.monotonic()+ttl,value)
 def delete_prefix(self,prefix):
  for key in [x for x in self.data if x.startswith(prefix)]:self.data.pop(key,None)
 def health(self):return True
class RedisCache(CachePort):
 def __init__(self,url):
  import redis
  self.client=redis.Redis.from_url(url,decode_responses=True,socket_connect_timeout=1)
 def get(self,key):
  value=self.client.get(key);return json.loads(value) if value else None
 def set(self,key,value,ttl=60):self.client.setex(key,ttl,json.dumps(value,default=str))
 def delete_prefix(self,prefix):
  for key in self.client.scan_iter(f'{prefix}*',count=100):self.client.delete(key)
 def health(self):return bool(self.client.ping())
_cache=None
def get_cache():
 global _cache
 if _cache is None:
  from app.core.config import get_settings
  settings=get_settings();_cache=RedisCache(settings.redis_url) if settings.redis_url else MemoryCache()
 return _cache
