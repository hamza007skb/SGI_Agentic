from typing import Dict
from typing_extensions import TypedDict

class AgentState(TypedDict):
    raw_email: Dict
    senders_email: str | None
    nic: str | None
    client_name: str | None
    contact_number: str | None
    address: str | None
    error: str | None
