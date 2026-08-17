from fastapi import APIRouter

router = APIRouter()

@router.get("/test")
def test_api():
    return {
        "message": "Test API working fine ✔️",
        "success": True
    }