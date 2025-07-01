"""
Example: Broker Integration with GridWorks AI SDK
Shows how a trading broker can integrate all AI services
"""

import asyncio
from app.sdk_manager import create_broker_sdk


async def main():
    """Example broker integration"""
    
    # Broker configuration
    broker_config = {
        "broker_id": "zerodha_demo",
        "broker_name": "Zerodha Kite",
        "api_key": "broker_api_key_xyz123",
        "tier_mapping": {
            "basic": "lite",
            "pro": "pro", 
            "premium": "black"
        },
        "billing_config": {
            "model": "per_request",
            "monthly_cap": 100000  # ₹1L monthly cap
        }
    }
    
    # Initialize SDK
    sdk = create_broker_sdk(broker_config)
    await sdk.initialize_services()
    
    print("🚀 GridWorks AI SDK initialized for Zerodha")
    
    # Example 1: Handle customer support query
    print("\n📞 Handling customer support query...")
    
    support_response = await sdk.handle_customer_query(
        user_id="user_12345",
        query="My order failed with error. Can you help?",
        user_tier="pro"
    )
    
    print(f"✅ Support Response: {support_response.data['message']}")
    print(f"💰 Cost: ₹{support_response.billing_info['cost']}")
    
    # Example 2: Get morning intelligence for VIP users
    print("\n🌅 Getting morning intelligence...")
    
    vip_users = ["user_12345", "user_67890", "user_54321"]
    intelligence_results = await sdk.get_daily_market_intelligence(vip_users)
    
    for result in intelligence_results:
        if result.success:
            data = result.data
            print(f"📊 Trade Ideas for user: {len(data['trade_ideas'])} ideas")
            if data['trade_ideas']:
                idea = data['trade_ideas'][0]
                print(f"   💡 {idea['action']} {idea['symbol']} @ ₹{idea['entry_price']}")
    
    # Example 3: Get analytics
    print("\n📈 Client Analytics:")
    analytics = await sdk.get_client_analytics()
    print(f"   Total Requests: {analytics['usage_statistics']['total_requests']}")
    print(f"   Total Cost: ₹{analytics['usage_statistics']['total_cost']}")
    print(f"   Services Used: {analytics['usage_statistics']['services_used']}")


if __name__ == "__main__":
    asyncio.run(main())