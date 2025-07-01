"""
WhatsApp Business API Webhook Handler
Processes incoming WhatsApp messages and routes them to AI engine
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import PlainTextResponse
import hmac
import hashlib
import json
import logging
from typing import Dict, Any

from app.core.config import settings
from app.whatsapp.message_handler import WhatsAppMessageHandler
from app.whatsapp.models import WebhookPayload, MessageStatus

logger = logging.getLogger(__name__)
whatsapp_router = APIRouter(tags=["WhatsApp"])

# Initialize message handler
message_handler = WhatsAppMessageHandler()


def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verify WhatsApp webhook signature for security"""
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    received_signature = signature[7:]  # Remove 'sha256=' prefix
    return hmac.compare_digest(expected_signature, received_signature)


@whatsapp_router.get("/webhook")
async def verify_webhook(
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    """
    WhatsApp webhook verification endpoint
    Used during webhook setup to verify ownership
    """
    logger.info(f"Webhook verification attempt: mode={hub_mode}, token={hub_verify_token}")
    
    if (hub_mode == "subscribe" and 
        hub_verify_token == settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN):
        logger.info("✅ Webhook verification successful")
        return PlainTextResponse(content=hub_challenge)
    
    logger.warning("❌ Webhook verification failed")
    raise HTTPException(status_code=403, detail="Forbidden")


@whatsapp_router.post("/webhook")
async def handle_webhook(request: Request):
    """
    Main webhook endpoint for processing WhatsApp messages
    Handles incoming messages, status updates, and delivery receipts
    """
    try:
        # Get raw payload for signature verification
        payload = await request.body()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Verify webhook signature
        if not verify_webhook_signature(payload, signature):
            logger.warning("❌ Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse JSON payload
        data = json.loads(payload.decode())
        logger.info(f"📨 Received webhook: {json.dumps(data, indent=2)}")
        
        # Process webhook data
        webhook_payload = WebhookPayload(**data)
        
        for entry in webhook_payload.entry:
            for change in entry.changes:
                if change.field == "messages":
                    await process_messages(change.value)
                elif change.field == "message_status":
                    await process_message_status(change.value)
        
        return {"status": "success"}
        
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    except Exception as e:
        logger.error(f"❌ Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_messages(message_data: Dict[str, Any]):
    """Process incoming WhatsApp messages"""
    
    if not message_data.get('messages'):
        return
    
    for message in message_data['messages']:
        try:
            logger.info(f"💬 Processing message: {message.get('id')}")
            
            # Extract message details
            user_phone = message['from']
            message_id = message['id']
            timestamp = message['timestamp']
            
            # Handle different message types
            if message['type'] == 'text':
                text_content = message['text']['body']
                await message_handler.handle_text_message(
                    user_phone=user_phone,
                    message_id=message_id,
                    text=text_content,
                    timestamp=timestamp
                )
            
            elif message['type'] == 'audio':
                audio_id = message['audio']['id']
                await message_handler.handle_audio_message(
                    user_phone=user_phone,
                    message_id=message_id,
                    audio_id=audio_id,
                    timestamp=timestamp
                )
            
            elif message['type'] == 'image':
                image_id = message['image']['id']
                caption = message['image'].get('caption', '')
                await message_handler.handle_image_message(
                    user_phone=user_phone,
                    message_id=message_id,
                    image_id=image_id,
                    caption=caption,
                    timestamp=timestamp
                )
            
            elif message['type'] == 'interactive':
                # Handle button clicks and list selections
                interactive_data = message['interactive']
                await message_handler.handle_interactive_message(
                    user_phone=user_phone,
                    message_id=message_id,
                    interactive_data=interactive_data,
                    timestamp=timestamp
                )
            
            else:
                logger.warning(f"⚠️ Unsupported message type: {message['type']}")
        
        except Exception as e:
            logger.error(f"❌ Error processing message {message.get('id')}: {str(e)}")


async def process_message_status(status_data: Dict[str, Any]):
    """Process message delivery status updates"""
    
    if not status_data.get('statuses'):
        return
    
    for status in status_data['statuses']:
        try:
            message_id = status['id']
            recipient_id = status['recipient_id']
            status_type = status['status']  # sent, delivered, read, failed
            
            logger.info(f"📋 Message status update: {message_id} -> {status_type}")
            
            # Update message status in database
            await message_handler.update_message_status(
                message_id=message_id,
                recipient_id=recipient_id,
                status=MessageStatus(status_type),
                timestamp=status.get('timestamp')
            )
            
        except Exception as e:
            logger.error(f"❌ Error processing status update: {str(e)}")


@whatsapp_router.get("/health")
async def whatsapp_health():
    """Health check endpoint for WhatsApp service"""
    return {
        "status": "healthy",
        "service": "WhatsApp Integration",
        "webhook_configured": bool(settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN),
        "api_token_configured": bool(settings.WHATSAPP_ACCESS_TOKEN)
    }