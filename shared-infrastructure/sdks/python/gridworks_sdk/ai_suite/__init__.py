"""
AI Suite Services for GridWorks SDK
"""

from typing import Dict, Any, Optional, List
from ..models.common import APIResponse


class AISuiteClient:
    """AI Suite client for multi-language support, intelligence, and moderation"""
    
    def __init__(self, sdk):
        self.sdk = sdk
    
    def get_support(self, 
                    message: str, 
                    language: str = "en",
                    context: Optional[Dict[str, Any]] = None,
                    priority: str = "medium") -> APIResponse:
        """
        Get AI support response
        
        Args:
            message: Support request message
            language: Language code (en, hi, ta, etc.)
            context: Additional context
            priority: Request priority
            
        Returns:
            Support response
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/support", {
            "message": message,
            "language": language,
            "context": context or {},
            "priority": priority
        })
    
    def get_whatsapp_support(self,
                            message: str,
                            phone_number: str,
                            context: Optional[Dict[str, Any]] = None) -> APIResponse:
        """
        Get support via WhatsApp Business
        
        Args:
            message: Support message
            phone_number: WhatsApp phone number
            context: Additional context
            
        Returns:
            WhatsApp support response
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/support/whatsapp", {
            "message": message,
            "phoneNumber": phone_number,
            "context": context or {}
        })
    
    def get_morning_pulse(self,
                         markets: List[str] = None,
                         delivery_format: str = "text") -> APIResponse:
        """
        Get morning pulse market intelligence
        
        Args:
            markets: List of markets (NSE, BSE, NASDAQ, etc.)
            delivery_format: Format (text, voice, whatsapp)
            
        Returns:
            Morning pulse analysis
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/intelligence", {
            "type": "morning_pulse",
            "parameters": {
                "markets": markets or ["NSE", "BSE", "NASDAQ"],
                "analysisDepth": "comprehensive"
            },
            "deliveryFormat": delivery_format
        })
    
    def get_market_correlation(self,
                              source_market: str,
                              target_markets: List[str],
                              timeframe: str = "1M") -> APIResponse:
        """
        Get market correlation analysis
        
        Args:
            source_market: Source market code
            target_markets: List of target markets
            timeframe: Analysis timeframe
            
        Returns:
            Correlation analysis
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/intelligence", {
            "type": "market_correlation",
            "parameters": {
                "markets": [source_market] + target_markets,
                "timeframe": timeframe,
                "analysisDepth": "detailed"
            }
        })
    
    def moderate_content(self,
                        content: str,
                        content_type: str = "text",
                        source: Optional[str] = None) -> APIResponse:
        """
        Moderate content for compliance
        
        Args:
            content: Content to moderate
            content_type: Type of content (text, image, voice)
            source: Source platform (whatsapp, telegram, etc.)
            
        Returns:
            Moderation result
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/moderation", {
            "content": content,
            "contentType": content_type,
            "source": source
        })
    
    def verify_expert(self, expert_id: str) -> APIResponse:
        """
        Verify expert credentials
        
        Args:
            expert_id: Expert identifier
            
        Returns:
            Expert verification result
        """
        return self.sdk.request("GET", f"/api/v1/ai-suite/experts/{expert_id}/verify")
    
    def send_whatsapp_message(self,
                             to: str,
                             content: str,
                             message_type: str = "text") -> APIResponse:
        """
        Send WhatsApp message
        
        Args:
            to: Recipient phone number
            content: Message content
            message_type: Message type (text, voice, document)
            
        Returns:
            Message send result
        """
        return self.sdk.request("POST", "/api/v1/ai-suite/whatsapp/send", {
            "to": to,
            "type": message_type,
            "content": content
        })
    
    def get_usage_analytics(self, timeframe: str = "30d") -> APIResponse:
        """
        Get AI Suite usage analytics
        
        Args:
            timeframe: Analytics timeframe
            
        Returns:
            Usage analytics
        """
        return self.sdk.request("GET", "/api/v1/ai-suite/analytics", {
            "params": {"timeframe": timeframe}
        })
    
    def health_check(self) -> APIResponse:
        """
        Check AI Suite service health
        
        Returns:
            Health status
        """
        return self.sdk.request("GET", "/api/v1/ai-suite/health")