"""
Example: User Tier Progression Journey
Shows how a user progresses from Lite → Pro → Elite → Black with AI SDK integration
"""

import asyncio
from datetime import datetime, timedelta
from app.tier_integration.tier_ai_manager import TierAIManager, UserTier


class MockUser:
    """Mock user for demonstration"""
    
    def __init__(self, user_id: str, name: str, tier: UserTier):
        self.id = user_id
        self.name = name
        self.tier = tier
        self.portfolio_value = 100000  # Starting with ₹1L
        self.balance = 50000
        self.days_active = 0
        self.ai_interactions = []
        self.revenue_earned = 0
    
    def log_interaction(self, service: str, action: str, success: bool = True):
        """Log AI service interaction"""
        self.ai_interactions.append({
            "timestamp": datetime.now(),
            "service": service,
            "action": action,
            "success": success,
            "tier": self.tier.value
        })
    
    def upgrade_tier(self, new_tier: UserTier):
        """Upgrade user tier"""
        old_tier = self.tier.value
        self.tier = new_tier
        print(f"🎉 {self.name} upgraded from {old_tier.upper()} to {new_tier.value.upper()}!")
    
    def simulate_trading_success(self):
        """Simulate successful trading"""
        growth = 1.15  # 15% growth
        self.portfolio_value = int(self.portfolio_value * growth)
        print(f"📈 {self.name}'s portfolio grew to ₹{self.portfolio_value:,}")


async def demonstrate_user_journey():
    """Demonstrate complete user journey through all tiers"""
    
    tier_manager = TierAIManager()
    
    # Create a new user starting at Lite tier
    user = MockUser("user_123", "Rajesh Kumar", UserTier.LITE)
    print(f"👋 Welcome {user.name}! Starting journey at {user.tier.value.upper()} tier\n")
    
    # =============================================================================
    # LITE TIER EXPERIENCE (Days 1-30)
    # =============================================================================
    print("🔵 LITE TIER EXPERIENCE")
    print("=" * 50)
    
    # Day 1: User tries AI support
    print(f"Day 1: {user.name} asks AI support about order failure")
    support_response = await tier_manager.handle_ai_support_request(
        user_id=user.id,
        user_tier=user.tier,
        query="Why did my order fail? I had sufficient balance.",
        context={"balance": user.balance}
    )
    
    user.log_interaction("support", "query")
    print(f"✅ AI Response: {support_response.get('message', 'Order failure usually due to insufficient margin...')[:80]}...")
    
    if support_response.get('upsell_offer'):
        print(f"💡 Upsell shown: {support_response['upsell_offer'].get('message', 'Upgrade for better features')}")
    
    # Day 3: User discovers morning pulse
    print(f"\nDay 3: {user.name} checks morning pulse")
    pulse_response = await tier_manager.handle_morning_pulse_request(
        user_id=user.id,
        user_tier=user.tier
    )
    
    user.log_interaction("intelligence", "morning_pulse")
    print(f"📊 Morning Pulse: {pulse_response.get('content', {}).get('summary', 'Market summary available')}")
    
    if pulse_response.get('upsell_offer'):
        print(f"🎵 Teaser: {pulse_response['upsell_offer'].get('cta', 'Upgrade for voice notes!')}")
    
    # Day 7: User hits support limit
    print(f"\nDay 7: {user.name} hits daily support limit")
    for i in range(6):  # Try 6 queries (limit is 5)
        response = await tier_manager.handle_ai_support_request(
            user_id=user.id,
            user_tier=user.tier,
            query=f"Query {i+1}: How to read charts?",
            context={"balance": user.balance}
        )
        user.log_interaction("support", "query", response.get("success", True))
        
        if not response.get("success"):
            print(f"❌ Query {i+1} blocked: {response.get('error')}")
            print(f"💰 Upsell triggered: {response.get('upsell', {}).get('message', 'Upgrade to Pro')}")
            break
    
    # Day 15: User tries to join expert group
    print(f"\nDay 15: {user.name} tries to join expert group")
    group_response = await tier_manager.handle_expert_group_request(
        user_id=user.id,
        user_tier=user.tier,
        action="join_group",
        data={"group_id": "nifty_experts"}
    )
    
    user.log_interaction("moderator", "join_group", group_response.get("success", False))
    if not group_response.get("success"):
        print(f"⚠️ Restricted: {group_response.get('message', 'Upgrade to participate')}")
    
    # Day 30: User decides to upgrade after consistent usage
    print(f"\nDay 30: After 30 days of consistent usage, {user.name} upgrades to PRO")
    user.upgrade_tier(UserTier.PRO)
    user.simulate_trading_success()
    
    print(f"\n{'='*60}\n")
    
    # =============================================================================
    # PRO TIER EXPERIENCE (Days 31-90)
    # =============================================================================
    print("🟡 PRO TIER EXPERIENCE")
    print("=" * 50)
    
    # Day 31: First Pro experience
    print(f"Day 31: {user.name} gets first Pro morning pulse with voice note")
    pro_pulse = await tier_manager.handle_morning_pulse_request(
        user_id=user.id,
        user_tier=user.tier
    )
    
    user.log_interaction("intelligence", "morning_pulse_pro")
    print(f"🎙️ Voice note delivered: {pro_pulse.get('voice_note_url', 'voice_note_123.mp3')}")
    print(f"💡 Trade ideas: {len(pro_pulse.get('trade_ideas', []))} specific recommendations")
    
    # Day 35: User executes trade ideas
    print(f"\nDay 35: {user.name} executes Pro trade ideas")
    trade_ideas = pro_pulse.get('trade_ideas', [{'symbol': 'TCS', 'action': 'BUY', 'entry_price': 3900}])
    for idea in trade_ideas[:2]:
        print(f"📈 Executed: {idea.get('action')} {idea.get('symbol')} @ ₹{idea.get('entry_price')}")
    
    user.simulate_trading_success()
    
    # Day 50: User joins expert groups
    print(f"\nDay 50: {user.name} joins premium expert groups")
    group_join = await tier_manager.handle_expert_group_request(
        user_id=user.id,
        user_tier=user.tier,
        action="join_group",
        data={"group_id": "nifty_pro_signals"}
    )
    
    user.log_interaction("moderator", "join_expert_group")
    print(f"👥 Joined: Expert group with ₹1999/month subscription")
    
    # Day 70: User starts thinking about becoming expert
    print(f"\nDay 70: {user.name} has built good track record")
    user.simulate_trading_success()
    print(f"💼 Portfolio now: ₹{user.portfolio_value:,} (52% growth)")
    print(f"🎯 Trading accuracy: 73% (tracking from Pro trade ideas)")
    
    # Day 90: Upgrade to Elite triggered by success
    print(f"\nDay 90: {user.name}'s success triggers Elite upgrade offer")
    elite_upsell = await tier_manager.upsell_triggers.check_moderator_upsell(user.id, user.tier)
    if elite_upsell:
        print(f"💎 Elite offer: {elite_upsell.get('offer', 'Create expert groups and earn revenue')}")
    
    user.upgrade_tier(UserTier.ELITE)
    
    print(f"\n{'='*60}\n")
    
    # =============================================================================
    # ELITE TIER EXPERIENCE (Days 91-180)
    # =============================================================================
    print("🟣 ELITE TIER EXPERIENCE")
    print("=" * 50)
    
    # Day 91: Elite onboarding
    print(f"Day 91: {user.name} gets Elite personal AI butler")
    elite_support = await tier_manager.handle_ai_support_request(
        user_id=user.id,
        user_tier=user.tier,
        query="Analyze my portfolio and suggest optimization",
        context={"portfolio_value": user.portfolio_value}
    )
    
    user.log_interaction("support", "portfolio_analysis")
    print(f"🤖 AI Butler: Detailed portfolio analysis with video explanation")
    print(f"📱 Response time: 10 seconds (vs 15s in Pro)")
    
    # Day 100: Create first expert group
    print(f"\nDay 100: {user.name} creates expert group")
    group_creation = await tier_manager.handle_expert_group_request(
        user_id=user.id,
        user_tier=user.tier,
        action="create_group",
        data={
            "group_settings": {
                "name": "Rajesh's Swing Trading Signals",
                "subscription_price": 1999,
                "max_members": 30
            }
        }
    )
    
    user.log_interaction("moderator", "create_expert_group")
    print(f"👑 Created: Expert group with ₹1999/month subscription")
    print(f"🎯 AI moderation enabled for spam detection")
    
    # Day 130: Group starts earning
    print(f"\nDay 130: {user.name}'s expert group gains traction")
    members_joined = 23
    monthly_revenue = members_joined * 1999 * 0.75  # 75% revenue share for Elite
    user.revenue_earned += monthly_revenue
    
    print(f"👥 Members: {members_joined}/30")
    print(f"💰 Monthly revenue: ₹{monthly_revenue:,.0f} (75% share)")
    print(f"📊 Group rating: 4.6/5 stars")
    
    # Day 150: Portfolio growth accelerates
    print(f"\nDay 150: Elite features accelerate {user.name}'s growth")
    user.simulate_trading_success()
    user.portfolio_value = int(user.portfolio_value * 1.2)  # 20% additional growth
    print(f"📈 Portfolio: ₹{user.portfolio_value:,} (Elite AI optimization)")
    print(f"💎 Expert revenue: ₹{user.revenue_earned:,.0f} total earned")
    
    # Day 180: Black tier qualification
    print(f"\nDay 180: {user.name} qualifies for Black tier")
    if user.portfolio_value > 5000000:  # ₹50L+
        black_upsell = await tier_manager.upsell_triggers.check_moderator_upsell(user.id, user.tier)
        print(f"⚫ Black invitation: Institutional intelligence + unlimited earning")
        user.upgrade_tier(UserTier.BLACK)
    
    print(f"\n{'='*60}\n")
    
    # =============================================================================
    # BLACK TIER EXPERIENCE (Days 181+)
    # =============================================================================
    print("⚫ BLACK TIER EXPERIENCE")
    print("=" * 50)
    
    # Day 181: Black tier onboarding
    print(f"Day 181: {user.name} enters Black tier with institutional access")
    black_pulse = await tier_manager.handle_morning_pulse_request(
        user_id=user.id,
        user_tier=user.tier
    )
    
    user.log_interaction("intelligence", "institutional_briefing")
    print(f"🏛️ Institutional briefing: 10-page research report")
    print(f"📊 FII/DII flows: Real-time institutional activity")
    print(f"🔍 Block deals: Insider trading alerts")
    
    # Day 200: Institutional group creation
    print(f"\nDay 200: {user.name} creates institutional-grade group")
    institutional_group = await tier_manager.handle_expert_group_request(
        user_id=user.id,
        user_tier=user.tier,
        action="create_group",
        data={
            "group_settings": {
                "name": "Institutional Equity Strategies",
                "subscription_price": 25000,
                "max_members": 10,
                "institutional_grade": True
            }
        }
    )
    
    user.log_interaction("moderator", "create_institutional_group")
    print(f"🏦 Created: Institutional group at ₹25,000/month")
    print(f"⚫ White-label branding available")
    print(f"👨‍💼 Dedicated relationship manager assigned")
    
    # Day 220: Platform partnership
    print(f"\nDay 220: {user.name} becomes platform partner")
    institutional_members = 8
    institutional_revenue = institutional_members * 25000 * 0.85  # 85% share for Black
    user.revenue_earned += institutional_revenue
    
    print(f"🤝 Platform partnership: API access + white-label rights")
    print(f"💰 Monthly revenue: ₹{institutional_revenue:,.0f} (85% share)")
    print(f"📊 Total portfolio: ₹{user.portfolio_value:,}")
    print(f"💎 Total expert revenue: ₹{user.revenue_earned:,.0f}")
    
    # =============================================================================
    # JOURNEY SUMMARY
    # =============================================================================
    print(f"\n{'='*60}")
    print("🏆 JOURNEY SUMMARY")
    print("=" * 60)
    
    print(f"👤 User: {user.name}")
    print(f"📅 Journey duration: 220 days (7+ months)")
    print(f"🎯 Final tier: {user.tier.value.upper()}")
    print(f"📈 Portfolio growth: ₹100,000 → ₹{user.portfolio_value:,} ({((user.portfolio_value/100000)-1)*100:.0f}% gain)")
    print(f"💰 Expert revenue earned: ₹{user.revenue_earned:,.0f}")
    print(f"🔥 Total AI interactions: {len(user.ai_interactions)}")
    
    # Revenue attribution to AI SDKs
    print(f"\n💡 AI SDK Impact:")
    print(f"   🛡️ Support: Reduced query resolution time by 80%")
    print(f"   🌍 Intelligence: Enabled profitable trading decisions")
    print(f"   👥 Moderator: Created ₹{user.revenue_earned:,.0f} expert revenue stream")
    
    # Tier progression insights
    tier_progression = {}
    for interaction in user.ai_interactions:
        tier = interaction['tier']
        tier_progression[tier] = tier_progression.get(tier, 0) + 1
    
    print(f"\n📊 Usage by tier:")
    for tier, count in tier_progression.items():
        print(f"   {tier.upper()}: {count} interactions")
    
    print(f"\n🎉 Result: GridWorks AI SDKs transformed {user.name} from retail trader to institutional expert!")
    print(f"💰 Platform revenue from {user.name}: ₹{calculate_platform_revenue(user):,.0f}")
    
    return user


def calculate_platform_revenue(user: MockUser) -> float:
    """Calculate total platform revenue from user journey"""
    
    # Subscription revenue (simplified calculation)
    lite_days = 30
    pro_days = 60  # ₹999/month
    elite_days = 90  # ₹4999/month  
    black_days = 40  # ₹25000/month
    
    subscription_revenue = (
        0 +  # Lite is free
        (pro_days / 30) * 999 +  # Pro subscription
        (elite_days / 30) * 4999 +  # Elite subscription
        (black_days / 30) * 25000   # Black subscription
    )
    
    # Platform revenue share from expert earnings
    platform_share = user.revenue_earned * 0.20  # 20% platform cut
    
    total_platform_revenue = subscription_revenue + platform_share
    
    print(f"\n💰 Platform Revenue Breakdown:")
    print(f"   Subscriptions: ₹{subscription_revenue:,.0f}")
    print(f"   Revenue share: ₹{platform_share:,.0f}")
    print(f"   Total: ₹{total_platform_revenue:,.0f}")
    
    return total_platform_revenue


async def main():
    """Run the complete user journey demonstration"""
    
    print("🚀 GridWorks AI SDK Tier Integration Demo")
    print("=" * 60)
    print("Following a user's journey from Lite → Pro → Elite → Black")
    print("Showing how AI SDKs create value and drive tier progression\n")
    
    user = await demonstrate_user_journey()
    
    print(f"\n🎯 Key Insights:")
    print(f"1. AI SDKs create immediate value at every tier")
    print(f"2. Intelligent upselling drives natural progression")
    print(f"3. Revenue sharing creates win-win ecosystem")
    print(f"4. Platform becomes more valuable with network effects")
    print(f"\n✅ Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())