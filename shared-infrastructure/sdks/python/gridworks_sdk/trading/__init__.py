"""
Trading-as-a-Service for GridWorks SDK
"""

from typing import Dict, Any, Optional, List
from ..models.common import APIResponse


class TradingClient:
    """Trading client for multi-exchange trading with risk management"""
    
    def __init__(self, sdk):
        self.sdk = sdk
    
    def place_order(self,
                   symbol: str,
                   side: str,
                   quantity: float,
                   order_type: str = "market",
                   price: Optional[float] = None,
                   exchange: Optional[str] = None) -> APIResponse:
        """
        Place trading order
        
        Args:
            symbol: Trading symbol
            side: Order side (buy/sell)
            quantity: Order quantity
            order_type: Order type (market, limit, stop)
            price: Order price (for limit orders)
            exchange: Target exchange
            
        Returns:
            Order response
        """
        order_data = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "orderType": order_type
        }
        if price:
            order_data["price"] = price
        if exchange:
            order_data["exchange"] = exchange
            
        return self.sdk.request("POST", "/api/v1/trading/orders", order_data)
    
    def cancel_order(self, order_id: str) -> APIResponse:
        """
        Cancel trading order
        
        Args:
            order_id: Order identifier
            
        Returns:
            Cancellation result
        """
        return self.sdk.request("DELETE", f"/api/v1/trading/orders/{order_id}")
    
    def get_order(self, order_id: str) -> APIResponse:
        """
        Get order status
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order details
        """
        return self.sdk.request("GET", f"/api/v1/trading/orders/{order_id}")
    
    def get_orders(self, 
                   filters: Optional[Dict[str, Any]] = None,
                   page: int = 1,
                   limit: int = 50) -> APIResponse:
        """
        Get order history
        
        Args:
            filters: Order filters
            page: Page number
            limit: Results per page
            
        Returns:
            Order list
        """
        params = {"page": page, "limit": limit}
        if filters:
            params.update(filters)
        return self.sdk.request("GET", "/api/v1/trading/orders", {"params": params})
    
    def get_quote(self, symbol: str, exchange: Optional[str] = None) -> APIResponse:
        """
        Get real-time quote
        
        Args:
            symbol: Trading symbol
            exchange: Exchange identifier
            
        Returns:
            Market quote
        """
        params = {}
        if exchange:
            params["exchange"] = exchange
        return self.sdk.request("GET", f"/api/v1/trading/quote/{symbol}", {"params": params})
    
    def get_candles(self,
                   symbol: str,
                   interval: str = "1d",
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   limit: int = 100) -> APIResponse:
        """
        Get historical price candles
        
        Args:
            symbol: Trading symbol
            interval: Candle interval
            start_time: Start time
            end_time: End time
            limit: Number of candles
            
        Returns:
            Price candles
        """
        params = {"interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self.sdk.request("GET", f"/api/v1/trading/candles/{symbol}", {"params": params})
    
    def assess_risk(self,
                   portfolio_id: str,
                   proposed_trade: Optional[Dict[str, Any]] = None) -> APIResponse:
        """
        Assess portfolio or trade risk
        
        Args:
            portfolio_id: Portfolio identifier
            proposed_trade: Proposed trade data
            
        Returns:
            Risk assessment
        """
        request_data = {"portfolioId": portfolio_id}
        if proposed_trade:
            request_data["proposedTrade"] = proposed_trade
        return self.sdk.request("POST", "/api/v1/trading/risk/assess", request_data)
    
    def pre_trade_risk_check(self, order_data: Dict[str, Any]) -> APIResponse:
        """
        Pre-trade risk validation
        
        Args:
            order_data: Order information
            
        Returns:
            Risk check result
        """
        return self.sdk.request("POST", "/api/v1/trading/risk/pre-trade", order_data)
    
    def get_account(self, account_id: Optional[str] = None) -> APIResponse:
        """
        Get trading account details
        
        Args:
            account_id: Account identifier (optional)
            
        Returns:
            Account information
        """
        endpoint = f"/api/v1/trading/accounts/{account_id}" if account_id else "/api/v1/trading/accounts/default"
        return self.sdk.request("GET", endpoint)
    
    def get_positions(self, account_id: Optional[str] = None) -> APIResponse:
        """
        Get portfolio positions
        
        Args:
            account_id: Account identifier (optional)
            
        Returns:
            Position list
        """
        endpoint = f"/api/v1/trading/accounts/{account_id}/positions" if account_id else "/api/v1/trading/positions"
        return self.sdk.request("GET", endpoint)
    
    def get_portfolio_performance(self,
                                 portfolio_id: str,
                                 timeframe: str = "1M") -> APIResponse:
        """
        Get portfolio performance analytics
        
        Args:
            portfolio_id: Portfolio identifier
            timeframe: Performance timeframe
            
        Returns:
            Performance metrics
        """
        return self.sdk.request("GET", f"/api/v1/trading/portfolio/{portfolio_id}/performance", {
            "params": {"timeframe": timeframe}
        })
    
    def get_exchanges(self) -> APIResponse:
        """
        Get available exchanges
        
        Returns:
            Exchange list
        """
        return self.sdk.request("GET", "/api/v1/trading/exchanges")
    
    def health_check(self) -> APIResponse:
        """
        Check trading services health
        
        Returns:
            Health status
        """
        return self.sdk.request("GET", "/api/v1/trading/health")