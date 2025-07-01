#!/usr/bin/env python3
"""
GridWorks GPT-4 Financial Coach
===============================
AI-powered financial advisory system with SEBI compliance
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import openai
from openai import AsyncOpenAI
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskProfile(Enum):
    """User risk tolerance levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    VERY_AGGRESSIVE = "very_aggressive"


class LanguageCode(Enum):
    """Supported languages for financial advice"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class AdviceCategory(Enum):
    """Categories of financial advice"""
    INVESTMENT_PLANNING = "investment_planning"
    RETIREMENT_PLANNING = "retirement_planning"
    TAX_PLANNING = "tax_planning"
    INSURANCE_PLANNING = "insurance_planning"
    DEBT_MANAGEMENT = "debt_management"
    EMERGENCY_FUND = "emergency_fund"
    GOAL_PLANNING = "goal_planning"
    MARKET_EDUCATION = "market_education"


@dataclass
class UserProfile:
    """User financial profile for personalized advice"""
    user_id: str
    age: int
    annual_income: float
    monthly_expenses: float
    current_investments: float
    debt_amount: float
    dependents: int
    risk_profile: RiskProfile
    investment_experience: str  # "beginner", "intermediate", "advanced"
    preferred_language: LanguageCode
    financial_goals: List[str]
    time_horizon: int  # years
    created_at: datetime
    updated_at: datetime


@dataclass
class AdviceRequest:
    """Financial advice request structure"""
    request_id: str
    user_id: str
    category: AdviceCategory
    query: str
    language: LanguageCode
    context: Dict[str, Any]
    timestamp: datetime


@dataclass
class AdviceResponse:
    """Financial advice response structure"""
    response_id: str
    request_id: str
    user_id: str
    advice_text: str
    disclaimer: str
    confidence_score: float
    category: AdviceCategory
    language: LanguageCode
    generated_at: datetime
    reviewed_by_human: bool = False
    sebi_compliant: bool = True


class SEBIComplianceValidator:
    """SEBI compliance validation for financial advice"""
    
    FORBIDDEN_PHRASES = [
        "guaranteed returns",
        "risk-free investment",
        "sure profit",
        "100% safe",
        "guaranteed profit",
        "no risk",
        "certain returns"
    ]
    
    REQUIRED_DISCLAIMERS = [
        "mutual fund investments are subject to market risks",
        "past performance does not guarantee future results",
        "please read the offer document carefully",
        "consult your financial advisor"
    ]
    
    FORBIDDEN_SPECIFIC_STOCKS = True
    FORBIDDEN_MARKET_TIMING = True
    
    @classmethod
    def validate_advice(cls, advice_text: str, category: AdviceCategory) -> Tuple[bool, List[str]]:
        """Validate advice for SEBI compliance"""
        issues = []
        
        # Check for forbidden phrases
        advice_lower = advice_text.lower()
        for phrase in cls.FORBIDDEN_PHRASES:
            if phrase in advice_lower:
                issues.append(f"Contains forbidden phrase: '{phrase}'")
        
        # Check for specific stock recommendations
        if cls.FORBIDDEN_SPECIFIC_STOCKS:
            stock_indicators = ["buy", "sell", "invest in", "purchase"]
            company_patterns = ["reliance", "tcs", "hdfc", "icici", "sbi"]
            
            for indicator in stock_indicators:
                for company in company_patterns:
                    if f"{indicator} {company}" in advice_lower:
                        issues.append(f"Contains specific stock recommendation")
                        break
        
        # Check for market timing advice
        if cls.FORBIDDEN_MARKET_TIMING:
            timing_phrases = ["market will go up", "market will crash", "buy now", "sell now"]
            for phrase in timing_phrases:
                if phrase in advice_lower:
                    issues.append(f"Contains market timing advice: '{phrase}'")
        
        return len(issues) == 0, issues


class MultilingualTemplates:
    """Multilingual response templates and translations"""
    
    DISCLAIMERS = {
        LanguageCode.ENGLISH: "This is general financial education. Mutual fund investments are subject to market risks. Please read the offer document carefully before investing. Consult your financial advisor for personalized advice.",
        
        LanguageCode.HINDI: "यह सामान्य वित्तीय शिक्षा है। म्यूचुअल फंड निवेश बाजार जोखिमों के अधीन हैं। निवेश से पहले प्रस्ताव दस्तावेज को ध्यान से पढ़ें। व्यक्तिगत सलाह के लिए अपने वित्तीय सलाहकार से परामर्श करें।",
        
        LanguageCode.TAMIL: "இது பொதுவான நிதி கல்வி. மியூச்சுவல் ஃபண்ட் முதலீடுகள் சந்தை அபாயங்களுக்கு உட்பட்டவை. முதலீடு செய்வதற்கு முன் சலுகை ஆவணத்தை கவனமாக படிக்கவும். தனிப்பட்ட ஆலோசனைக்கு உங்கள் நிதி ஆலோசகரை அணுகவும்.",
        
        LanguageCode.TELUGU: "ఇది సాధారణ ఆర్థిక విద్య. మ్యూచువల్ ఫండ్ పెట్టుబడులు మార్కెట్ రిస్క్‌లకు లోబడి ఉంటాయి. పెట్టుబడి చేయడానికి ముందు ఆఫర్ డాక్యుమెంట్‌ను జాగ్రత్తగా చదవండి. వ్యక్తిగత సలహా కోసం మీ ఆర్థిక సలహాదారుని సంప్రదించండి.",
        
        LanguageCode.BENGALI: "এটি সাধারণ আর্থিক শিক্ষা। মিউচুয়াল ফান্ড বিনিয়োগ বাজারের ঝুঁকির সাপেক্ষে। বিনিয়োগের আগে অফার ডকুমেন্ট সাবধানে পড়ুন। ব্যক্তিগত পরামর্শের জন্য আপনার আর্থিক পরামর্শদাতার সাথে পরামর্শ করুন।",
        
        LanguageCode.MARATHI: "हे सामान्य आर्थिक शिक्षण आहे. म्युच्युअल फंड गुंतवणूक बाजारातील जोखमींच्या अधीन आहेत. गुंतवणूक करण्यापूर्वी ऑफर डॉक्युमेंट काळजीपूर्वक वाचा. वैयक्तिक सल्ल्यासाठी तुमच्या आर्थिक सल्लागाराशी सल्लामसलत करा.",
        
        LanguageCode.GUJARATI: "આ સામાન્ય નાણાકીય શિક્ષણ છે. મ્યુચ્યુઅલ ફંડ રોકાણ બજારના જોખમોને આધીન છે. રોકાણ કરતા પહેલા ઓફર ડોક્યુમેન્ટ કાળજીપૂર્વક વાંચો. વ્યક્તિગત સલાહ માટે તમારા નાણાકીય સલાહકારની સલાહ લો.",
        
        LanguageCode.KANNADA: "ಇದು ಸಾಮಾನ್ಯ ಹಣಕಾಸು ಶಿಕ್ಷಣ. ಮ್ಯೂಚುಯಲ್ ಫಂಡ್ ಹೂಡಿಕೆಗಳು ಮಾರುಕಟ್ಟೆ ಅಪಾಯಗಳಿಗೆ ಒಳಪಟ್ಟಿರುತ್ತವೆ. ಹೂಡಿಕೆ ಮಾಡುವ ಮೊದಲು ಆಫರ್ ಡಾಕ್ಯುಮೆಂಟ್ ಅನ್ನು ಎಚ್ಚರಿಕೆಯಿಂದ ಓದಿ. ವೈಯಕ್ತಿಕ ಸಲಹೆಗಾಗಿ ನಿಮ್ಮ ಹಣಕಾಸು ಸಲಹೆಗಾರರನ್ನು ಸಂಪರ್ಕಿಸಿ."
    }
    
    GREETING_TEMPLATES = {
        LanguageCode.ENGLISH: "Hello! I'm your AI financial coach. How can I help you plan your financial future today?",
        LanguageCode.HINDI: "नमस्ते! मैं आपका AI वित्तीय कोच हूँ। आज मैं आपके वित्तीय भविष्य की योजना बनाने में कैसे मदद कर सकता हूँ?",
        LanguageCode.TAMIL: "வணக்கம்! நான் உங்கள் AI நிதி பயிற்சியாளர். இன்று உங்கள் நிதி எதிர்காலத்தைத் திட்டமிட நான் எப்படி உதவ முடியும்?",
        LanguageCode.TELUGU: "నమస్కారం! నేను మీ AI ఆర్థిక కోచ్. ఈరోజు మీ ఆర్థిక భవిష్యత్తును ప్లాన్ చేయడంలో నేను ఎలా సహాయం చేయగలను?",
        LanguageCode.BENGALI: "নমস্কার! আমি আপনার AI আর্থিক কোচ। আজ আপনার আর্থিক ভবিষ্যৎ পরিকল্পনা করতে আমি কীভাবে সাহায্য করতে পারি?"
    }


class GPT4FinancialCoach:
    """GPT-4 powered financial coaching system"""
    
    def __init__(self, openai_api_key: str):
        """Initialize the financial coach"""
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-4"
        self.compliance_validator = SEBIComplianceValidator()
        self.templates = MultilingualTemplates()
        
        # Response cache for similar queries
        self.response_cache = {}
        
        # Audit trail storage
        self.audit_trail = []
    
    async def get_financial_advice(
        self, 
        request: AdviceRequest, 
        user_profile: UserProfile
    ) -> AdviceResponse:
        """Generate personalized financial advice"""
        
        try:
            # Build context-aware prompt
            prompt = self._build_advice_prompt(request, user_profile)
            
            # Generate advice using GPT-4
            advice_text = await self._generate_advice(prompt, request.language)
            
            # Validate SEBI compliance
            is_compliant, compliance_issues = self.compliance_validator.validate_advice(
                advice_text, request.category
            )
            
            if not is_compliant:
                # Regenerate with stricter compliance
                prompt = self._build_compliance_prompt(prompt, compliance_issues)
                advice_text = await self._generate_advice(prompt, request.language)
                
                # Re-validate
                is_compliant, _ = self.compliance_validator.validate_advice(
                    advice_text, request.category
                )
            
            # Add appropriate disclaimer
            disclaimer = self.templates.DISCLAIMERS.get(
                request.language, 
                self.templates.DISCLAIMERS[LanguageCode.ENGLISH]
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                request, user_profile, advice_text
            )
            
            # Create response
            response = AdviceResponse(
                response_id=str(uuid.uuid4()),
                request_id=request.request_id,
                user_id=request.user_id,
                advice_text=advice_text,
                disclaimer=disclaimer,
                confidence_score=confidence_score,
                category=request.category,
                language=request.language,
                generated_at=datetime.now(),
                sebi_compliant=is_compliant
            )
            
            # Log for audit trail
            self._log_advice_interaction(request, response, user_profile)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating advice: {e}")
            raise
    
    def _build_advice_prompt(self, request: AdviceRequest, user_profile: UserProfile) -> str:
        """Build context-aware prompt for GPT-4"""
        
        # Base system prompt
        system_prompt = f"""You are a SEBI-certified financial advisor providing educational guidance in {request.language.value}. 

CRITICAL RULES:
1. NEVER recommend specific stocks or securities
2. NEVER guarantee returns or claim investments are risk-free
3. ALWAYS emphasize market risks and the need for professional consultation
4. Focus on general financial principles and asset allocation concepts
5. Provide educational content, not specific investment advice
6. Use simple language appropriate for the user's experience level

User Profile:
- Age: {user_profile.age}
- Annual Income: ₹{user_profile.annual_income:,.0f}
- Monthly Expenses: ₹{user_profile.monthly_expenses:,.0f}
- Current Investments: ₹{user_profile.current_investments:,.0f}
- Risk Profile: {user_profile.risk_profile.value}
- Experience Level: {user_profile.investment_experience}
- Dependents: {user_profile.dependents}
- Time Horizon: {user_profile.time_horizon} years

Respond in {request.language.value} language with practical, educational guidance."""

        # Category-specific guidance
        category_guidance = {
            AdviceCategory.INVESTMENT_PLANNING: "Focus on asset allocation principles, diversification, and long-term wealth building strategies appropriate for the user's risk profile.",
            
            AdviceCategory.RETIREMENT_PLANNING: "Discuss retirement corpus calculation, EPF/PPF benefits, and systematic investment approaches for retirement goals.",
            
            AdviceCategory.TAX_PLANNING: "Explain tax-saving investment options under Section 80C, ELSS funds, and tax-efficient investment strategies.",
            
            AdviceCategory.EMERGENCY_FUND: "Guide on emergency fund calculation (3-6 months expenses) and suitable parking options like liquid funds.",
            
            AdviceCategory.DEBT_MANAGEMENT: "Provide guidance on debt-to-income ratios, debt consolidation strategies, and prioritizing high-interest debt repayment."
        }
        
        category_prompt = category_guidance.get(
            request.category, 
            "Provide general financial education relevant to the query."
        )
        
        # Final prompt
        final_prompt = f"""{system_prompt}

Category Focus: {category_prompt}

User Query: {request.query}

Provide helpful, educational guidance in {request.language.value} that helps the user understand financial concepts without giving specific investment recommendations."""
        
        return final_prompt
    
    async def _generate_advice(self, prompt: str, language: LanguageCode) -> str:
        """Generate advice using GPT-4"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a SEBI-compliant financial educator. Provide general financial education, never specific investment advice."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            advice_text = response.choices[0].message.content.strip()
            return advice_text
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # Fallback to template response
            return self._get_fallback_response(language)
    
    def _build_compliance_prompt(self, original_prompt: str, issues: List[str]) -> str:
        """Build stricter compliance prompt to fix issues"""
        
        compliance_fixes = f"""
CRITICAL: The previous response had compliance issues:
{chr(10).join(f'- {issue}' for issue in issues)}

STRICT REQUIREMENTS:
1. Do NOT recommend any specific stocks or securities
2. Do NOT use words like 'guaranteed', 'risk-free', 'sure profit'
3. Do NOT provide market timing advice
4. ALWAYS mention market risks
5. Focus ONLY on general financial education principles

{original_prompt}

Generate a compliant educational response that avoids all the issues mentioned above."""
        
        return compliance_fixes
    
    def _calculate_confidence_score(
        self, 
        request: AdviceRequest, 
        user_profile: UserProfile, 
        advice_text: str
    ) -> float:
        """Calculate confidence score for the advice"""
        
        score = 0.8  # Base score
        
        # Adjust based on user profile completeness
        if user_profile.annual_income > 0:
            score += 0.05
        if user_profile.current_investments > 0:
            score += 0.05
        if user_profile.financial_goals:
            score += 0.05
        
        # Adjust based on advice length and structure
        if len(advice_text) > 200:
            score += 0.03
        if "market risks" in advice_text.lower():
            score += 0.02
        
        # Cap at 0.95 to indicate AI limitations
        return min(score, 0.95)
    
    def _get_fallback_response(self, language: LanguageCode) -> str:
        """Get fallback response when API fails"""
        
        fallback_responses = {
            LanguageCode.ENGLISH: "I'm currently experiencing technical difficulties. For financial guidance, please consider consulting with a certified financial advisor who can provide personalized advice based on your specific situation.",
            
            LanguageCode.HINDI: "मुझे तकनीकी समस्या हो रही है। वित्तीय मार्गदर्शन के लिए, कृपया एक प्रमाणित वित्तीय सलाहकार से सलाह लें जो आपकी विशिष्ट स्थिति के आधार पर व्यक्तिगत सलाह दे सकें।"
        }
        
        return fallback_responses.get(
            language, 
            fallback_responses[LanguageCode.ENGLISH]
        )
    
    def _log_advice_interaction(
        self, 
        request: AdviceRequest, 
        response: AdviceResponse, 
        user_profile: UserProfile
    ):
        """Log interaction for audit trail"""
        
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": request.user_id,
            "request_id": request.request_id,
            "response_id": response.response_id,
            "category": request.category.value,
            "language": request.language.value,
            "confidence_score": response.confidence_score,
            "sebi_compliant": response.sebi_compliant,
            "user_age": user_profile.age,
            "user_risk_profile": user_profile.risk_profile.value
        }
        
        self.audit_trail.append(audit_entry)
        
        # Keep only last 1000 entries in memory
        if len(self.audit_trail) > 1000:
            self.audit_trail = self.audit_trail[-1000:]
    
    async def get_greeting_message(self, language: LanguageCode) -> str:
        """Get personalized greeting message"""
        
        return self.templates.GREETING_TEMPLATES.get(
            language,
            self.templates.GREETING_TEMPLATES[LanguageCode.ENGLISH]
        )
    
    async def analyze_user_query(self, query: str) -> AdviceCategory:
        """Analyze user query to determine advice category"""
        
        query_lower = query.lower()
        
        # Simple keyword-based categorization
        if any(word in query_lower for word in ["retirement", "pension", "60", "retire"]):
            return AdviceCategory.RETIREMENT_PLANNING
        elif any(word in query_lower for word in ["tax", "80c", "save tax", "deduction"]):
            return AdviceCategory.TAX_PLANNING
        elif any(word in query_lower for word in ["emergency", "emergency fund", "urgent money"]):
            return AdviceCategory.EMERGENCY_FUND
        elif any(word in query_lower for word in ["debt", "loan", "emi", "credit card"]):
            return AdviceCategory.DEBT_MANAGEMENT
        elif any(word in query_lower for word in ["insurance", "health", "life insurance"]):
            return AdviceCategory.INSURANCE_PLANNING
        elif any(word in query_lower for word in ["goal", "house", "car", "education", "marriage"]):
            return AdviceCategory.GOAL_PLANNING
        elif any(word in query_lower for word in ["invest", "mutual fund", "sip", "portfolio"]):
            return AdviceCategory.INVESTMENT_PLANNING
        else:
            return AdviceCategory.MARKET_EDUCATION


# Example usage and testing
async def main():
    """Example usage of GPT-4 Financial Coach"""
    
    # Initialize with OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    coach = GPT4FinancialCoach(api_key)
    
    # Create sample user profile
    user_profile = UserProfile(
        user_id="user123",
        age=30,
        annual_income=800000,
        monthly_expenses=40000,
        current_investments=200000,
        debt_amount=100000,
        dependents=1,
        risk_profile=RiskProfile.MODERATE,
        investment_experience="beginner",
        preferred_language=LanguageCode.HINDI,
        financial_goals=["retirement", "house purchase"],
        time_horizon=20,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Create advice request
    request = AdviceRequest(
        request_id=str(uuid.uuid4()),
        user_id="user123",
        category=AdviceCategory.INVESTMENT_PLANNING,
        query="मुझे 30 साल की उम्र में निवेश कैसे शुरू करना चाहिए?",
        language=LanguageCode.HINDI,
        context={},
        timestamp=datetime.now()
    )
    
    # Get advice
    try:
        response = await coach.get_financial_advice(request, user_profile)
        print(f"Advice: {response.advice_text}")
        print(f"Disclaimer: {response.disclaimer}")
        print(f"Confidence: {response.confidence_score}")
        print(f"SEBI Compliant: {response.sebi_compliant}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())