from fastapi import APIRouter, Request

from services.payment import PaymentService

router = APIRouter(prefix="/api/yookassa", tags=["YooKassa"])

@router.post("/webhook")
async def yookassa_webhook_endpoint(request: Request):
    data = await request.json()
    await PaymentService.process_webhook(data)
    return {"status": "ok"}
