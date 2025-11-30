from datetime import datetime
from pydantic import BaseModel

class SystemHealthResponse(BaseModel):
    """
    Pydantic Schema for the Health Check Response.
    """
    database_time: datetime
    status: str
    app_version: str = "0.1.0"
