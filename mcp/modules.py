from pydantic import BaseModel
from typing import Optional, List

class Document(BaseModel):
    repo: str
    path: str
    content: str
    version: Optional[str] = "latest"

class Repository(BaseModel):
    url: str
    name: Optional[str] = None
    branch: Optional[str] = "main"

