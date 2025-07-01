#!/usr/bin/env python3
"""
GridWorks Risk Profiling System
===============================
Comprehensive user risk assessment for personalized financial advice
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio

from .gpt4_financial_coach import RiskProfile, LanguageCode


class QuestionType(Enum):
    """Types of risk profiling questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE_RATING = "scale_rating"
    YES_NO = "yes_no"
    NUMERIC_INPUT = "numeric_input"


class FinancialGoal(Enum):
    """Common financial goals"""
    RETIREMENT = "retirement"
    HOUSE_PURCHASE = "house_purchase"
    CHILD_EDUCATION = "child_education"
    MARRIAGE = "marriage"
    EMERGENCY_FUND = "emergency_fund"
    WEALTH_CREATION = "wealth_creation"
    DEBT_CLEARANCE = "debt_clearance"
    VACATION = "vacation"
    BUSINESS_INVESTMENT = "business_investment"


@dataclass
class RiskQuestion:
    """Risk profiling question structure"""
    question_id: str
    question_text: Dict[LanguageCode, str]  # Multilingual questions
    question_type: QuestionType
    options: Optional[List[Dict[str, Any]]]  # For multiple choice
    weight: float  # Question importance weight
    category: str  # "risk_tolerance", "investment_knowledge", "financial_situation"
    min_value: Optional[int] = None  # For scale ratings
    max_value: Optional[int] = None


@dataclass
class UserResponse:
    """User response to risk question"""
    question_id: str
    response_value: Any  # Can be string, int, float, bool
    response_text: Optional[str] = None
    timestamp: datetime = datetime.now()


@dataclass
class RiskAssessmentResult:
    """Complete risk assessment result"""
    user_id: str
    assessment_id: str
    risk_profile: RiskProfile
    risk_score: float  # 0-100 scale
    investment_experience_level: str
    recommended_asset_allocation: Dict[str, float]
    financial_goals: List[FinancialGoal]
    assessment_date: datetime
    responses: List[UserResponse]
    confidence_level: float  # How confident we are in the assessment


class RiskProfilingSystem:
    """Comprehensive risk profiling and assessment system"""
    
    def __init__(self):
        """Initialize the risk profiling system"""
        self.questions = self._initialize_questions()
        self.assessment_cache = {}
    
    def _initialize_questions(self) -> List[RiskQuestion]:
        """Initialize risk profiling questions"""
        
        questions = [
            # Risk Tolerance Questions
            RiskQuestion(
                question_id="risk_tolerance_1",
                question_text={
                    LanguageCode.ENGLISH: "If your investment loses 20% of its value in a month, what would you do?",
                    LanguageCode.HINDI: "यदि आपका निवेश एक महीने में 20% मूल्य खो देता है, तो आप क्या करेंगे?",
                    LanguageCode.TAMIL: "உங்கள் முதலீடு ஒரு மாதத்தில் 20% மதிப்பை இழந்தால், நீங்கள் என்ன செய்வீர்கள்?",
                    LanguageCode.TELUGU: "మీ పెట్టుబడి ఒక నెలలో 20% విలువను కోల్పోతే, ఆప మీరు ఏమి చేస్తారు?",
                    LanguageCode.BENGALI: "আপনার বিনিয়োগ এক মাসে 20% মূল্য হারালে, আপনি কী করবেন?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Sell immediately", "hi": "तुरंत बेच देना", "ta": "உடனே விற்று விடுவீர்கள்", "te": "వెంటనే అమ్మేస్తాను", "bn": "তৎক্ষণাৎ বিক্রি করব"}},
                    {"value": 2, "text": {"en": "Sell partially", "hi": "आंशिक रूप से बेचना", "ta": "ஒரு பகுதியை விற்பீர்கள்", "te": "కొంత భాగాన్ని అమ్ముతాను", "bn": "আংশিক বিক্রি করব"}},
                    {"value": 3, "text": {"en": "Hold and wait", "hi": "होल्ड करना और इंतजार करना", "ta": "வைத்திருந்து காத்திருப்பீர்கள்", "te": "పట్టుకుని వేచి ఉంటాను", "bn": "ধরে রেখে অপেক্ষা করব"}},
                    {"value": 4, "text": {"en": "Buy more at lower price", "hi": "कम कीमत पर और खरीदना", "ta": "குறைந்த விலையில் மேலும் வாங்குவீர்கள்", "te": "తక్కువ ధరకు మరింత కొనుగోలు చేస్తాను", "bn": "কম দামে আরও কিনব"}}
                ],
                weight=0.25,
                category="risk_tolerance"
            ),
            
            RiskQuestion(
                question_id="risk_tolerance_2",
                question_text={
                    LanguageCode.ENGLISH: "What is your primary investment objective?",
                    LanguageCode.HINDI: "आपका मुख्य निवेश उद्देश्य क्या है?",
                    LanguageCode.TAMIL: "உங்கள் முதன்மை முதலீட்டு நோக்கம் என்ன?",
                    LanguageCode.TELUGU: "మీ ప్రాథమిక పెట్టుబడి లక్ష్యం ఏమిటి?",
                    LanguageCode.BENGALI: "আপনার প্রাথমিক বিনিয়োগের উদ্দেশ্য কী?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Capital preservation", "hi": "पूंजी संरक्षण", "ta": "மூலதான பாதுகாப்பு", "te": "మూలధన రక్షణ", "bn": "পুঁজি সংরক্ষণ"}},
                    {"value": 2, "text": {"en": "Steady income", "hi": "स्थिर आय", "ta": "நிலையான வருமானம்", "te": "స్థిరమైన ఆదాయం", "bn": "স্থিতিশীল আয়"}},
                    {"value": 3, "text": {"en": "Moderate growth", "hi": "मध्यम वृद्धि", "ta": "மிதமான வளர்ச்சி", "te": "మితమైన వృద్ధి", "bn": "মাঝারি বৃদ্ধি"}},
                    {"value": 4, "text": {"en": "Aggressive growth", "hi": "आक्रामक विकास", "ta": "தீவிர வளர்ச்சி", "te": "దూకుడు వృద్ధి", "bn": "আক্রমণাত্মক বৃদ্ধি"}}
                ],
                weight=0.2,
                category="risk_tolerance"
            ),
            
            # Investment Knowledge Questions
            RiskQuestion(
                question_id="knowledge_1",
                question_text={
                    LanguageCode.ENGLISH: "How many years of investment experience do you have?",
                    LanguageCode.HINDI: "आपके पास कितने साल का निवेश अनुभव है?",
                    LanguageCode.TAMIL: "உங்களுக்கு எத்தனை ஆண்டுகள் முதலீட்டு அனுபவம் உள்ளது?",
                    LanguageCode.TELUGU: "మీకు ఎన్ని సంవత్సరాల పెట్టుబడి అనుభవం ఉంది?",
                    LanguageCode.BENGALI: "আপনার কত বছরের বিনিয়োগের অভিজ্ঞতা আছে?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Less than 1 year", "hi": "1 साल से कम", "ta": "1 ஆண்டுக்கும் குறைவு", "te": "1 సంవత్సరం కంటే తక్కువ", "bn": "1 বছরের কম"}},
                    {"value": 2, "text": {"en": "1-3 years", "hi": "1-3 साल", "ta": "1-3 ஆண்டுகள்", "te": "1-3 సంవత్సరాలు", "bn": "1-3 বছর"}},
                    {"value": 3, "text": {"en": "3-7 years", "hi": "3-7 साल", "ta": "3-7 ஆண்டுகள்", "te": "3-7 సంవత్సరాలు", "bn": "3-7 বছর"}},
                    {"value": 4, "text": {"en": "More than 7 years", "hi": "7 साल से अधिक", "ta": "7 ஆண்டுகளுக்கு மேல்", "te": "7 సంవత్సరాలకు మించి", "bn": "7 বছরের বেশি"}}
                ],
                weight=0.15,
                category="investment_knowledge"
            ),
            
            RiskQuestion(
                question_id="knowledge_2",
                question_text={
                    LanguageCode.ENGLISH: "Which investment products have you used before?",
                    LanguageCode.HINDI: "आपने पहले कौन से निवेश उत्पादों का उपयोग किया है?",
                    LanguageCode.TAMIL: "முன்பு நீங்கள் எந்த முதலீட்டு தயாரிப்புகளைப் பயன்படுத்தியுள்ளீர்கள்?",
                    LanguageCode.TELUGU: "మీరు ఇంతకు ముందు ఏ పెట్టుబడి ఉత్పత్తులను ఉపయోగించారు?",
                    LanguageCode.BENGALI: "আপনি আগে কোন বিনিয়োগ পণ্য ব্যবহার করেছেন?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Only FD/Savings", "hi": "केवल FD/बचत", "ta": "FD/சேமிப்பு மட்டும்", "te": "FD/సేవింగ్స్ మాత్రమే", "bn": "শুধু FD/সঞ্চয়"}},
                    {"value": 2, "text": {"en": "FD + PPF/ELSS", "hi": "FD + PPF/ELSS", "ta": "FD + PPF/ELSS", "te": "FD + PPF/ELSS", "bn": "FD + PPF/ELSS"}},
                    {"value": 3, "text": {"en": "Mutual Funds", "hi": "म्यूचुअल फंड", "ta": "மியூச்சுவல் ஃபண்ட்", "te": "మ్యూచువల్ ఫండ్స్", "bn": "মিউচুয়াল ফান্ড"}},
                    {"value": 4, "text": {"en": "Stocks/Derivatives", "hi": "स्टॉक/डेरिवेटिव", "ta": "பங்குகள்/வழித்தோன்றல்கள்", "te": "స్టాక్స్/డెరివేటివ్స్", "bn": "স্টক/ডেরিভেটিভ"}}
                ],
                weight=0.15,
                category="investment_knowledge"
            ),
            
            # Financial Situation Questions
            RiskQuestion(
                question_id="financial_situation_1",
                question_text={
                    LanguageCode.ENGLISH: "What percentage of your monthly income can you invest?",
                    LanguageCode.HINDI: "आप अपनी मासिक आय का कितना प्रतिशत निवेश कर सकते हैं?",
                    LanguageCode.TAMIL: "உங்கள் மாதாந்திர வருமானத்தில் எத்தனை சதவீதத்தை முதலீடு செய்ய முடியும்?",
                    LanguageCode.TELUGU: "మీ నెలవారీ ఆదాయంలో ఎంత శాతం పెట్టుబడి పెట్టగలరు?",
                    LanguageCode.BENGALI: "আপনার মাসিক আয়ের কত শতাংশ বিনিয়োগ করতে পারেন?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Less than 10%", "hi": "10% से कम", "ta": "10% க்கும் குறைவு", "te": "10% కంటే తక్కువ", "bn": "10% এর কম"}},
                    {"value": 2, "text": {"en": "10-20%", "hi": "10-20%", "ta": "10-20%", "te": "10-20%", "bn": "10-20%"}},
                    {"value": 3, "text": {"en": "20-30%", "hi": "20-30%", "ta": "20-30%", "te": "20-30%", "bn": "20-30%"}},
                    {"value": 4, "text": {"en": "More than 30%", "hi": "30% से अधिक", "ta": "30% க்கும் மேல்", "te": "30% కంటే ఎక్కువ", "bn": "30% এর বেশি"}}
                ],
                weight=0.1,
                category="financial_situation"
            ),
            
            RiskQuestion(
                question_id="time_horizon",
                question_text={
                    LanguageCode.ENGLISH: "When do you plan to use this investment?",
                    LanguageCode.HINDI: "आप इस निवेश का उपयोग कब करने की योजना बना रहे हैं?",
                    LanguageCode.TAMIL: "இந்த முதலீட்டை எப்போது பயன்படுத்த திட்டமிட்டுள்ளீர்கள்?",
                    LanguageCode.TELUGU: "ఈ పెట్టుబడిని ఎప్పుడు ఉపయోగించాలని అనుకుంటున్నారు?",
                    LanguageCode.BENGALI: "এই বিনিয়োগ কবে ব্যবহার করার পরিকল্পনা করছেন?"
                },
                question_type=QuestionType.MULTIPLE_CHOICE,
                options=[
                    {"value": 1, "text": {"en": "Within 1 year", "hi": "1 साल के भीतर", "ta": "1 ஆண்டுக்குள்", "te": "1 సంవత్సరంలో", "bn": "1 বছরের মধ্যে"}},
                    {"value": 2, "text": {"en": "1-3 years", "hi": "1-3 साल", "ta": "1-3 ஆண்டுகள்", "te": "1-3 సంవత్సరాలు", "bn": "1-3 বছর"}},
                    {"value": 3, "text": {"en": "3-7 years", "hi": "3-7 साল", "ta": "3-7 ஆண்டுகள்", "te": "3-7 సంవత్సరాలు", "bn": "3-7 বছর"}},
                    {"value": 4, "text": {"en": "More than 7 years", "hi": "7 साल से अधिक", "ta": "7 ஆண்டுகளுக்கு மேல்", "te": "7 సంవత్సరాలకు మించి", "bn": "7 বছরের বেশি"}}
                ],
                weight=0.15,
                category="time_horizon"
            )
        ]
        
        return questions
    
    async def start_risk_assessment(
        self, 
        user_id: str, 
        language: LanguageCode = LanguageCode.ENGLISH
    ) -> str:
        """Start a new risk assessment session"""
        
        assessment_id = str(uuid.uuid4())
        
        # Initialize assessment session
        self.assessment_cache[assessment_id] = {
            "user_id": user_id,
            "language": language,
            "current_question": 0,
            "responses": [],
            "started_at": datetime.now()
        }
        
        # Return first question
        first_question = self.questions[0]
        return self._format_question(first_question, language, assessment_id)
    
    def _format_question(
        self, 
        question: RiskQuestion, 
        language: LanguageCode, 
        assessment_id: str
    ) -> str:
        """Format question for WhatsApp display"""
        
        question_text = question.question_text.get(
            language, 
            question.question_text[LanguageCode.ENGLISH]
        )
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            options_text = ""
            for i, option in enumerate(question.options, 1):
                option_lang = language.value if language.value in option["text"] else "en"
                option_text = option["text"].get(option_lang, option["text"]["en"])
                options_text += f"\n{i}. {option_text}"
            
            return f"*Risk Assessment Question*\n\n{question_text}{options_text}\n\nReply with option number (1-{len(question.options)})"
        
        elif question.question_type == QuestionType.SCALE_RATING:
            return f"*Risk Assessment Question*\n\n{question_text}\n\nRate from {question.min_value} to {question.max_value}"
        
        elif question.question_type == QuestionType.YES_NO:
            return f"*Risk Assessment Question*\n\n{question_text}\n\nReply with 'Yes' or 'No'"
        
        return question_text
    
    async def process_response(
        self, 
        assessment_id: str, 
        response_value: str
    ) -> Tuple[bool, str]:
        """Process user response and return next question or results"""
        
        if assessment_id not in self.assessment_cache:
            return False, "Assessment session not found. Please start a new assessment."
        
        session = self.assessment_cache[assessment_id]
        current_q_index = session["current_question"]
        
        if current_q_index >= len(self.questions):
            return False, "Assessment already completed."
        
        current_question = self.questions[current_q_index]
        
        # Validate and process response
        try:
            processed_value = self._validate_response(current_question, response_value)
        except ValueError as e:
            return False, f"Invalid response: {e}"
        
        # Store response
        user_response = UserResponse(
            question_id=current_question.question_id,
            response_value=processed_value,
            response_text=response_value
        )
        session["responses"].append(user_response)
        session["current_question"] += 1
        
        # Check if assessment is complete
        if session["current_question"] >= len(self.questions):
            # Calculate final assessment
            assessment_result = await self._calculate_risk_assessment(session)
            return True, self._format_assessment_result(assessment_result, session["language"])
        
        # Return next question
        next_question = self.questions[session["current_question"]]
        next_q_text = self._format_question(next_question, session["language"], assessment_id)
        return True, next_q_text
    
    def _validate_response(self, question: RiskQuestion, response_value: str) -> Any:
        """Validate user response based on question type"""
        
        if question.question_type == QuestionType.MULTIPLE_CHOICE:
            try:
                choice_num = int(response_value.strip())
                if 1 <= choice_num <= len(question.options):
                    return question.options[choice_num - 1]["value"]
                else:
                    raise ValueError(f"Choice must be between 1 and {len(question.options)}")
            except ValueError:
                raise ValueError("Please enter a valid option number")
        
        elif question.question_type == QuestionType.SCALE_RATING:
            try:
                rating = int(response_value.strip())
                if question.min_value <= rating <= question.max_value:
                    return rating
                else:
                    raise ValueError(f"Rating must be between {question.min_value} and {question.max_value}")
            except ValueError:
                raise ValueError("Please enter a valid number")
        
        elif question.question_type == QuestionType.YES_NO:
            response_lower = response_value.strip().lower()
            if response_lower in ["yes", "y", "हाँ", "हां", "ஆம்", "అవును", "হ্যাঁ"]:
                return True
            elif response_lower in ["no", "n", "नहीं", "இல்லை", "కాదు", "না"]:
                return False
            else:
                raise ValueError("Please answer 'Yes' or 'No'")
        
        elif question.question_type == QuestionType.NUMERIC_INPUT:
            try:
                return float(response_value.strip())
            except ValueError:
                raise ValueError("Please enter a valid number")
        
        return response_value
    
    async def _calculate_risk_assessment(self, session: Dict) -> RiskAssessmentResult:
        """Calculate comprehensive risk assessment from responses"""
        
        responses = session["responses"]
        
        # Calculate weighted risk score
        total_score = 0
        total_weight = 0
        
        for response in responses:
            question = next(q for q in self.questions if q.question_id == response.question_id)
            score = self._get_response_score(response.response_value, question)
            total_score += score * question.weight
            total_weight += question.weight
        
        risk_score = (total_score / total_weight) * 25  # Scale to 0-100
        
        # Determine risk profile
        if risk_score < 25:
            risk_profile = RiskProfile.CONSERVATIVE
        elif risk_score < 50:
            risk_profile = RiskProfile.MODERATE
        elif risk_score < 75:
            risk_profile = RiskProfile.AGGRESSIVE
        else:
            risk_profile = RiskProfile.VERY_AGGRESSIVE
        
        # Determine investment experience
        knowledge_responses = [r for r in responses if r.question_id.startswith("knowledge")]
        avg_knowledge = sum(r.response_value for r in knowledge_responses) / len(knowledge_responses)
        
        if avg_knowledge < 2:
            experience_level = "beginner"
        elif avg_knowledge < 3:
            experience_level = "intermediate"
        else:
            experience_level = "advanced"
        
        # Generate asset allocation recommendation
        asset_allocation = self._generate_asset_allocation(risk_profile, avg_knowledge)
        
        # Extract financial goals (simplified)
        financial_goals = [FinancialGoal.WEALTH_CREATION]  # Default goal
        
        # Calculate confidence based on response consistency
        confidence_level = self._calculate_confidence(responses)
        
        return RiskAssessmentResult(
            user_id=session["user_id"],
            assessment_id=str(uuid.uuid4()),
            risk_profile=risk_profile,
            risk_score=risk_score,
            investment_experience_level=experience_level,
            recommended_asset_allocation=asset_allocation,
            financial_goals=financial_goals,
            assessment_date=datetime.now(),
            responses=responses,
            confidence_level=confidence_level
        )
    
    def _get_response_score(self, response_value: Any, question: RiskQuestion) -> float:
        """Get numerical score for response (0-4 scale)"""
        
        if isinstance(response_value, (int, float)):
            return float(response_value)
        elif isinstance(response_value, bool):
            return 4.0 if response_value else 1.0
        else:
            return 2.0  # Default score
    
    def _generate_asset_allocation(
        self, 
        risk_profile: RiskProfile, 
        knowledge_score: float
    ) -> Dict[str, float]:
        """Generate recommended asset allocation"""
        
        allocations = {
            RiskProfile.CONSERVATIVE: {
                "debt": 0.70,
                "equity": 0.25,
                "gold": 0.05
            },
            RiskProfile.MODERATE: {
                "debt": 0.50,
                "equity": 0.45,
                "gold": 0.05
            },
            RiskProfile.AGGRESSIVE: {
                "debt": 0.30,
                "equity": 0.65,
                "gold": 0.05
            },
            RiskProfile.VERY_AGGRESSIVE: {
                "debt": 0.15,
                "equity": 0.80,
                "gold": 0.05
            }
        }
        
        base_allocation = allocations[risk_profile]
        
        # Adjust based on knowledge level
        if knowledge_score < 2:  # Beginner
            base_allocation["debt"] += 0.1
            base_allocation["equity"] -= 0.1
        
        return base_allocation
    
    def _calculate_confidence(self, responses: List[UserResponse]) -> float:
        """Calculate confidence level in assessment"""
        
        # Simple confidence calculation based on response consistency
        base_confidence = 0.8
        
        # Reduce confidence if responses are inconsistent
        risk_responses = [r.response_value for r in responses if "risk_tolerance" in r.question_id]
        if len(risk_responses) >= 2:
            variance = max(risk_responses) - min(risk_responses)
            if variance > 2:
                base_confidence -= 0.1
        
        return min(base_confidence, 0.95)
    
    def _format_assessment_result(
        self, 
        result: RiskAssessmentResult, 
        language: LanguageCode
    ) -> str:
        """Format assessment results for WhatsApp"""
        
        result_templates = {
            LanguageCode.ENGLISH: f"""*🎯 Your Risk Profile Assessment*

*Risk Profile:* {result.risk_profile.value.title()}
*Risk Score:* {result.risk_score:.0f}/100
*Experience Level:* {result.investment_experience_level.title()}

*💼 Recommended Asset Allocation:*
• Debt/Fixed Income: {result.recommended_asset_allocation['debt']*100:.0f}%
• Equity/Stocks: {result.recommended_asset_allocation['equity']*100:.0f}%
• Gold: {result.recommended_asset_allocation['gold']*100:.0f}%

*📊 Assessment Confidence:* {result.confidence_level*100:.0f}%

*⚠️ Disclaimer:* This is a general assessment for educational purposes. Please consult a certified financial advisor for personalized investment advice.""",

            LanguageCode.HINDI: f"""*🎯 आपका जोखिम प्रोफाइल मूल्यांकन*

*जोखिम प्रोफाइल:* {result.risk_profile.value.title()}
*जोखिम स्कोर:* {result.risk_score:.0f}/100
*अनुभव स्तर:* {result.investment_experience_level.title()}

*💼 सुझावित परिसंपत्ति आवंटन:*
• ऋण/फिक्स्ड इनकम: {result.recommended_asset_allocation['debt']*100:.0f}%
• इक्विटी/स्टॉक्स: {result.recommended_asset_allocation['equity']*100:.0f}%
• सोना: {result.recommended_asset_allocation['gold']*100:.0f}%

*📊 मूल्यांकन विश्वास:* {result.confidence_level*100:.0f}%

*⚠️ अस्वीकरण:* यह शैक्षणिक उद्देश्यों के लिए एक सामान्य मूल्यांकन है। व्यक्तिगत निवेश सलाह के लिए एक प्रमाणित वित्तीय सलाहकार से सलाह लें।"""
        }
        
        return result_templates.get(
            language, 
            result_templates[LanguageCode.ENGLISH]
        )
    
    async def get_assessment_summary(self, assessment_id: str) -> Optional[RiskAssessmentResult]:
        """Get saved assessment result"""
        
        # In real implementation, this would fetch from database
        return self.assessment_cache.get(assessment_id)


# Example usage
async def main():
    """Example usage of Risk Profiling System"""
    
    risk_system = RiskProfilingSystem()
    
    # Start assessment
    assessment_id = await risk_system.start_risk_assessment("user123", LanguageCode.HINDI)
    print(f"First question: {assessment_id}")
    
    # Simulate responses
    responses = ["3", "2", "2", "3", "2", "3"]  # Sample responses
    
    for response in responses:
        success, message = await risk_system.process_response("assessment_123", response)
        print(f"Response: {response}")
        print(f"Next: {message}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())