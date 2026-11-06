from fastapi import APIRouter, HTTPException, Request

router = APIRouter(
    prefix="/api/scraping",
    tags=["Scraping"],
)


@router.post("/run")
async def run_scraping(request: Request):
    scheduler = request.app.state.scraping_scheduler

    try:
        return await scheduler.run_manual_scraping()

    except RuntimeError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Scraping operation failed",
        ) from exc