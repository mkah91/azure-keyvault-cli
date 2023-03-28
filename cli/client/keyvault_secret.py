from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional


@dataclass
class Secret:
    name: Optional[str]
    expires_on: Optional[datetime]
    value: Optional[str] = field(default=None)
    _days_before_expiration: int = field(default=15, init=False)

    def is_expired(self) -> bool:
        if not self.expires_on:
            return False
        return self.expires_on < datetime.now(timezone.utc)

    def is_soon_expired(self) -> bool:
        if not self.expires_on or (self.expires_on < datetime.now(timezone.utc)):
            return False
        return self.expires_on < (datetime.now(timezone.utc) + timedelta(days=self._days_before_expiration))
