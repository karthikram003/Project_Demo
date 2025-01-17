from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.export_schema import DownloadResponse, DownloadRequest
from app.utils.validate_token import get_current_user
from app.schemas.user_schema import CurrentUser
from app.services.export_service import handle_download
from app.utils.validate_token import verify_token
 
router = APIRouter(
    prefix="/export",
    tags=["Export"],
    dependencies=[Depends(verify_token)]
)
 
 
@router.post("/buildings", response_model=DownloadResponse)
async def export_buildings(
        download_request: DownloadRequest,
        current_user: CurrentUser = Depends(get_current_user)
):
    """
    Endpoint to handle building export requests.
 
    Args:
        download_request (DownloadRequest): The request body containing the number of buildings to download.
        current_user (CurrentUser): The authenticated user making the request.
 
    Returns:
        DownloadResponse: The response indicating whether the download is allowed and related details.
    """
    result = handle_download(current_user, download_request.requested_download_count)
    if not result['allowed']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=result['message']
        )
    return DownloadResponse(
        message=result['message'],
        download_count=result['download_count'],
        download_limit=result['download_limit']
)