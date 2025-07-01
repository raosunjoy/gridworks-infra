"""
WhatsApp Business API Client
Handles all WhatsApp message sending and media operations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import httpx
import json
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp Business API client for sending messages"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def send_text_message(
        self,
        phone_number: str,
        message: str,
        preview_url: bool = False
    ) -> Dict[str, Any]:
        """Send text message to WhatsApp"""
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {
                "body": message,
                "preview_url": preview_url
            }
        }
        
        return await self._send_message(payload)
    
    async def send_interactive_message(
        self,
        phone_number: str,
        message: str,
        buttons: List[Dict[str, str]],
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send interactive message with buttons"""
        
        # Build interactive payload
        interactive_payload = {
            "type": "button",
            "body": {"text": message}
        }
        
        if header:
            interactive_payload["header"] = {"type": "text", "text": header}
        
        if footer:
            interactive_payload["footer"] = {"text": footer}
        
        # Add buttons (max 3 buttons allowed)
        interactive_payload["action"] = {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {
                        "id": btn["id"],
                        "title": btn["title"][:20]  # Max 20 chars
                    }
                }
                for btn in buttons[:3]  # Max 3 buttons
            ]
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": interactive_payload
        }
        
        return await self._send_message(payload)
    
    async def send_list_message(
        self,
        phone_number: str,
        message: str,
        sections: List[Dict[str, Any]],
        button_text: str = "Choose Option",
        header: Optional[str] = None,
        footer: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send interactive list message"""
        
        interactive_payload = {
            "type": "list",
            "body": {"text": message}
        }
        
        if header:
            interactive_payload["header"] = {"type": "text", "text": header}
        
        if footer:
            interactive_payload["footer"] = {"text": footer}
        
        # Build sections with rows
        list_sections = []
        for section in sections:
            section_data = {
                "title": section["title"],
                "rows": [
                    {
                        "id": row["id"],
                        "title": row["title"][:24],  # Max 24 chars
                        "description": row.get("description", "")[:72]  # Max 72 chars
                    }
                    for row in section.get("rows", [])[:10]  # Max 10 rows per section
                ]
            }
            list_sections.append(section_data)
        
        interactive_payload["action"] = {
            "button": button_text[:20],  # Max 20 chars
            "sections": list_sections
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": interactive_payload
        }
        
        return await self._send_message(payload)
    
    async def send_media_message(
        self,
        phone_number: str,
        media_type: str,
        media_id: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send media message (image, audio, video, document)"""
        
        media_payload = {"id": media_id}
        if caption:
            media_payload["caption"] = caption
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": media_type,
            media_type: media_payload
        }
        
        return await self._send_message(payload)
    
    async def send_template_message(
        self,
        phone_number: str,
        template_name: str,
        language_code: str = "en",
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send template message"""
        
        template_payload = {
            "name": template_name,
            "language": {"code": language_code}
        }
        
        if parameters:
            template_payload["components"] = [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param}
                        for param in parameters
                    ]
                }
            ]
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": template_payload
        }
        
        return await self._send_message(payload)
    
    async def send_typing_indicator(self, phone_number: str) -> Dict[str, Any]:
        """Send typing indicator"""
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": "Typing..."}
        }
        
        # Send and immediately mark as read
        response = await self._send_message(payload)
        await asyncio.sleep(0.5)  # Brief delay
        return response
    
    async def mark_message_read(self, message_id: str) -> Dict[str, Any]:
        """Mark message as read"""
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to mark message as read: {response.text}")
                return {"error": response.text}
    
    async def get_media_url(self, media_id: str) -> str:
        """Get media URL from media ID"""
        
        url = f"{self.base_url}/{media_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("url", "")
            else:
                logger.error(f"❌ Failed to get media URL: {response.text}")
                return ""
    
    async def download_media(self, media_url: str) -> bytes:
        """Download media content"""
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                media_url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=60
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"❌ Failed to download media: {response.text}")
                return b""
    
    async def upload_media(
        self,
        media_type: str,
        media_content: bytes,
        filename: str
    ) -> str:
        """Upload media and get media ID"""
        
        url = f"{self.base_url}/{self.phone_number_id}/media"
        
        files = {
            "file": (filename, media_content, f"image/{media_type}"),
            "type": (None, media_type),
            "messaging_product": (None, "whatsapp")
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                files=files,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("id", "")
            else:
                logger.error(f"❌ Failed to upload media: {response.text}")
                return ""
    
    async def send_portfolio_summary(
        self,
        phone_number: str,
        portfolio_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send formatted portfolio summary"""
        
        # Generate portfolio message
        message = await self._format_portfolio_message(portfolio_data)
        
        # Add action buttons
        buttons = [
            {"id": "refresh_portfolio", "title": "🔄 Refresh"},
            {"id": "add_investment", "title": "➕ Invest More"},
            {"id": "portfolio_details", "title": "📊 Details"}
        ]
        
        return await self.send_interactive_message(
            phone_number=phone_number,
            message=message,
            buttons=buttons,
            header="📊 Portfolio Update"
        )
    
    async def send_trade_confirmation(
        self,
        phone_number: str,
        trade_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send trade confirmation with action buttons"""
        
        message = f"""📈 **Trade Ready for Execution**

**{trade_data['action'].upper()}**: {trade_data['symbol']}
**Quantity**: {trade_data['quantity']} shares
**Price**: ₹{trade_data['price']:,.2f}
**Total**: ₹{trade_data['total_amount']:,.2f}

**Charges**: ₹{trade_data['charges']:,.2f}
**Net Amount**: ₹{trade_data['net_amount']:,.2f}

⚠️ **Risk Level**: {trade_data.get('risk_level', 'Medium')}"""
        
        buttons = [
            {"id": "confirm_trade", "title": "✅ Confirm"},
            {"id": "modify_trade", "title": "📝 Modify"},
            {"id": "cancel_trade", "title": "❌ Cancel"}
        ]
        
        return await self.send_interactive_message(
            phone_number=phone_number,
            message=message,
            buttons=buttons
        )
    
    async def send_market_alert(
        self,
        phone_number: str,
        alert_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send market alerts and notifications"""
        
        alert_type = alert_data.get('type', 'general')
        
        if alert_type == 'price_alert':
            message = f"""🔔 **Price Alert Triggered!**

**{alert_data['symbol']}** has reached your target!

**Current Price**: ₹{alert_data['current_price']:,.2f}
**Target Price**: ₹{alert_data['target_price']:,.2f}
**Change**: {alert_data['change_percent']:+.1f}%

What would you like to do?"""
            
            buttons = [
                {"id": f"buy_{alert_data['symbol']}", "title": "💰 Buy Now"},
                {"id": f"sell_{alert_data['symbol']}", "title": "💸 Sell Now"},
                {"id": "update_alert", "title": "🔄 Update Alert"}
            ]
        
        elif alert_type == 'news_alert':
            message = f"""📰 **Market News Alert**

**{alert_data['headline']}**

**Impact**: {alert_data['impact_level']}
**Affected Stocks**: {', '.join(alert_data['affected_stocks'])}

{alert_data['summary'][:200]}..."""
            
            buttons = [
                {"id": "read_full_news", "title": "📖 Read Full"},
                {"id": "portfolio_impact", "title": "📊 My Impact"},
                {"id": "ignore_news", "title": "❌ Dismiss"}
            ]
        
        else:
            message = alert_data.get('message', 'Market update available!')
            buttons = [
                {"id": "view_details", "title": "👀 View Details"},
                {"id": "dismiss_alert", "title": "❌ Dismiss"}
            ]
        
        return await self.send_interactive_message(
            phone_number=phone_number,
            message=message,
            buttons=buttons
        )
    
    async def send_social_trading_update(
        self,
        phone_number: str,
        social_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send social trading updates"""
        
        update_type = social_data.get('type', 'general')
        
        if update_type == 'copy_trade_alert':
            message = f"""🔄 **Copy Trade Alert**

**{social_data['leader_name']}** just made a trade:

**Action**: {social_data['action']} {social_data['symbol']}
**Quantity**: {social_data['quantity']} shares
**Price**: ₹{social_data['price']:,.2f}

**Your Copy Settings**:
• Copy Ratio: {social_data['copy_ratio']}%
• Your Quantity: {social_data['your_quantity']} shares
• Your Investment: ₹{social_data['your_amount']:,.2f}

Execute copy trade?"""
            
            buttons = [
                {"id": "execute_copy", "title": "✅ Copy Trade"},
                {"id": "skip_copy", "title": "⏭️ Skip Once"},
                {"id": "modify_copy", "title": "📝 Modify"}
            ]
        
        elif update_type == 'leader_performance':
            message = f"""⭐ **Trader Performance Update**

**{social_data['leader_name']}** (Following: {social_data['followers_count']})

**This Month**:
• Return: {social_data['monthly_return']:+.1f}%
• Success Rate: {social_data['success_rate']:.1f}%
• Total Trades: {social_data['total_trades']}

**Portfolio**: {', '.join(social_data['top_holdings'])}

Your copy performance: {social_data['your_copy_return']:+.1f}%"""
            
            buttons = [
                {"id": "view_trades", "title": "📊 View Trades"},
                {"id": "adjust_copy", "title": "⚙️ Settings"},
                {"id": "unfollow", "title": "❌ Unfollow"}
            ]
        
        return await self.send_interactive_message(
            phone_number=phone_number,
            message=message,
            buttons=buttons
        )
    
    async def _send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to send message to WhatsApp API"""
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                logger.info(f"📤 WhatsApp API Response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Message sent successfully: {result}")
                    return result
                else:
                    error_data = response.json() if response.content else {"error": "Unknown error"}
                    logger.error(f"❌ WhatsApp API Error: {response.status_code} - {error_data}")
                    return {"error": error_data, "status_code": response.status_code}
        
        except Exception as e:
            logger.error(f"❌ WhatsApp client error: {str(e)}")
            return {"error": str(e)}
    
    async def _format_portfolio_message(self, portfolio_data: Dict[str, Any]) -> str:
        """Format portfolio data into WhatsApp message"""
        
        total_value = portfolio_data.get('total_value', 0)
        day_pnl = portfolio_data.get('day_pnl', 0)
        total_pnl = portfolio_data.get('total_pnl', 0)
        holdings = portfolio_data.get('holdings', [])
        
        message = f"""📊 **Portfolio Summary**

**Total Value**: ₹{total_value:,.2f}
**Today's P&L**: ₹{day_pnl:+,.2f}
**Overall P&L**: ₹{total_pnl:+,.2f}

**Top Holdings**:"""
        
        for holding in holdings[:3]:  # Show top 3
            pnl_emoji = "🟢" if holding.get('pnl', 0) >= 0 else "🔴"
            message += f"""
{pnl_emoji} **{holding['symbol']}**: ₹{holding['current_value']:,.0f}
   {holding['quantity']} @ ₹{holding['current_price']:.1f} ({holding['pnl_percent']:+.1f}%)"""
        
        if len(holdings) > 3:
            message += f"\n\n📈 +{len(holdings) - 3} more holdings"
        
        return message