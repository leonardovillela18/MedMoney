from typing import Protocol


class BankingProvider(Protocol):
    """Contract for a future authorized Open Finance provider."""

    def list_accounts(self): ...
    def sync_transactions(self, account_id): ...
    def get_balance(self, account_id): ...
    def disconnect(self, account_id): ...


class ManualBankingProvider:
    """Manual accounts deliberately perform no external connection."""

    def list_accounts(self): return []
    def sync_transactions(self, account_id): return []
    def get_balance(self, account_id): return None
    def disconnect(self, account_id): return None
