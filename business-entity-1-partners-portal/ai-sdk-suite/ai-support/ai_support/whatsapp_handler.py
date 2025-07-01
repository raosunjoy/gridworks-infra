"""
WhatsApp Integration Layer for AI Support
Ultra-fast message processing with tier-aware routing
"""

import asyncio
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import redis
import aiohttp
from dataclasses import asdict

from .models import SupportMessage, SupportTier, MessageType, UserContext
from .universal_engine import UniversalAISupport
from .tier_ux import TierUXRenderer, WhatsAppUXFormatter

logger = logging.getLogger(__name__)


class WhatsAppSupportHandler:
    """Ultra-fast WhatsApp support message processing"""
    
    def __init__(self):
        # Core components
        self.ai_engine = UniversalAISupport()
        self.ux_renderer = TierUXRenderer()
        
        # Redis for message queuing
        self.redis = redis.Redis(decode_responses=True)
        self.message_queue = "support_messages"
        
        # WhatsApp API configuration
        self.whatsapp_api = WhatsAppBusinessAPI()
        
        # Language detection cache
        self.language_cache = {}
        
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming WhatsApp webhook for support"""
        
        try:
            # Parse webhook data
            message = await self._parse_webhook(webhook_data)
            if not message:
                return {"status": "ignored", "reason": "not_support_message"}
            
            # Immediate acknowledgment
            await self._send_typing_indicator(message)
            
            # Queue for processing
            await self._queue_message(message)
            
            # Process immediately (async)
            asyncio.create_task(self._process_message_async(message))
            
            return {"status": "queued", "message_id": message.id}
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _parse_webhook(self, webhook_data: Dict[str, Any]) -> Optional[SupportMessage]:
        """Parse WhatsApp webhook into SupportMessage"""
        
        try:
            # Extract message data from webhook
            if "messages" not in webhook_data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
                return None
                
            messages = webhook_data["entry"][0]["changes"][0]["value"]["messages"]
            if not messages:
                return None
                
            msg_data = messages[0]
            
            # Get user phone
            phone = msg_data.get("from", "")
            
            # Get message content
            msg_type = msg_data.get("type", "text")
            if msg_type == "text":
                content = msg_data.get("text", {}).get("body", "")
            elif msg_type == "voice":
                content = "[Voice Message]"  # Would transcribe in production
            else:
                content = f"[{msg_type.upper()} Message]"
            
            # Skip if not support-related
            if not await self._is_support_message(content):
                return None
            
            # Get user context
            user_context = await self._get_user_context(phone)
            if not user_context:
                return None
            
            # Detect language
            language = await self._detect_language(content, phone)
            
            # Calculate priority
            priority = await self._calculate_priority(content, user_context.tier)
            
            return SupportMessage(
                id=msg_data.get("id", ""),
                user_id=user_context.user_id,
                phone=phone,
                message=content,
                message_type=MessageType(msg_type),
                language=language,
                timestamp=datetime.utcnow(),
                user_tier=user_context.tier,
                priority=priority
            )
            
        except Exception as e:
            logger.error(f"Message parsing failed: {e}")
            return None
    
    async def _is_support_message(self, content: str) -> bool:
        """Determine if message is support-related"""
        
        support_keywords = [
            "help", "problem", "issue", "error", "failed", "stuck", "cancel",
            "order", "money", "payment", "kyc", "portfolio", "trade", "support",
            "madad", "samasya", "dikkat", "paisa", "galat", "band", "ruk"  # Hindi keywords
        ]
        
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in support_keywords)
    
    async def _get_user_context(self, phone: str) -> Optional[UserContext]:
        """Get user context from phone number"""
        
        # In production, this would query user database
        # For now, return mock data
        
        # Mock user data based on phone
        if phone.endswith("0001"):
            tier = SupportTier.BLACK
            name = "Rajesh Gupta"
            portfolio_value = 5000000
        elif phone.endswith("0002"):
            tier = SupportTier.ELITE
            name = "Priya Sharma"
            portfolio_value = 1000000
        elif phone.endswith("0003"):
            tier = SupportTier.PRO
            name = "Amit Kumar"
            portfolio_value = 250000
        else:
            tier = SupportTier.LITE
            name = "User"
            portfolio_value = 50000
        
        return UserContext(
            user_id=hashlib.md5(phone.encode()).hexdigest(),
            tier=tier,
            name=name,
            portfolio_value=portfolio_value,
            recent_orders=[
                {"id": "12345", "symbol": "TCS", "quantity": 10, "status": "failed"},
                {"id": "12346", "symbol": "RELIANCE", "quantity": 5, "status": "completed"}
            ],
            balance=10000,
            kyc_status="verified",
            preferred_language="en",
            trading_history={"total_trades": 150, "success_rate": 95},
            risk_profile="moderate"
        )
    
    async def _detect_language(self, content: str, phone: str) -> str:
        """Detect message language with caching"""
        
        # Check cache first
        cache_key = f"lang:{phone}"
        cached_lang = self.language_cache.get(cache_key)
        if cached_lang:
            return cached_lang
        
        # Simple language detection (would use proper model in production)
        hindi_keywords = ["mera", "kya", "kaise", "paisa", "order", "dikkat", "madad"]
        english_keywords = ["my", "what", "how", "money", "order", "problem", "help"]
        
        content_lower = content.lower()
        
        hindi_score = sum(1 for keyword in hindi_keywords if keyword in content_lower)
        english_score = sum(1 for keyword in english_keywords if keyword in content_lower)
        
        detected_lang = "hi" if hindi_score > english_score else "en"
        
        # Cache for future use
        self.language_cache[cache_key] = detected_lang
        
        return detected_lang
    
    async def _calculate_priority(self, content: str, tier: SupportTier) -> int:
        """Calculate message priority for queue routing"""
        
        # Base priority by tier
        tier_priority = {
            SupportTier.BLACK: 5,
            SupportTier.ELITE: 4,
            SupportTier.PRO: 3,
            SupportTier.LITE: 2
        }
        
        base_priority = tier_priority[tier]
        
        # Urgency keywords boost
        urgent_keywords = [
            "stuck", "money", "loss", "error", "failed", "emergency", "urgent",
            "paisa", "atka", "galat", "jaldi", "turant"  # Hindi urgent words
        ]
        
        content_lower = content.lower()
        if any(keyword in content_lower for keyword in urgent_keywords):
            base_priority = min(5, base_priority + 1)
        
        return base_priority
    
    async def _send_typing_indicator(self, message: SupportMessage):
        """Send typing indicator to user"""
        
        try:
            await self.whatsapp_api.send_typing_indicator(message.phone)
        except Exception as e:
            logger.warning(f"Failed to send typing indicator: {e}")
    
    async def _queue_message(self, message: SupportMessage):
        """Queue message for processing"""
        
        try:
            # Add to Redis queue with priority
            queue_data = {
                "message": asdict(message),
                "priority": message.priority,
                "queued_at": time.time()
            }
            
            await self.redis.lpush(self.message_queue, json.dumps(queue_data))
            
        except Exception as e:
            logger.error(f"Message queuing failed: {e}")
    
    async def _process_message_async(self, message: SupportMessage):
        """Process support message asynchronously"""
        
        try:
            start_time = time.time()
            
            # Get user context
            user_context = await self._get_user_context(message.phone)
            if not user_context:
                await self._send_error_response(message, "User context not found")
                return
            
            # Process with AI engine
            ai_response = await self.ai_engine.process_support_request(message, user_context)
            
            # Render tier-specific UX
            tier_response = await self.ux_renderer.render_tier_response(
                ai_response, message, user_context
            )
            
            # Format for WhatsApp
            whatsapp_message = await WhatsAppUXFormatter.format_for_whatsapp(tier_response)
            
            # Send response
            await self._send_response(message, whatsapp_message, tier_response)
            
            # Log performance
            processing_time = time.time() - start_time
            await self._log_performance(message, processing_time, ai_response.confidence)
            
        except Exception as e:
            logger.error(f"Message processing failed for {message.id}: {e}")
            await self._send_error_response(message, "Processing error occurred")
    
    async def _send_response(
        self,
        message: SupportMessage,
        whatsapp_text: str,
        tier_response: Dict[str, Any]
    ):
        """Send response via WhatsApp"""
        
        try:
            # Send main message
            await self.whatsapp_api.send_message(message.phone, whatsapp_text)
            
            # Send action buttons if supported
            if tier_response.get("actions"):
                await self._send_quick_actions(message.phone, tier_response["actions"])
                
        except Exception as e:
            logger.error(f"Failed to send response: {e}")
    
    async def _send_quick_actions(self, phone: str, actions: List[Dict[str, Any]]):
        """Send interactive quick action buttons"""
        
        try:
            # Format as WhatsApp interactive buttons (if supported)
            button_data = {
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": "Choose an action:"},
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": action.get("action", f"action_{i}"),
                                    "title": action.get("text", "Action")[:20]  # WhatsApp limit
                                }
                            }
                            for i, action in enumerate(actions[:3])  # Max 3 buttons
                        ]
                    }
                }
            }
            
            await self.whatsapp_api.send_interactive_message(phone, button_data)
            
        except Exception as e:
            logger.warning(f"Failed to send quick actions: {e}")
    
    async def _send_error_response(self, message: SupportMessage, error: str):
        """Send error response to user"""
        
        error_messages = {
            SupportTier.BLACK: "◆ I apologize for the technical difficulty. Your dedicated butler will call you immediately.",
            SupportTier.ELITE: "👑 Technical issue encountered. Connecting you to an expert advisor now.",
            SupportTier.PRO: "⚡ System issue detected. Priority support will contact you within 5 minutes.",
            SupportTier.LITE: "System error occurred. Our team will help you shortly. Please try again in a moment."
        }
        
        error_msg = error_messages.get(message.user_tier, error_messages[SupportTier.LITE])
        
        try:
            await self.whatsapp_api.send_message(message.phone, error_msg)
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")
    
    async def _log_performance(self, message: SupportMessage, processing_time: float, confidence: float):
        """Log performance metrics"""
        
        try:
            performance_data = {
                "message_id": message.id,
                "user_tier": message.user_tier.value,
                "processing_time": processing_time,
                "confidence": confidence,
                "timestamp": time.time(),
                "language": message.language,
                "priority": message.priority
            }
            
            # Store in Redis for monitoring
            await self.redis.lpush("support_performance", json.dumps(performance_data))
            
            # Log to application logs
            logger.info(f"Support processed: {message.id} | {message.user_tier.value} | {processing_time:.3f}s")
            
        except Exception as e:
            logger.warning(f"Performance logging failed: {e}")


class WhatsAppBusinessAPI:
    """WhatsApp Business API client for support messages"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = "YOUR_PHONE_NUMBER_ID"  # Configure in production
        self.access_token = "YOUR_ACCESS_TOKEN"  # Configure in production
        
    async def send_message(self, to_phone: str, message: str) -> bool:
        """Send text message via WhatsApp Business API"""
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message}
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"WhatsApp message send failed: {e}")
            return False
    
    async def send_interactive_message(self, to_phone: str, interactive_data: Dict[str, Any]) -> bool:
        """Send interactive message with buttons"""
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                **interactive_data
            }
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"WhatsApp interactive message send failed: {e}")
            return False
    
    async def send_typing_indicator(self, to_phone: str) -> bool:
        """Send typing indicator"""
        
        try:
            # WhatsApp Business API doesn't support typing indicators directly
            # This would be implemented via webhook status updates
            return True
            
        except Exception as e:
            logger.error(f"Typing indicator failed: {e}")
            return False


class SupportMessageProcessor:
    """Background message processor for queued support messages"""
    
    def __init__(self, handler: WhatsAppSupportHandler):
        self.handler = handler
        self.redis = handler.redis
        self.running = False
    
    async def start_processing(self):
        """Start background message processing"""
        
        self.running = True
        logger.info("Support message processor started")
        
        while self.running:
            try:
                # Get message from queue (blocking with timeout)
                queue_data = await self.redis.brpop(
                    self.handler.message_queue, 
                    timeout=5
                )
                
                if queue_data:
                    # Parse queue data
                    message_data = json.loads(queue_data[1])
                    message_dict = message_data["message"]
                    
                    # Convert back to SupportMessage
                    message = SupportMessage(**message_dict)
                    
                    # Process message
                    await self.handler._process_message_async(message)
                    
            except Exception as e:
                logger.error(f"Queue processing error: {e}")
                await asyncio.sleep(1)
    
    async def stop_processing(self):
        """Stop background processing"""
        
        self.running = False
        logger.info("Support message processor stopped")