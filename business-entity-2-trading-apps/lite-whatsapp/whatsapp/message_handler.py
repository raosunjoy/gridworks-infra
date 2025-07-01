"""
WhatsApp Message Handler
Core logic for processing and responding to WhatsApp messages
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.ai.conversation_engine import ConversationEngine
from app.whatsapp.client import WhatsAppClient
from app.whatsapp.models import MessageStatus
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.core.database import get_async_session

logger = logging.getLogger(__name__)


class WhatsAppMessageHandler:
    """Handles incoming WhatsApp messages and coordinates responses"""
    
    def __init__(self):
        self.whatsapp_client = WhatsAppClient()
        self.conversation_engine = ConversationEngine()
        
    async def handle_text_message(
        self,
        user_phone: str,
        message_id: str,
        text: str,
        timestamp: str
    ):
        """Handle incoming text messages"""
        
        try:
            # Get or create user
            user = await self._get_or_create_user(user_phone)
            
            # Store incoming message
            await self._store_message(
                user_id=user.id,
                message_id=message_id,
                content=text,
                message_type="text",
                direction="incoming",
                timestamp=timestamp
            )
            
            # Show typing indicator
            await self.whatsapp_client.send_typing_indicator(user_phone)
            
            # Process message through AI engine
            response = await self.conversation_engine.process_message(
                user_id=user.id,
                message=text,
                context=await self._get_conversation_context(user.id)
            )
            
            # Send response back to user
            if response.get('type') == 'text':
                await self.whatsapp_client.send_text_message(
                    phone_number=user_phone,
                    message=response['content']
                )
            
            elif response.get('type') == 'interactive':
                await self.whatsapp_client.send_interactive_message(
                    phone_number=user_phone,
                    message=response['content'],
                    buttons=response.get('buttons', [])
                )
            
            elif response.get('type') == 'list':
                await self.whatsapp_client.send_list_message(
                    phone_number=user_phone,
                    message=response['content'],
                    sections=response.get('sections', [])
                )
            
            # Execute any actions requested by AI
            if response.get('actions'):
                await self._execute_actions(user.id, response['actions'])
                
        except Exception as e:
            logger.error(f"❌ Error handling text message: {str(e)}")
            await self._send_error_response(user_phone)
    
    async def handle_audio_message(
        self,
        user_phone: str,
        message_id: str,
        audio_id: str,
        timestamp: str
    ):
        """Handle incoming voice messages"""
        
        try:
            # Get or create user
            user = await self._get_or_create_user(user_phone)
            
            # Download and transcribe audio
            audio_url = await self.whatsapp_client.get_media_url(audio_id)
            transcription = await self.conversation_engine.transcribe_audio(audio_url)
            
            # Store original audio message
            await self._store_message(
                user_id=user.id,
                message_id=message_id,
                content=f"[Voice Message: {transcription}]",
                message_type="audio",
                direction="incoming",
                timestamp=timestamp,
                media_id=audio_id
            )
            
            # Process transcribed text
            await self.handle_text_message(
                user_phone=user_phone,
                message_id=f"{message_id}_transcribed",
                text=transcription,
                timestamp=timestamp
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling audio message: {str(e)}")
            await self._send_error_response(user_phone)
    
    async def handle_image_message(
        self,
        user_phone: str,
        message_id: str,
        image_id: str,
        caption: str,
        timestamp: str
    ):
        """Handle incoming images (e.g., screenshots of trading platforms)"""
        
        try:
            # Get or create user
            user = await self._get_or_create_user(user_phone)
            
            # Download and analyze image
            image_url = await self.whatsapp_client.get_media_url(image_id)
            image_analysis = await self.conversation_engine.analyze_image(
                image_url=image_url,
                caption=caption
            )
            
            # Store image message
            await self._store_message(
                user_id=user.id,
                message_id=message_id,
                content=f"[Image: {caption}] Analysis: {image_analysis}",
                message_type="image",
                direction="incoming",
                timestamp=timestamp,
                media_id=image_id
            )
            
            # Respond with image analysis
            response_text = f"📸 I can see your image! {image_analysis}"
            await self.whatsapp_client.send_text_message(user_phone, response_text)
            
        except Exception as e:
            logger.error(f"❌ Error handling image message: {str(e)}")
            await self._send_error_response(user_phone)
    
    async def handle_interactive_message(
        self,
        user_phone: str,
        message_id: str,
        interactive_data: Dict[str, Any],
        timestamp: str
    ):
        """Handle interactive messages (button clicks, list selections)"""
        
        try:
            # Get or create user
            user = await self._get_or_create_user(user_phone)
            
            # Extract interaction details
            interaction_type = interactive_data['type']  # button_reply, list_reply
            
            if interaction_type == 'button_reply':
                button_id = interactive_data['button_reply']['id']
                button_title = interactive_data['button_reply']['title']
                content = f"[Button: {button_title}] ID: {button_id}"
                
            elif interaction_type == 'list_reply':
                list_id = interactive_data['list_reply']['id']
                list_title = interactive_data['list_reply']['title']
                content = f"[List Selection: {list_title}] ID: {list_id}"
            
            else:
                content = f"[Interactive: {interaction_type}]"
            
            # Store interaction
            await self._store_message(
                user_id=user.id,
                message_id=message_id,
                content=content,
                message_type="interactive",
                direction="incoming",
                timestamp=timestamp
            )
            
            # Process interaction through AI
            response = await self.conversation_engine.process_interaction(
                user_id=user.id,
                interaction_type=interaction_type,
                interaction_data=interactive_data,
                context=await self._get_conversation_context(user.id)
            )
            
            # Send response
            await self.whatsapp_client.send_text_message(
                phone_number=user_phone,
                message=response['content']
            )
            
        except Exception as e:
            logger.error(f"❌ Error handling interactive message: {str(e)}")
            await self._send_error_response(user_phone)
    
    async def update_message_status(
        self,
        message_id: str,
        recipient_id: str,
        status: MessageStatus,
        timestamp: Optional[str] = None
    ):
        """Update message delivery status"""
        
        try:
            async with get_async_session() as session:
                # Find and update message status
                # Implementation depends on your database schema
                logger.info(f"📋 Updated message {message_id} status to {status.value}")
                
        except Exception as e:
            logger.error(f"❌ Error updating message status: {str(e)}")
    
    async def _get_or_create_user(self, phone_number: str) -> User:
        """Get existing user or create new one"""
        
        async with get_async_session() as session:
            # Implementation will depend on your User model
            # For now, return a mock user object
            return User(
                id=f"user_{phone_number}",
                phone_number=phone_number,
                is_active=True,
                created_at=datetime.utcnow()
            )
    
    async def _store_message(
        self,
        user_id: str,
        message_id: str,
        content: str,
        message_type: str,
        direction: str,
        timestamp: str,
        media_id: Optional[str] = None
    ):
        """Store message in database"""
        
        try:
            # Store message in database
            # Implementation will depend on your Message model
            logger.info(f"💾 Stored {direction} {message_type} message: {message_id}")
            
        except Exception as e:
            logger.error(f"❌ Error storing message: {str(e)}")
    
    async def _get_conversation_context(self, user_id: str) -> Dict[str, Any]:
        """Get recent conversation context for AI processing"""
        
        try:
            # Fetch recent messages and user context
            # Implementation will depend on your database schema
            return {
                "user_id": user_id,
                "recent_messages": [],
                "user_preferences": {},
                "trading_context": {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation context: {str(e)}")
            return {}
    
    async def _execute_actions(self, user_id: str, actions: list):
        """Execute actions requested by AI (trades, alerts, etc.)"""
        
        for action in actions:
            try:
                action_type = action.get('type')
                
                if action_type == 'place_order':
                    # Handle trade execution
                    logger.info(f"🎯 Executing trade action for user {user_id}")
                    
                elif action_type == 'set_alert':
                    # Handle price alerts
                    logger.info(f"🔔 Setting alert for user {user_id}")
                    
                elif action_type == 'update_portfolio':
                    # Handle portfolio updates
                    logger.info(f"📊 Updating portfolio for user {user_id}")
                
            except Exception as e:
                logger.error(f"❌ Error executing action {action_type}: {str(e)}")
    
    async def _send_error_response(self, phone_number: str):
        """Send friendly error message to user"""
        
        error_message = """😅 Sorry, I'm having trouble processing your message right now. 

Please try again in a moment, or type 'help' if you need assistance!"""
        
        try:
            await self.whatsapp_client.send_text_message(phone_number, error_message)
        except Exception as e:
            logger.error(f"❌ Failed to send error response: {str(e)}")