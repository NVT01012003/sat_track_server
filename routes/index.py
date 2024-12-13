from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()

@router.get("/users")
async def redirect_to_users():
    return RedirectResponse(url="/users/")

@router.get("/satellites")
async def redirect_to_satellites():
    return RedirectResponse(url="/satellites/")

@router.get("/tles")
async def redirect_to_tles():
    return RedirectResponse(url="/tles/")

@router.get("/visible_satellites")
async def redirect_to_tles():
    return RedirectResponse(url="/visible_satelites/")
