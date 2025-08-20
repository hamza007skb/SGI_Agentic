from pydantic import BaseModel, Field

class EmailInfo(BaseModel):
    sender: str = Field(description="Senders Email address")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Main content of the email")