"""
Banking-as-a-Service for GridWorks SDK
"""

from typing import Dict, Any, Optional, List
from ..models.common import APIResponse


class BankingClient:
    """Banking client for payment processing, account management, and compliance"""
    
    def __init__(self, sdk):
        self.sdk = sdk
    
    def process_payment(self,
                       amount: float,
                       currency: str,
                       from_account: str,
                       to_account: str,
                       payment_method: str = "bank_transfer",
                       purpose: str = "Payment") -> APIResponse:
        """
        Process payment
        
        Args:
            amount: Payment amount
            currency: Currency code
            from_account: Source account
            to_account: Destination account
            payment_method: Payment method
            purpose: Payment purpose
            
        Returns:
            Payment response
        """
        return self.sdk.request("POST", "/api/v1/banking/payments", {
            "amount": amount,
            "currency": currency,
            "fromAccount": from_account,
            "toAccount": to_account,
            "paymentMethod": payment_method,
            "purpose": purpose
        })
    
    def get_payment(self, payment_id: str) -> APIResponse:
        """
        Get payment status
        
        Args:
            payment_id: Payment identifier
            
        Returns:
            Payment details
        """
        return self.sdk.request("GET", f"/api/v1/banking/payments/{payment_id}")
    
    def cancel_payment(self, payment_id: str, reason: Optional[str] = None) -> APIResponse:
        """
        Cancel payment
        
        Args:
            payment_id: Payment identifier
            reason: Cancellation reason
            
        Returns:
            Cancellation result
        """
        return self.sdk.request("POST", f"/api/v1/banking/payments/{payment_id}/cancel", {
            "reason": reason
        })
    
    def create_account(self,
                      account_type: str,
                      currency: str,
                      client_id: str,
                      account_name: str,
                      purpose: str) -> APIResponse:
        """
        Create bank account
        
        Args:
            account_type: Type of account
            currency: Account currency
            client_id: Client identifier
            account_name: Account name
            purpose: Account purpose
            
        Returns:
            Account creation result
        """
        return self.sdk.request("POST", "/api/v1/banking/accounts", {
            "accountType": account_type,
            "currency": currency,
            "clientId": client_id,
            "accountName": account_name,
            "purpose": purpose
        })
    
    def get_account(self, account_id: str) -> APIResponse:
        """
        Get account details
        
        Args:
            account_id: Account identifier
            
        Returns:
            Account information
        """
        return self.sdk.request("GET", f"/api/v1/banking/accounts/{account_id}")
    
    def get_account_balance(self, account_id: str) -> APIResponse:
        """
        Get account balance
        
        Args:
            account_id: Account identifier
            
        Returns:
            Account balance
        """
        return self.sdk.request("GET", f"/api/v1/banking/accounts/{account_id}/balance")
    
    def create_escrow(self,
                     amount: float,
                     currency: str,
                     parties: Dict[str, Any],
                     terms: Dict[str, Any],
                     timeline: Dict[str, Any]) -> APIResponse:
        """
        Create escrow agreement
        
        Args:
            amount: Escrow amount
            currency: Currency code
            parties: Involved parties
            terms: Escrow terms
            timeline: Timeline information
            
        Returns:
            Escrow creation result
        """
        return self.sdk.request("POST", "/api/v1/banking/escrow", {
            "amount": amount,
            "currency": currency,
            "parties": parties,
            "terms": terms,
            "timeline": timeline
        })
    
    def fund_escrow(self,
                   escrow_id: str,
                   amount: float,
                   from_account_id: str) -> APIResponse:
        """
        Fund escrow account
        
        Args:
            escrow_id: Escrow identifier
            amount: Funding amount
            from_account_id: Source account
            
        Returns:
            Funding result
        """
        return self.sdk.request("POST", f"/api/v1/banking/escrow/{escrow_id}/fund", {
            "amount": amount,
            "fromAccountId": from_account_id
        })
    
    def release_escrow(self,
                      escrow_id: str,
                      amount: float,
                      milestone: Optional[str] = None) -> APIResponse:
        """
        Release escrow funds
        
        Args:
            escrow_id: Escrow identifier
            amount: Release amount
            milestone: Milestone reference
            
        Returns:
            Release result
        """
        return self.sdk.request("POST", f"/api/v1/banking/escrow/{escrow_id}/release", {
            "amount": amount,
            "milestone": milestone
        })
    
    def perform_kyc(self, client_id: str, documents: List[Dict[str, Any]]) -> APIResponse:
        """
        Perform KYC verification
        
        Args:
            client_id: Client identifier
            documents: KYC documents
            
        Returns:
            KYC result
        """
        return self.sdk.request("POST", "/api/v1/banking/compliance/kyc", {
            "clientId": client_id,
            "documents": documents
        })
    
    def perform_aml(self, client_id: str, transaction_data: Optional[Dict[str, Any]] = None) -> APIResponse:
        """
        Perform AML screening
        
        Args:
            client_id: Client identifier
            transaction_data: Transaction information
            
        Returns:
            AML screening result
        """
        return self.sdk.request("POST", "/api/v1/banking/compliance/aml", {
            "clientId": client_id,
            "transactionData": transaction_data
        })
    
    def get_exchange_rate(self,
                         from_currency: str,
                         to_currency: str,
                         amount: Optional[float] = None) -> APIResponse:
        """
        Get currency exchange rate
        
        Args:
            from_currency: Source currency
            to_currency: Target currency
            amount: Amount to convert
            
        Returns:
            Exchange rate information
        """
        params = {
            "fromCurrency": from_currency,
            "toCurrency": to_currency
        }
        if amount:
            params["amount"] = amount
        return self.sdk.request("GET", "/api/v1/banking/exchange/rate", {"params": params})
    
    def exchange_currency(self,
                         from_account: str,
                         to_account: str,
                         from_currency: str,
                         to_currency: str,
                         amount: float) -> APIResponse:
        """
        Execute currency exchange
        
        Args:
            from_account: Source account
            to_account: Target account
            from_currency: Source currency
            to_currency: Target currency
            amount: Amount to exchange
            
        Returns:
            Exchange result
        """
        return self.sdk.request("POST", "/api/v1/banking/exchange/execute", {
            "fromAccount": from_account,
            "toAccount": to_account,
            "fromCurrency": from_currency,
            "toCurrency": to_currency,
            "amount": amount
        })
    
    def initiate_wire_transfer(self, wire_data: Dict[str, Any]) -> APIResponse:
        """
        Initiate wire transfer
        
        Args:
            wire_data: Wire transfer information
            
        Returns:
            Wire transfer result
        """
        return self.sdk.request("POST", "/api/v1/banking/wire", wire_data)
    
    def get_compliance_status(self, client_id: str) -> APIResponse:
        """
        Get compliance status for client
        
        Args:
            client_id: Client identifier
            
        Returns:
            Compliance status
        """
        return self.sdk.request("GET", f"/api/v1/banking/compliance/status/{client_id}")
    
    def health_check(self) -> APIResponse:
        """
        Check banking services health
        
        Returns:
            Health status
        """
        return self.sdk.request("GET", "/api/v1/banking/health")