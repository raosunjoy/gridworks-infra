"""
GridWorks B2B Services - WhatsApp Business Integration
Enterprise WhatsApp Business API integration with voice responses and financial services
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
from enum import Enum
from dataclasses import dataclass
import base64
import hashlib
import hmac
from urllib.parse import quote
import redis
from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import EnterpriseClient, UsageRecord
from ..config import settings
from ..utils.voice_synthesis import VoiceSynthesizer
from ..utils.media_processor import MediaProcessor
from ..ai_suite.support_engine import SupportEngine, SupportRequest, SupportChannel
from ..ai_suite.moderator_engine import ModerationEngine, ModerationRequest, ContentType, Platform


class MessageType(str, Enum):
    """WhatsApp message types"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACTS = "contacts"
    STICKER = "sticker"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"


class BusinessFeature(str, Enum):
    """WhatsApp Business features"""
    AI_SUPPORT = "ai_support"
    VOICE_RESPONSES = "voice_responses"
    DOCUMENT_ANALYSIS = "document_analysis"
    PORTFOLIO_UPDATES = "portfolio_updates"
    MARKET_ALERTS = "market_alerts"
    COMPLIANCE_NOTIFICATIONS = "compliance_notifications"


@dataclass
class WhatsAppMessage:
    """WhatsApp message structure"""
    message_id: str
    from_number: str
    to_number: str
    message_type: MessageType
    content: Union[str, bytes, Dict[str, Any]]
    timestamp: datetime
    client_id: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class WhatsAppResponse:
    """WhatsApp response structure"""
    success: bool
    message_id: Optional[str]
    status: str
    error_message: Optional[str] = None
    delivery_timestamp: Optional[datetime] = None


class WhatsAppBusinessClient:
    """
    Enterprise WhatsApp Business API client with financial services features
    """
    
    def __init__(self):
        self.api_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.webhook_token = settings.WHATSAPP_WEBHOOK_TOKEN
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.voice_synthesizer = VoiceSynthesizer()
        self.media_processor = MediaProcessor()
        
        # Session for HTTP requests
        self.session = None
        
        # Rate limiting configuration
        self.rate_limits = {
            "messaging": 1000,  # messages per second
            "media": 100,       # media uploads per minute
            "templates": 250000 # template messages per day
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def send_text_message(
        self,
        to_number: str,
        message: str,
        client_id: Optional[str] = None,
        preview_url: bool = False
    ) -> WhatsAppResponse:
        """Send text message"""
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {
                "body": message,
                "preview_url": preview_url
            }
        }
        
        return await self._send_message(payload, client_id)
    
    async def send_voice_message(
        self,
        to_number: str,
        text: str,
        language: str = "en",
        voice_type: str = "professional",
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send AI-generated voice message"""
        
        try:
            # Generate voice audio
            audio_data = await self.voice_synthesizer.synthesize_speech(
                text=text,
                language=language,
                voice_type=voice_type
            )
            
            # Upload audio to WhatsApp
            media_id = await self._upload_media(audio_data, "audio/ogg")
            
            if not media_id:
                return WhatsAppResponse(
                    success=False,
                    message_id=None,
                    status="error",
                    error_message="Failed to upload audio"
                )
            
            # Send audio message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "audio",
                "audio": {
                    "id": media_id
                }
            }
            
            return await self._send_message(payload, client_id)
            
        except Exception as e:
            return WhatsAppResponse(
                success=False,
                message_id=None,
                status="error",
                error_message=str(e)
            )
    
    async def send_document(
        self,
        to_number: str,
        document_data: bytes,
        filename: str,
        caption: Optional[str] = None,
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send document (PDF reports, statements, etc.)"""
        
        try:
            # Determine MIME type
            mime_type = self._get_mime_type(filename)
            
            # Upload document
            media_id = await self._upload_media(document_data, mime_type, filename)
            
            if not media_id:
                return WhatsAppResponse(
                    success=False,
                    message_id=None,
                    status="error",
                    error_message="Failed to upload document"
                )
            
            # Send document message
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "document",
                "document": {
                    "id": media_id,
                    "filename": filename
                }
            }
            
            if caption:
                payload["document"]["caption"] = caption
            
            return await self._send_message(payload, client_id)
            
        except Exception as e:
            return WhatsAppResponse(
                success=False,
                message_id=None,
                status="error",
                error_message=str(e)
            )
    
    async def send_interactive_menu(
        self,
        to_number: str,
        header_text: str,
        body_text: str,
        footer_text: str,
        menu_items: List[Dict[str, str]],
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send interactive menu for financial services"""
        
        # Format menu items
        rows = []
        for i, item in enumerate(menu_items[:10]):  # WhatsApp limit: 10 items
            rows.append({
                "id": f"menu_item_{i}",
                "title": item.get("title", ""),
                "description": item.get("description", "")
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": body_text
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": "View Options",
                    "sections": [
                        {
                            "title": "Services",
                            "rows": rows
                        }
                    ]
                }
            }
        }
        
        return await self._send_message(payload, client_id)
    
    async def send_template_message(
        self,
        to_number: str,
        template_name: str,
        language_code: str,
        parameters: List[str],
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send pre-approved template message"""
        
        # Format parameters
        components = []
        if parameters:
            components.append({
                "type": "body",
                "parameters": [{"type": "text", "text": param} for param in parameters]
            })
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                },
                "components": components
            }
        }
        
        return await self._send_message(payload, client_id)
    
    async def send_market_alert(
        self,
        to_number: str,
        alert_data: Dict[str, Any],
        include_voice: bool = True,
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send market alert with optional voice"""
        
        # Format alert message
        alert_text = self._format_market_alert(alert_data)
        
        # Send text alert
        text_response = await self.send_text_message(to_number, alert_text, client_id)
        
        # Send voice alert if requested
        if include_voice and text_response.success:
            voice_text = self._format_voice_alert(alert_data)
            await self.send_voice_message(
                to_number,
                voice_text,
                language="en",
                voice_type="urgent",
                client_id=client_id
            )
        
        return text_response
    
    async def process_incoming_message(
        self,
        webhook_data: Dict[str, Any],
        db: AsyncSession
    ) -> Optional[WhatsAppResponse]:
        """Process incoming WhatsApp message with AI support"""
        
        try:
            # Parse webhook data
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            if "messages" not in value:
                return None
            
            message = value["messages"][0]
            contact = value.get("contacts", [{}])[0]
            
            # Extract message data
            from_number = message.get("from")
            message_type = message.get("type")
            message_id = message.get("id")
            timestamp = datetime.fromtimestamp(int(message.get("timestamp")))
            
            # Get client_id from number mapping
            client_id = await self._get_client_from_number(from_number)
            
            if not client_id:
                # Send registration prompt
                await self.send_text_message(
                    from_number,
                    "Welcome to GridWorks Financial Services! Please contact your account manager to activate WhatsApp support."
                )
                return None
            
            # Extract message content
            content = await self._extract_message_content(message, message_type)
            
            # Moderate content
            moderation_request = ModerationRequest(
                client_id=client_id,
                platform=Platform.WHATSAPP,
                content_type=ContentType.TEXT_MESSAGE,
                content=content if isinstance(content, str) else str(content),
                sender_id=from_number,
                channel_id="whatsapp",
                metadata={
                    "contact_name": contact.get("profile", {}).get("name", "Unknown"),
                    "message_id": message_id
                },
                timestamp=timestamp
            )
            
            # Check if content should be blocked
            from ..ai_suite.moderator_engine import get_moderator_engine
            moderator = await get_moderator_engine()
            moderation_result = await moderator.moderate_content(moderation_request, db)
            
            if moderation_result.action.value in ["block", "quarantine"]:
                await self.send_text_message(
                    from_number,
                    "I'm sorry, but I cannot process that request. Please contact customer support for assistance."
                )
                return None
            
            # Process with AI support
            support_request = SupportRequest(
                client_id=client_id,
                user_id=None,
                query=content if isinstance(content, str) else str(content),
                language="en",  # Auto-detect in production
                channel=SupportChannel.WHATSAPP,
                priority=await self._get_client_support_tier(client_id),
                context={
                    "whatsapp_number": from_number,
                    "contact_name": contact.get("profile", {}).get("name"),
                    "response_format": "both",  # Text and audio
                    "message_type": message_type
                }
            )
            
            # Get AI response
            from ..ai_suite.support_engine import get_support_engine
            support_engine = await get_support_engine()
            ai_response = await support_engine.process_support_request(support_request, db)
            
            # Send response
            response = await self.send_text_message(
                from_number,
                ai_response.response_text,
                client_id
            )
            
            # Send voice response if available
            if ai_response.response_audio:
                await self.send_voice_message(
                    from_number,
                    ai_response.response_text,
                    language=ai_response.language,
                    client_id=client_id
                )
            
            # Send follow-up suggestions if available
            if ai_response.follow_up_suggestions:
                suggestions_text = "You might also want to ask:\n" + "\n".join(
                    f"• {suggestion}" for suggestion in ai_response.follow_up_suggestions
                )
                await self.send_text_message(from_number, suggestions_text, client_id)
            
            return response
            
        except Exception as e:
            # Log error and send fallback response
            if 'from_number' in locals():
                await self.send_text_message(
                    from_number,
                    "I apologize, but I'm having technical difficulties. Please try again or contact customer support."
                )
            return WhatsAppResponse(
                success=False,
                message_id=None,
                status="error",
                error_message=str(e)
            )
    
    async def _send_message(
        self,
        payload: Dict[str, Any],
        client_id: Optional[str] = None
    ) -> WhatsAppResponse:
        """Send message via WhatsApp API"""
        
        try:
            # Check rate limits
            await self._check_rate_limit("messaging")
            
            # Send message
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            async with self.session.post(url, json=payload) as response:
                response_data = await response.json()
                
                if response.status == 200:
                    # Log successful message
                    await self._log_message_usage(payload, client_id)
                    
                    return WhatsAppResponse(
                        success=True,
                        message_id=response_data.get("messages", [{}])[0].get("id"),
                        status="sent",
                        delivery_timestamp=datetime.utcnow()
                    )
                else:
                    return WhatsAppResponse(
                        success=False,
                        message_id=None,
                        status="error",
                        error_message=response_data.get("error", {}).get("message", "Unknown error")
                    )
                    
        except Exception as e:
            return WhatsAppResponse(
                success=False,
                message_id=None,
                status="error",
                error_message=str(e)
            )
    
    async def _upload_media(
        self,
        media_data: bytes,
        mime_type: str,
        filename: Optional[str] = None
    ) -> Optional[str]:
        """Upload media to WhatsApp"""
        
        try:
            # Check rate limits
            await self._check_rate_limit("media")
            
            # Prepare form data
            form_data = aiohttp.FormData()
            form_data.add_field('messaging_product', 'whatsapp')
            form_data.add_field('type', mime_type)
            form_data.add_field(
                'file',
                media_data,
                filename=filename or 'media_file',
                content_type=mime_type
            )
            
            url = f"{self.api_url}/{self.phone_number_id}/media"
            
            # Create temporary session without JSON content-type
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(url, data=form_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data.get("id")
                    else:
                        return None
                        
        except Exception as e:
            return None
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename"""
        extension = filename.lower().split('.')[-1]
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'mp3': 'audio/mpeg',
            'ogg': 'audio/ogg',
            'mp4': 'video/mp4'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def _format_market_alert(self, alert_data: Dict[str, Any]) -> str:
        """Format market alert message"""
        alert_type = alert_data.get("type", "Market Update")
        symbol = alert_data.get("symbol", "")
        price = alert_data.get("price", 0)
        change = alert_data.get("change", 0)
        change_percent = alert_data.get("change_percent", 0)
        
        direction = "📈" if change >= 0 else "📉"
        
        return f"""
{direction} **{alert_type}**

**{symbol}**
Price: ₹{price:,.2f}
Change: {change:+.2f} ({change_percent:+.2f}%)

{alert_data.get('message', '')}

*GridWorks Financial Intelligence*
        """.strip()
    
    def _format_voice_alert(self, alert_data: Dict[str, Any]) -> str:
        """Format alert for voice synthesis"""
        symbol = alert_data.get("symbol", "")
        change_percent = alert_data.get("change_percent", 0)
        
        direction = "up" if change_percent >= 0 else "down"
        
        return f"""
Market alert for {symbol}. 
The stock is {direction} {abs(change_percent):.1f} percent. 
{alert_data.get('voice_message', alert_data.get('message', ''))}
        """.strip()
    
    async def _extract_message_content(
        self,
        message: Dict[str, Any],
        message_type: str
    ) -> Union[str, bytes]:
        """Extract content from WhatsApp message"""
        
        if message_type == "text":
            return message.get("text", {}).get("body", "")
        
        elif message_type == "audio":
            # Download and return audio data
            audio_id = message.get("audio", {}).get("id")
            return await self._download_media(audio_id)
        
        elif message_type == "image":
            # Download and return image data
            image_id = message.get("image", {}).get("id")
            return await self._download_media(image_id)
        
        elif message_type == "document":
            # Download and return document data
            doc_id = message.get("document", {}).get("id")
            return await self._download_media(doc_id)
        
        else:
            return f"Received {message_type} message"
    
    async def _download_media(self, media_id: str) -> Optional[bytes]:
        """Download media from WhatsApp"""
        try:
            # Get media URL
            url = f"{self.api_url}/{media_id}"
            async with self.session.get(url) as response:
                if response.status == 200:
                    media_info = await response.json()
                    media_url = media_info.get("url")
                    
                    if media_url:
                        # Download actual media
                        async with self.session.get(media_url) as media_response:
                            if media_response.status == 200:
                                return await media_response.read()
            
            return None
            
        except Exception:
            return None
    
    async def _get_client_from_number(self, phone_number: str) -> Optional[str]:
        """Get client ID from phone number mapping"""
        cache_key = f"whatsapp_client:{phone_number}"
        client_id = self.redis_client.get(cache_key)
        
        if client_id:
            return client_id
        
        # In production, query database for number-to-client mapping
        # For now, return None to prompt registration
        return None
    
    async def _get_client_support_tier(self, client_id: str) -> str:
        """Get client support tier"""
        # This would query the database for client tier
        # For now, return default
        return "professional"
    
    async def _check_rate_limit(self, operation: str):
        """Check rate limits for WhatsApp API"""
        rate_key = f"whatsapp_rate:{operation}"
        current_count = self.redis_client.incr(rate_key)
        
        if current_count == 1:
            # Set expiry based on operation
            if operation == "messaging":
                self.redis_client.expire(rate_key, 1)  # 1 second
            elif operation == "media":
                self.redis_client.expire(rate_key, 60)  # 1 minute
            else:
                self.redis_client.expire(rate_key, 86400)  # 1 day
        
        limit = self.rate_limits.get(operation, 100)
        if current_count > limit:
            raise Exception(f"Rate limit exceeded for {operation}")
    
    async def _log_message_usage(
        self,
        payload: Dict[str, Any],
        client_id: Optional[str]
    ):
        """Log message usage for billing"""
        if not client_id:
            return
        
        message_type = payload.get("type", "text")
        
        # Calculate cost based on message type
        costs = {
            "text": 0.005,      # $0.005 per text
            "audio": 0.015,     # $0.015 per audio
            "image": 0.010,     # $0.010 per image
            "document": 0.020,  # $0.020 per document
            "template": 0.025   # $0.025 per template
        }
        
        cost = costs.get(message_type, 0.005)
        
        # Store in cache for batch processing
        usage_key = f"whatsapp_usage:{client_id}:{datetime.now().strftime('%Y%m%d')}"
        usage_data = {
            "message_type": message_type,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.redis_client.lpush(usage_key, json.dumps(usage_data))
        self.redis_client.expire(usage_key, 86400 * 7)  # Keep for 7 days


# Dependency injection
whatsapp_client = WhatsAppBusinessClient()

async def get_whatsapp_client() -> WhatsAppBusinessClient:
    """Get WhatsApp client instance"""
    return whatsapp_client