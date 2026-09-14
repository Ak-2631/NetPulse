from fastapi import APIRouter
from app.services.traffic import get_host_traffic

router = APIRouter()

@router.get("/")
def get_traffic():
    return get_host_traffic()
