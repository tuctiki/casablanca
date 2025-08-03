from dataclasses import dataclass
from datetime import datetime

@dataclass
class Video:
    title: str
    description: str
    published_at: datetime

    @property
    def date(self):
        return self.published_at.strftime("%Y-%m-%d")