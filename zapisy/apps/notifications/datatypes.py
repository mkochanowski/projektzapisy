from datetime import datetime
from typing import Dict


class Notification:

    def __init__(self, issued_on: datetime, description_id: str,
                 description_args: Dict):
        self.issued_on = issued_on
        self.description_id = description_id
        self.description_args = description_args
