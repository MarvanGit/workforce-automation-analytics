from pydantic import BaseModel

# Schema for health check response
class HealthResponse(BaseModel):
    status: str
    service: str
    environment: str

