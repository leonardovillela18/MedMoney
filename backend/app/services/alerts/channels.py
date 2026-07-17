from typing import Protocol
from app.models.alert import Alert
class AlertChannel(Protocol):
 def deliver(self,alert:Alert)->None:...
class InternalAlertChannel:
 """Internal notifications are persisted by the engine; delivery needs no external side effect."""
 def deliver(self,alert:Alert)->None:return None
CHANNELS=(InternalAlertChannel(),)
