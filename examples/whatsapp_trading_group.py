"""
Example: WhatsApp Trading Group Integration
Shows how to create and manage AI-moderated trading groups
"""

import asyncio
from app.sdk_manager import create_trading_group_sdk


async def main():
    """Example WhatsApp trading group setup"""
    
    # Group configuration
    group_config = {
        "group_id": "nifty_experts_premium",
        "group_name": "Nifty Experts Premium",
        "api_key": "group_api_key_abc789",
        "webhook_urls": {
            "moderation": "https://api.gridworks.ai/webhook/moderation",
            "analytics": "https://api.gridworks.ai/webhook/analytics"
        },
        "moderation_settings": {
            "auto_delete_spam": True,
            "expert_verification_required": True,
            "max_members": 50,
            "language": "english"
        }
    }
    
    # Initialize SDK
    sdk = create_trading_group_sdk(group_config)
    await sdk.initialize_services()
    
    print("🎯 GridWorks AI Moderator initialized for trading group")
    
    # Example 1: Set up expert-led group
    print("\n👑 Setting up expert-led group...")
    
    expert_setup = await sdk.setup_expert_group(
        expert_id="expert_raj_trader",
        group_settings={
            "expert_credentials": [
                {
                    "type": "sebi_registration",
                    "document_url": "https://example.com/sebi_cert.pdf"
                },
                {
                    "type": "trading_screenshot", 
                    "document_url": "https://example.com/pnl_screenshot.png"
                }
            ],
            "subscription_price": 2999,  # ₹2999/month
            "max_members": 25
        }
    )
    
    if expert_setup["success"]:
        expert_data = expert_setup["expert_verification"]
        print(f"✅ Expert verified: {expert_data['tier_eligible']} tier")
        print(f"📊 Verification score: {expert_data['verification_score']:.2f}")
    else:
        print(f"❌ Expert setup failed: {expert_setup['error']}")
    
    # Example 2: Moderate incoming messages
    print("\n🛡️ Moderating group messages...")
    
    test_messages = [
        {
            "message_id": "msg_001",
            "user_id": "expert_raj_trader",
            "content": "BUY RELIANCE @ 2500, Target 2600, SL 2450",
            "group_id": "nifty_experts_premium",
            "timestamp": "2025-06-30T09:15:00Z"
        },
        {
            "message_id": "msg_002", 
            "user_id": "spam_user_123",
            "content": "GUARANTEED 100% PROFIT! Join my telegram channel for sure shot tips!",
            "group_id": "nifty_experts_premium",
            "timestamp": "2025-06-30T09:16:00Z"
        },
        {
            "message_id": "msg_003",
            "user_id": "regular_user_456",
            "content": "What's your view on TCS after the results?",
            "group_id": "nifty_experts_premium",
            "timestamp": "2025-06-30T09:17:00Z"
        }
    ]
    
    for message in test_messages:
        moderation_result = await sdk.process_request(
            service="moderator",
            action="moderate_message",
            data=message
        )
        
        if moderation_result.success:
            result = moderation_result.data
            print(f"\n📝 Message from {message['user_id'][:15]}...")
            
            if result["spam_analysis"]:
                spam_score = result["spam_analysis"]["spam_score"]
                print(f"🔍 Spam Score: {spam_score:.2f}")
                
                if spam_score > 0.6:
                    print("🚨 SPAM DETECTED - Message blocked")
                else:
                    print("✅ Message approved")
            
            if result["trading_call"]:
                call = result["trading_call"]
                print(f"📈 Trading Call: {call['action']} {call['symbol']} @ ₹{call['entry_price']}")
            
            if result["actions"]:
                for action in result["actions"]:
                    print(f"⚡ Action: {action['action_type']} - {action['reason']}")
    
    # Example 3: Get group analytics
    print("\n📊 Group Analytics:")
    analytics_result = await sdk.process_request(
        service="moderator",
        action="get_group_analytics",
        data={"group_id": "nifty_experts_premium"}
    )
    
    if analytics_result.success:
        analytics = analytics_result.data
        stats = analytics["statistics"]
        print(f"   Total Messages: {stats['total_messages']}")
        print(f"   Spam Detected: {stats['spam_detected']}")
        print(f"   Trading Calls: {stats['calls_tracked']}")
        print(f"   Active Users: {stats['active_users']}")
        print(f"   Spam Rate: {stats['spam_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(main())