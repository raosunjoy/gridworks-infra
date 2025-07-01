"""
Example: WhatsApp Business Integration
Shows how to integrate GridWorks AI with WhatsApp Business API
"""

import asyncio
from app.sdk_manager import create_whatsapp_sdk


async def main():
    """Example WhatsApp Business integration"""
    
    # WhatsApp Business configuration
    whatsapp_config = {
        "business_account_id": "103845762728293",
        "business_name": "TradeMate WhatsApp",
        "access_token": "EAAG1xZB...",  # WhatsApp Business API token
        "phone_number_id": "106540135772629",
        "webhook_verify_token": "gridworks_webhook_token",
        "app_secret": "whatsapp_app_secret_key"
    }
    
    # Initialize SDK with all services
    from app.sdk_manager import ServiceType
    sdk = create_whatsapp_sdk(
        whatsapp_config=whatsapp_config,
        services=[ServiceType.SUPPORT, ServiceType.INTELLIGENCE, ServiceType.MODERATOR]
    )
    
    await sdk.initialize_services()
    
    print("📱 GridWorks WhatsApp Business SDK initialized")
    
    # Example 1: Handle customer support via WhatsApp
    print("\n💬 Handling WhatsApp support query...")
    
    support_response = await sdk.process_request(
        service="support",
        action="query",
        data={
            "user_id": "+919876543210",
            "message": "मेरा ऑर्डर क्यों फेल हो गया? (Why did my order fail?)",
            "user_tier": "pro",
            "language": "hindi",
            "deliver_via_whatsapp": True
        }
    )
    
    print(f"✅ Support Response: {support_response.data['message']}")
    print(f"📱 Delivered via WhatsApp: {support_response.data.get('whatsapp_delivered', False)}")
    
    # Example 2: Send morning pulse via WhatsApp
    print("\n🌅 Sending morning pulse via WhatsApp...")
    
    pulse_response = await sdk.process_request(
        service="intelligence", 
        action="morning_pulse",
        data={
            "user_id": "+919876543210",
            "user_tier": "black",
            "delivery_channels": ["whatsapp", "api"],
            "language": "english"
        }
    )
    
    if pulse_response.success:
        pulse_data = pulse_response.data
        print(f"📊 Global Triggers: {len(pulse_data['global_triggers'])}")
        print(f"💡 Trade Ideas: {len(pulse_data['trade_ideas'])}")
        print(f"🎙️ Voice Note: {pulse_data['voice_note_url']}")
    
    # Example 3: Handle WhatsApp webhook (incoming message)
    print("\n📥 Simulating WhatsApp webhook...")
    
    # Simulate incoming webhook data
    webhook_data = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "103845762728293",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {
                        "display_phone_number": "918369180053",
                        "phone_number_id": "106540135772629"
                    },
                    "messages": [{
                        "from": "919876543210",
                        "id": "wamid.HBgMOTE4MzY5MTgwMDUzFQIAEhgUM0NBNzAyNjc2M0JBQzI0RUY4RTU",
                        "timestamp": "1688546510",
                        "text": {
                            "body": "What are today's best stock picks?"
                        },
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    # Convert webhook to our format
    message_data = {
        "from": "919876543210",
        "text": "What are today's best stock picks?",
        "id": "wamid.HBgMOTE4MzY5MTgwMDUzFQIAEhgUM0NBNzAyNjc2M0JBQzI0RUY4RTU"
    }
    
    webhook_response = await sdk.handle_whatsapp_webhook(message_data)
    
    if webhook_response["success"]:
        print("✅ Webhook processed successfully")
        print(f"📝 Response: {webhook_response.get('data', {}).get('message', 'No message')}")
    else:
        print(f"❌ Webhook processing failed: {webhook_response.get('error')}")
    
    # Example 4: Bulk morning pulse delivery
    print("\n📢 Bulk morning pulse delivery...")
    
    user_list = [
        {"phone": "+919876543210", "tier": "pro", "language": "english"},
        {"phone": "+919876543211", "tier": "lite", "language": "hindi"},
        {"phone": "+919876543212", "tier": "black", "language": "english"}
    ]
    
    delivery_results = []
    
    for user in user_list:
        result = await sdk.process_request(
            service="intelligence",
            action="morning_pulse", 
            data={
                "user_id": user["phone"],
                "user_tier": user["tier"],
                "delivery_channels": ["whatsapp"],
                "language": user["language"]
            }
        )
        delivery_results.append({
            "phone": user["phone"],
            "success": result.success,
            "tier": user["tier"]
        })
    
    successful_deliveries = sum(1 for r in delivery_results if r["success"])
    print(f"📊 Bulk Delivery: {successful_deliveries}/{len(user_list)} successful")
    
    # Example 5: WhatsApp group moderation
    print("\n🛡️ WhatsApp group moderation...")
    
    group_message = {
        "message_id": "group_msg_001",
        "user_id": "+919876543213",
        "username": "TradingGuru",
        "content": "🚀 SURE SHOT TIP: Buy XYZ stock for 200% guaranteed profit! Limited time offer!",
        "group_id": "premium_trading_group",
        "timestamp": "2025-06-30T10:00:00Z"
    }
    
    moderation_result = await sdk.process_request(
        service="moderator",
        action="moderate_message",
        data=group_message
    )
    
    if moderation_result.success:
        result = moderation_result.data
        spam_score = result["spam_analysis"]["spam_score"]
        
        print(f"🔍 Message spam score: {spam_score:.2f}")
        
        if result["actions"]:
            for action in result["actions"]:
                print(f"⚡ Moderation action: {action['action_type']}")
                if action["action_type"] == "delete":
                    print("🗑️ Spam message deleted automatically")
    
    # Example 6: Get comprehensive analytics
    print("\n📈 WhatsApp Integration Analytics:")
    analytics = await sdk.get_client_analytics()
    
    print(f"   Business Account: {whatsapp_config['business_name']}")
    print(f"   Total API Calls: {analytics['usage_statistics']['total_requests']}")
    print(f"   Services Used: {', '.join(analytics['usage_statistics']['services_used'])}")
    print(f"   Integration Health: {analytics['service_health']}")


if __name__ == "__main__":
    asyncio.run(main())