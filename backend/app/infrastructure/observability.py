from dataclasses import dataclass
@dataclass
class ObservabilityHooks:
 """Provider-neutral hooks for OpenTelemetry and Sentry adapters."""
 def capture_exception(self,error,context=None):return None
 def record_metric(self,name,value=1,attributes=None):return None
hooks=ObservabilityHooks()
