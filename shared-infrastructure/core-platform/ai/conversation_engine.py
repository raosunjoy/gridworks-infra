"""
AI Conversation Engine
Handles natural language processing, multilingual support, and financial intelligence
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime

import openai
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from googletrans import Translator

from app.core.config import settings
from app.ai.financial_agent import FinancialAgent
from app.ai.risk_analyzer import RiskAnalyzer
from app.ai.market_intelligence import MarketIntelligence
from app.models.user import UserProfile

logger = logging.getLogger(__name__)


class ConversationEngine:
    """Core AI engine for processing WhatsApp conversations"""
    
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = settings.OPENAI_API_KEY
        
        # Initialize components
        self.translator = Translator()
        self.financial_agent = FinancialAgent()
        self.risk_analyzer = RiskAnalyzer()
        self.market_intelligence = MarketIntelligence()
        
        # Language detection patterns
        self.language_patterns = {
            'hindi': r'[\u0900-\u097F]',
            'tamil': r'[\u0B80-\u0BFF]',
            'telugu': r'[\u0C00-\u0C7F]',
            'bengali': r'[\u0980-\u09FF]',
            'gujarati': r'[\u0A80-\u0AFF]',
            'punjabi': r'[\u0A00-\u0A7F]'
        }
        
        # Conversation memory per user
        self.conversation_memories = {}
    
    async def process_message(
        self,
        user_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Main message processing pipeline"""
        
        try:
            # Get user profile and preferences
            user_profile = await self._get_user_profile(user_id)
            
            # Detect language and translate if needed
            detected_language = self._detect_language(message)
            original_message = message
            
            if detected_language != 'english':
                message = await self._translate_to_english(message, detected_language)
                logger.info(f"🌍 Translated {detected_language} -> English: {message}")
            
            # Initialize conversation memory if needed
            if user_id not in self.conversation_memories:
                self.conversation_memories[user_id] = ConversationBufferWindowMemory(
                    k=10,  # Remember last 10 exchanges
                    return_messages=True
                )
            
            memory = self.conversation_memories[user_id]
            
            # Classify message intent
            intent = await self._classify_intent(message, context)
            
            # Process based on intent
            response = await self._process_by_intent(
                user_id=user_id,
                message=message,
                intent=intent,
                context=context,
                user_profile=user_profile
            )
            
            # Translate response back to user's language if needed
            if detected_language != 'english':
                response['content'] = await self._translate_from_english(
                    response['content'], 
                    detected_language
                )
            
            # Add to conversation memory
            memory.chat_memory.add_user_message(original_message)
            memory.chat_memory.add_ai_message(response['content'])
            
            # Add metadata
            response['metadata'] = {
                'intent': intent,
                'language': detected_language,
                'processing_time': datetime.utcnow().isoformat(),
                'user_id': user_id
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}")
            return await self._generate_error_response(detected_language)
    
    def _detect_language(self, text: str) -> str:
        """Detect the primary language of the text"""
        
        # Check for regional language scripts
        for lang, pattern in self.language_patterns.items():
            if re.search(pattern, text):
                return lang
        
        # Default to English if no regional script detected
        return 'english'
    
    async def _translate_to_english(self, text: str, source_language: str) -> str:
        """Translate text to English for processing"""
        
        try:
            # Language code mapping
            lang_codes = {
                'hindi': 'hi',
                'tamil': 'ta',
                'telugu': 'te',
                'bengali': 'bn',
                'gujarati': 'gu',
                'punjabi': 'pa'
            }
            
            source_code = lang_codes.get(source_language, 'auto')
            translation = self.translator.translate(text, src=source_code, dest='en')
            return translation.text
            
        except Exception as e:
            logger.error(f"❌ Translation error: {str(e)}")
            return text  # Return original if translation fails
    
    async def _translate_from_english(self, text: str, target_language: str) -> str:
        """Translate English response back to user's language"""
        
        try:
            lang_codes = {
                'hindi': 'hi',
                'tamil': 'ta',
                'telugu': 'te',
                'bengali': 'bn',
                'gujarati': 'gu',
                'punjabi': 'pa'
            }
            
            target_code = lang_codes.get(target_language, 'en')
            if target_code == 'en':
                return text
                
            translation = self.translator.translate(text, src='en', dest=target_code)
            return translation.text
            
        except Exception as e:
            logger.error(f"❌ Translation error: {str(e)}")
            return text
    
    async def _classify_intent(self, message: str, context: Dict[str, Any]) -> str:
        """Classify user message intent using AI"""
        
        system_prompt = """You are an AI assistant for a trading platform. Classify the user's intent from these categories:

TRADING_INTENTS:
- buy_stock: User wants to buy stocks/shares
- sell_stock: User wants to sell stocks/shares  
- check_portfolio: User wants to see their portfolio
- market_status: User asking about market conditions
- stock_price: User asking for specific stock prices
- place_order: User wants to place a trading order

INFORMATION_INTENTS:
- learn_trading: User wants to learn about trading
- explain_concept: User asking for financial concept explanation
- market_news: User wants market news and updates
- stock_analysis: User wants analysis of specific stocks

ACCOUNT_INTENTS:
- account_balance: User asking about account balance
- transaction_history: User wants to see past transactions
- kyc_status: User asking about KYC/account status
- deposit_money: User wants to add money to account

GENERAL_INTENTS:
- greeting: Hello, hi, good morning etc.
- help: User needs help or doesn't know what to do
- complaint: User has an issue or complaint
- other: Anything else

Respond with just the intent category, nothing else."""
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Message: {message}\nContext: {json.dumps(context)}"}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            intent = response.choices[0].message.content.strip().lower()
            logger.info(f"🎯 Classified intent: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"❌ Intent classification error: {str(e)}")
            return "other"
    
    async def _process_by_intent(
        self,
        user_id: str,
        message: str,
        intent: str,
        context: Dict[str, Any],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Process message based on classified intent"""
        
        if intent in ['buy_stock', 'sell_stock', 'place_order']:
            return await self._handle_trading_intent(user_id, message, intent, context)
        
        elif intent in ['check_portfolio', 'account_balance']:
            return await self._handle_portfolio_intent(user_id, message, intent, context)
        
        elif intent in ['market_status', 'stock_price', 'market_news']:
            return await self._handle_market_intent(user_id, message, intent, context)
        
        elif intent in ['learn_trading', 'explain_concept']:
            return await self._handle_education_intent(user_id, message, intent, context)
        
        elif intent == 'greeting':
            return await self._handle_greeting(user_id, user_profile)
        
        elif intent == 'help':
            return await self._handle_help_request(user_id, user_profile)
        
        else:
            return await self._handle_general_conversation(user_id, message, context)
    
    async def _handle_trading_intent(
        self,
        user_id: str,
        message: str,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle trading-related intents"""
        
        # Extract trading parameters using AI
        trading_params = await self.financial_agent.extract_trading_parameters(message)
        
        if not trading_params.get('symbol'):
            return {
                'type': 'text',
                'content': """I'd be happy to help you trade! 📈 

Could you please specify:
• Which stock/company? (e.g., "Reliance", "TCS", "HDFC Bank")
• How many shares?
• Buy or sell?

Example: "Buy 10 shares of Reliance" """,
                'actions': []
            }
        
        # Risk assessment
        risk_assessment = await self.risk_analyzer.assess_trade_risk(
            user_id=user_id,
            trading_params=trading_params
        )
        
        if risk_assessment['risk_level'] == 'HIGH':
            return {
                'type': 'interactive',
                'content': f"""⚠️ **Risk Alert for {trading_params['symbol']}**

{risk_assessment['warning_message']}

• Risk Level: {risk_assessment['risk_level']}
• Potential Loss: ₹{risk_assessment['max_loss']:,.0f}
• Recommendation: {risk_assessment['recommendation']}

Do you want to proceed?""",
                'buttons': [
                    {'id': 'proceed_trade', 'title': '✅ Proceed Anyway'},
                    {'id': 'modify_trade', 'title': '📝 Modify Order'},
                    {'id': 'cancel_trade', 'title': '❌ Cancel'}
                ],
                'actions': [{'type': 'risk_warning_shown', 'data': risk_assessment}]
            }
        
        # Generate trade confirmation
        return {
            'type': 'interactive',
            'content': f"""📊 **Trade Confirmation**

**{intent.replace('_', ' ').title()}**: {trading_params['symbol']}
**Quantity**: {trading_params['quantity']} shares
**Estimated Price**: ₹{trading_params['price']:,.2f}
**Total Amount**: ₹{trading_params['total_amount']:,.2f}

**Charges**: ₹{trading_params['charges']:,.2f}
**Final Amount**: ₹{trading_params['final_amount']:,.2f}

Confirm to proceed?""",
            'buttons': [
                {'id': 'confirm_trade', 'title': '✅ Confirm Trade'},
                {'id': 'cancel_trade', 'title': '❌ Cancel'}
            ],
            'actions': [{'type': 'trade_prepared', 'data': trading_params}]
        }
    
    async def _handle_portfolio_intent(
        self,
        user_id: str,
        message: str,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle portfolio and account related queries"""
        
        # Get portfolio data
        portfolio = await self.financial_agent.get_user_portfolio(user_id)
        
        if intent == 'check_portfolio':
            if not portfolio.get('holdings'):
                return {
                    'type': 'text',
                    'content': """📊 **Your Portfolio**

You don't have any holdings yet! 

🚀 **Ready to start investing?**
• Type "buy [stock name]" to purchase stocks
• Try "buy 1 share of Reliance" 
• Or ask "what should I buy?" for recommendations

Type 'help' to see all available commands! 💡""",
                    'actions': []
                }
            
            # Generate portfolio summary
            return await self._generate_portfolio_summary(portfolio)
        
        elif intent == 'account_balance':
            return {
                'type': 'text',
                'content': f"""💰 **Account Summary**

**Available Balance**: ₹{portfolio['available_balance']:,.2f}
**Invested Amount**: ₹{portfolio['invested_amount']:,.2f}
**Current Value**: ₹{portfolio['current_value']:,.2f}
**Total P&L**: ₹{portfolio['total_pnl']:+,.2f} ({portfolio['total_pnl_percent']:+.1f}%)

**Buying Power**: ₹{portfolio['buying_power']:,.2f}

Type 'portfolio' to see your holdings! 📊""",
                'actions': []
            }
    
    async def _handle_market_intent(
        self,
        user_id: str,
        message: str,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle market information requests"""
        
        if intent == 'market_status':
            market_summary = await self.market_intelligence.get_market_overview()
            return {
                'type': 'text',
                'content': market_summary,
                'actions': []
            }
        
        elif intent == 'stock_price':
            # Extract stock symbol from message
            symbol = await self.financial_agent.extract_stock_symbol(message)
            if symbol:
                stock_info = await self.market_intelligence.get_stock_info(symbol)
                return {
                    'type': 'text',
                    'content': stock_info,
                    'actions': []
                }
            else:
                return {
                    'type': 'text',
                    'content': """📈 **Stock Price Query**

Please specify which stock you'd like to check:
• Example: "Reliance price"  
• Example: "What's TCS trading at?"
• Example: "HDFC Bank current price"

Or type 'market' for overall market status! 🌍""",
                    'actions': []
                }
        
        elif intent == 'market_news':
            news_summary = await self.market_intelligence.get_market_news()
            return {
                'type': 'text',
                'content': news_summary,
                'actions': []
            }
    
    async def _handle_greeting(self, user_id: str, user_profile: UserProfile) -> Dict[str, Any]:
        """Handle greeting messages"""
        
        user_name = user_profile.name if user_profile.name else "there"
        
        return {
            'type': 'text',
            'content': f"""Hello {user_name}! 👋 Welcome to GridWorks! 

🚀 **I'm your AI trading assistant. I can help you:**
• Buy and sell stocks with simple messages
• Check your portfolio and account balance
• Get market updates and stock prices  
• Learn about trading and investments
• Manage your risk and find opportunities

**Quick Start:**
• Try: "Buy 5 shares of Reliance"
• Try: "What's my portfolio?"
• Try: "Market status today"

What would you like to do? 💡""",
            'actions': []
        }
    
    async def _handle_help_request(self, user_id: str, user_profile: UserProfile) -> Dict[str, Any]:
        """Handle help requests"""
        
        return {
            'type': 'list',
            'content': """🤖 **GridWorks Help Center**

Choose what you'd like help with:""",
            'sections': [
                {
                    'title': '📈 Trading Commands',
                    'rows': [
                        {'id': 'help_buy', 'title': 'How to Buy Stocks', 'description': 'Learn to place buy orders'},
                        {'id': 'help_sell', 'title': 'How to Sell Stocks', 'description': 'Learn to place sell orders'},
                        {'id': 'help_portfolio', 'title': 'Check Portfolio', 'description': 'View your holdings'}
                    ]
                },
                {
                    'title': '📊 Market Information',
                    'rows': [
                        {'id': 'help_prices', 'title': 'Stock Prices', 'description': 'Get current stock prices'},
                        {'id': 'help_market', 'title': 'Market Status', 'description': 'Overall market overview'},
                        {'id': 'help_news', 'title': 'Market News', 'description': 'Latest market updates'}
                    ]
                },
                {
                    'title': '🎓 Learning',
                    'rows': [
                        {'id': 'help_basics', 'title': 'Trading Basics', 'description': 'Learn fundamental concepts'},
                        {'id': 'help_risk', 'title': 'Risk Management', 'description': 'Understanding investment risks'},
                        {'id': 'help_strategies', 'title': 'Investment Strategies', 'description': 'Different approaches to investing'}
                    ]
                }
            ],
            'actions': []
        }
    
    async def _handle_general_conversation(
        self,
        user_id: str,
        message: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle general conversation using AI"""
        
        system_prompt = """You are GridWorks, an AI assistant for a WhatsApp-based trading platform in India. 

Key Guidelines:
- Be friendly, helpful, and conversational
- Use simple language that everyone can understand
- Include relevant emojis to make conversations engaging
- Always relate responses back to trading/investing when possible
- Encourage users to take action (check portfolio, place trades, learn)
- Use Indian context (₹ currency, Indian stocks, local examples)
- Keep responses concise (under 200 words)
- If unsure about trading advice, suggest consulting financial advisors

Examples of good responses:
- Use "₹" for currency
- Mention Indian companies like "Reliance", "TCS", "HDFC Bank"
- Include actionable next steps
- Be encouraging about wealth building"""
        
        try:
            # Get conversation history
            memory = self.conversation_memories.get(user_id)
            messages = []
            
            if memory:
                for msg in memory.chat_memory.messages[-6:]:  # Last 3 exchanges
                    if isinstance(msg, HumanMessage):
                        messages.append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": system_prompt}] + messages,
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'type': 'text',
                'content': ai_response,
                'actions': []
            }
            
        except Exception as e:
            logger.error(f"❌ General conversation error: {str(e)}")
            return await self._generate_error_response('english')
    
    async def _generate_portfolio_summary(self, portfolio: Dict[str, Any]) -> Dict[str, Any]:
        """Generate formatted portfolio summary"""
        
        holdings_text = ""
        for holding in portfolio['holdings'][:5]:  # Show top 5 holdings
            pnl_emoji = "🟢" if holding['pnl'] >= 0 else "🔴"
            holdings_text += f"""
{pnl_emoji} **{holding['symbol']}**
   {holding['quantity']} shares • ₹{holding['current_price']:.1f}
   P&L: ₹{holding['pnl']:+,.0f} ({holding['pnl_percent']:+.1f}%)"""
        
        summary = f"""📊 **Your Portfolio Summary**

**Total Value**: ₹{portfolio['total_value']:,.2f}
**Today's P&L**: ₹{portfolio['day_pnl']:+,.2f} ({portfolio['day_pnl_percent']:+.1f}%)
**Overall P&L**: ₹{portfolio['total_pnl']:+,.2f} ({portfolio['total_pnl_percent']:+.1f}%)

**Top Holdings:**{holdings_text}

💡 Type 'buy [stock]' to add more stocks or 'sell [stock]' to book profits!"""
        
        return {
            'type': 'text',
            'content': summary,
            'actions': []
        }
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile and trading preferences"""
        
        # This would typically fetch from database
        # For now, return a default profile
        return UserProfile(
            user_id=user_id,
            name=None,
            language_preference='english',
            risk_tolerance='medium',
            trading_experience='beginner'
        )
    
    async def _generate_error_response(self, language: str) -> Dict[str, Any]:
        """Generate user-friendly error response"""
        
        error_messages = {
            'english': """😅 I'm having a small hiccup right now! 

Please try again in a moment, or:
• Type 'help' for assistance
• Try a simpler command like 'portfolio' or 'market'
• Contact support if the issue persists

I'm here to help! 🤖""",
            'hindi': """😅 मुझे अभी थोड़ी समस्या हो रही है!

कृपया थोड़ी देर बाद फिर कोशिश करें, या:
• सहायता के लिए 'help' टाइप करें  
• 'portfolio' या 'market' जैसी सरल कमांड का प्रयास करें
• समस्या बनी रहने पर सपोर्ट से संपर्क करें

मैं आपकी मदद के लिए यहाँ हूँ! 🤖"""
        }
        
        return {
            'type': 'text',
            'content': error_messages.get(language, error_messages['english']),
            'actions': []
        }
    
    async def transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio message to text"""
        
        try:
            # Download audio file
            # Use OpenAI Whisper for transcription
            # This is a placeholder - implement actual audio processing
            return "Audio transcription feature coming soon!"
            
        except Exception as e:
            logger.error(f"❌ Audio transcription error: {str(e)}")
            return "Sorry, I couldn't understand the audio message."
    
    async def analyze_image(self, image_url: str, caption: str) -> str:
        """Analyze images using AI vision"""
        
        try:
            # Use OpenAI Vision API or similar to analyze images
            # This is a placeholder - implement actual image analysis
            return f"I can see an image! Caption: {caption}. Image analysis feature coming soon!"
            
        except Exception as e:
            logger.error(f"❌ Image analysis error: {str(e)}")
            return "I can see you sent an image, but I'm having trouble analyzing it right now."
    
    async def process_interaction(
        self,
        user_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process interactive button/list selections"""
        
        try:
            if interaction_type == 'button_reply':
                button_id = interaction_data['button_reply']['id']
                return await self._handle_button_interaction(user_id, button_id, context)
            
            elif interaction_type == 'list_reply':
                list_id = interaction_data['list_reply']['id']
                return await self._handle_list_interaction(user_id, list_id, context)
            
            else:
                return {
                    'type': 'text',
                    'content': "Thanks for the interaction! How else can I help you? 😊",
                    'actions': []
                }
                
        except Exception as e:
            logger.error(f"❌ Interaction processing error: {str(e)}")
            return await self._generate_error_response('english')
    
    async def _handle_button_interaction(
        self,
        user_id: str,
        button_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle button click interactions"""
        
        if button_id == 'confirm_trade':
            return {
                'type': 'text',
                'content': """✅ **Trade Confirmed!**

Your order has been placed successfully! 🎉

📱 You'll receive updates on:
• Order execution status
• Trade settlement
• Portfolio changes

Type 'portfolio' to see your updated holdings! 📊""",
                'actions': [{'type': 'execute_trade', 'data': context}]
            }
        
        elif button_id == 'cancel_trade':
            return {
                'type': 'text',
                'content': """❌ **Trade Cancelled**

No worries! Your order has been cancelled.

💡 **What's next?**
• Try modifying your order
• Check market conditions with 'market'
• Ask for stock recommendations

How else can I help you? 😊""",
                'actions': []
            }
        
        # Add more button handlers as needed
        return {
            'type': 'text',
            'content': "Thanks! How else can I assist you today? 😊",
            'actions': []
        }
    
    async def _handle_list_interaction(
        self,
        user_id: str,
        list_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list selection interactions"""
        
        # Map list selections to appropriate responses
        help_responses = {
            'help_buy': """📈 **How to Buy Stocks**

**Simple Commands:**
• "Buy 10 shares of Reliance"
• "Purchase TCS stock worth ₹5000"
• "Buy HDFC Bank"

**I'll handle:**
✅ Current price lookup
✅ Order calculation  
✅ Risk assessment
✅ Confirmation before execution

Try it now! Just say "Buy [stock name]" 🚀""",
            
            'help_sell': """📉 **How to Sell Stocks**  

**Simple Commands:**
• "Sell 5 shares of TCS"
• "Sell all my Reliance shares"
• "Book profit in HDFC Bank"

**I'll show you:**
✅ Current holdings
✅ Profit/loss calculation
✅ Tax implications
✅ Confirmation before selling

Type 'portfolio' first to see what you own! 💼""",
            
            'help_market': """🌍 **Market Information**

**Available Commands:**
• "Market status" - Overall market overview
• "Nifty today" - Index performance
• "TCS price" - Individual stock prices  
• "Market news" - Latest updates
• "Top gainers" - Best performing stocks

**Live Updates Include:**
📊 Index levels & changes
📈 Sector performance  
💰 FII/DII flows
📰 Breaking news impact

Try "market status" now! 🚀"""
        }
        
        response_text = help_responses.get(list_id, "Thanks for selecting that option! How can I help you further? 😊")
        
        return {
            'type': 'text',
            'content': response_text,
            'actions': []
        }