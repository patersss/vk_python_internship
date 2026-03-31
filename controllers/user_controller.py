from fastapi import APIRouter, HTTPException, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", status_code=status.HTTP_200_OK)