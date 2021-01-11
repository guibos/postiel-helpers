from pydantic import BaseModel


class QueueConfig(BaseModel):
    url: str
    queue: str
