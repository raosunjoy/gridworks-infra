"""
Offline Onboarding System for Rural Financial Inclusion
Kirana store and post office partnerships for assisted sign-ups
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import qrcode
import io
import base64
from PIL import Image

from app.core.config import settings
from app.core.enterprise_architecture import PerformanceConfig, ServiceTier
from app.whatsapp.client import WhatsAppClient
from app.regulatory.sebi_account_aggregator import SEBIAccountAggregator

logger = logging.getLogger(__name__)


class PartnerType(Enum):
    KIRANA_STORE = "kirana_store"
    POST_OFFICE = "post_office"
    BANK_BRANCH = "bank_branch"
    CSC_CENTER = "csc_center"  # Common Service Center
    ASHA_WORKER = "asha_worker"
    RURAL_ENTREPRENEUR = "rural_entrepreneur"


class OnboardingStatus(Enum):
    INITIATED = "initiated"
    DOCUMENTS_COLLECTED = "documents_collected"
    VERIFICATION_PENDING = "verification_pending"
    KYC_IN_PROGRESS = "kyc_in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class VerificationMethod(Enum):
    AADHAAR_OTP = "aadhaar_otp"
    BIOMETRIC = "biometric"
    VIDEO_KYC = "video_kyc"
    DOCUMENT_UPLOAD = "document_upload"


@dataclass
class OfflinePartner:
    """Offline onboarding partner details"""
    partner_id: str
    partner_type: PartnerType
    name: str
    address: str
    pincode: str
    state: str
    district: str
    contact_person: str
    phone_number: str
    email: str
    license_number: str  # Business license or registration
    onboarding_capacity: int  # Max customers per day
    languages_supported: List[str]
    verification_methods: List[VerificationMethod]
    commission_rate: float  # Commission per successful onboarding
    is_active: bool = True
    certification_level: str = "basic"  # basic, intermediate, advanced
    success_rate: float = 0.0
    total_onboardings: int = 0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class OfflineOnboardingSession:
    """Offline onboarding session data"""
    session_id: str
    partner_id: str
    customer_phone: str
    customer_name: str
    customer_aadhaar: str  # Masked for security
    customer_pan: str  # Masked for security
    preferred_language: str
    onboarding_status: OnboardingStatus
    verification_method: VerificationMethod
    documents_collected: List[str]
    verification_data: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None
    notes: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class OfflineOnboardingSystem:
    """
    Comprehensive offline onboarding system for rural financial inclusion
    Enables GridWorks access through trusted local partners
    """
    
    def __init__(self):
        # Performance configuration
        self.performance_config = PerformanceConfig(
            max_response_time_ms=2000,  # Slower for rural internet
            max_concurrent_requests=1000,
            cache_ttl_seconds=3600,
            rate_limit_per_minute=100,
            circuit_breaker_threshold=5,
            service_tier=ServiceTier.HIGH
        )
        
        # Core components
        self.whatsapp_client = WhatsAppClient()
        self.sebi_aa = SEBIAccountAggregator()
        
        # Partner onboarding incentives
        self.commission_structure = {
            PartnerType.KIRANA_STORE: 50.0,  # ₹50 per onboarding
            PartnerType.POST_OFFICE: 75.0,   # ₹75 per onboarding
            PartnerType.BANK_BRANCH: 100.0,  # ₹100 per onboarding
            PartnerType.CSC_CENTER: 60.0,    # ₹60 per onboarding
            PartnerType.ASHA_WORKER: 40.0,   # ₹40 per onboarding
            PartnerType.RURAL_ENTREPRENEUR: 80.0  # ₹80 per onboarding
        }
        
        # Regional language support for rural areas
        self.rural_languages = {
            'hindi': ['हिंदी', 'Hindi'],
            'bengali': ['বাংলা', 'Bengali'],
            'tamil': ['தமிழ்', 'Tamil'],
            'telugu': ['తెలుగు', 'Telugu'],
            'marathi': ['मराठी', 'Marathi'],
            'gujarati': ['ગુજરાતી', 'Gujarati'],
            'kannada': ['ಕನ್ನಡ', 'Kannada'],
            'malayalam': ['മലയാളം', 'Malayalam'],
            'punjabi': ['ਪੰਜਾਬੀ', 'Punjabi'],
            'odia': ['ଓଡ଼ିଆ', 'Odia'],
            'assamese': ['অসমীয়া', 'Assamese']
        }
        
        # Verification document requirements
        self.document_requirements = {
            'mandatory': ['aadhaar', 'pan', 'photo'],
            'optional': ['bank_passbook', 'income_proof', 'address_proof'],
            'verification_methods': [
                VerificationMethod.AADHAAR_OTP,
                VerificationMethod.BIOMETRIC,
                VerificationMethod.VIDEO_KYC
            ]
        }
        
        # Training materials for partners
        self.training_modules = {
            'basic': [
                'GridWorks Platform Overview',
                'Customer Onboarding Process', 
                'Document Collection Guidelines',
                'KYC Compliance Requirements',
                'Fraud Prevention Basics'
            ],
            'intermediate': [
                'Advanced KYC Procedures',
                'Investment Product Knowledge',
                'Customer Risk Profiling',
                'Regulatory Compliance Deep Dive'
            ],
            'advanced': [
                'Financial Advisory Basics',
                'Complex Customer Scenarios',
                'Troubleshooting and Support',
                'Partner Leadership Training'
            ]
        }
    
    async def initialize(self):
        """Initialize offline onboarding system"""
        
        try:
            logger.info("🏪 Initializing Offline Onboarding System...")
            
            # Setup partner management system
            await self._setup_partner_network()
            
            # Initialize verification systems
            await self._setup_verification_systems()
            
            # Load training materials
            await self._load_training_materials()
            
            # Setup commission tracking
            await self._setup_commission_system()
            
            logger.info("✅ Offline Onboarding System initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Offline Onboarding System: {str(e)}")
            raise
    
    async def register_partner(
        self,
        partner_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register new offline onboarding partner"""
        
        try:
            logger.info(f"🏪 Registering new partner: {partner_data.get('name')}")
            
            # Validate partner data
            validation_result = await self._validate_partner_data(partner_data)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': validation_result['errors'],
                    'recommendation': 'Please provide complete and valid information'
                }
            
            # Create partner record
            partner_id = str(uuid.uuid4())
            
            partner = OfflinePartner(
                partner_id=partner_id,
                partner_type=PartnerType(partner_data['partner_type']),
                name=partner_data['name'],
                address=partner_data['address'],
                pincode=partner_data['pincode'],
                state=partner_data['state'],
                district=partner_data['district'],
                contact_person=partner_data['contact_person'],
                phone_number=partner_data['phone_number'],
                email=partner_data['email'],
                license_number=partner_data['license_number'],
                onboarding_capacity=partner_data.get('onboarding_capacity', 10),
                languages_supported=partner_data.get('languages_supported', ['hindi', 'english']),
                verification_methods=partner_data.get('verification_methods', [VerificationMethod.AADHAAR_OTP]),
                commission_rate=self.commission_structure.get(
                    PartnerType(partner_data['partner_type']), 50.0
                )
            )
            
            # Store partner in database
            await self._store_partner(partner)
            
            # Generate partner materials
            partner_materials = await self._generate_partner_materials(partner)
            
            # Send welcome materials
            await self._send_partner_welcome_kit(partner, partner_materials)
            
            return {
                'success': True,
                'partner_id': partner_id,
                'partner_type': partner.partner_type.value,
                'commission_rate': partner.commission_rate,
                'onboarding_capacity': partner.onboarding_capacity,
                'training_required': True,
                'materials': partner_materials,
                'next_steps': [
                    'Complete partner training program',
                    'Set up onboarding station',
                    'Download GridWorks Partner App',
                    'Start customer onboarding'
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error registering partner: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def initiate_offline_onboarding(
        self,
        partner_id: str,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initiate offline onboarding session"""
        
        try:
            logger.info(f"🏪 Initiating offline onboarding via partner {partner_id}")
            
            # Validate partner
            partner = await self._get_partner(partner_id)
            if not partner or not partner.is_active:
                return {
                    'success': False,
                    'error': 'Invalid or inactive partner',
                    'recommendation': 'Contact GridWorks support'
                }
            
            # Check partner capacity
            if not await self._check_partner_capacity(partner_id):
                return {
                    'success': False,
                    'error': 'Partner has reached daily onboarding capacity',
                    'recommendation': 'Try again tomorrow or visit another partner'
                }
            
            # Create onboarding session
            session_id = str(uuid.uuid4())
            
            onboarding_session = OfflineOnboardingSession(
                session_id=session_id,
                partner_id=partner_id,
                customer_phone=customer_data['phone_number'],
                customer_name=customer_data['name'],
                customer_aadhaar=self._mask_aadhaar(customer_data['aadhaar']),
                customer_pan=self._mask_pan(customer_data['pan']),
                preferred_language=customer_data.get('preferred_language', 'hindi'),
                onboarding_status=OnboardingStatus.INITIATED,
                verification_method=VerificationMethod.AADHAAR_OTP,
                documents_collected=[],
                verification_data={},
                created_at=datetime.utcnow()
            )
            
            # Store session
            await self._store_onboarding_session(onboarding_session)
            
            # Generate QR code for customer
            qr_code = await self._generate_onboarding_qr(session_id)
            
            # Send WhatsApp message to customer
            welcome_message = await self._generate_customer_welcome_message(
                onboarding_session, partner, qr_code
            )
            
            await self.whatsapp_client.send_text_message(
                phone_number=customer_data['phone_number'],
                message=welcome_message
            )
            
            return {
                'success': True,
                'session_id': session_id,
                'partner_name': partner.name,
                'estimated_time': '10-15 minutes',
                'qr_code': qr_code,
                'next_steps': [
                    'Customer scans QR code on their phone',
                    'Complete Aadhaar OTP verification',
                    'Partner assists with KYC documentation',
                    'Account activated within 24 hours'
                ],
                'customer_message_sent': True
            }
            
        except Exception as e:
            logger.error(f"❌ Error initiating offline onboarding: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def process_document_collection(
        self,
        session_id: str,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process document collection in offline onboarding"""
        
        try:
            # Get onboarding session
            session = await self._get_onboarding_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Invalid session ID'
                }
            
            # Validate documents
            validation_results = []
            for doc in documents:
                result = await self._validate_document(doc)
                validation_results.append(result)
            
            # Update session with collected documents
            session.documents_collected = [doc['type'] for doc in documents if doc.get('valid', False)]
            session.onboarding_status = OnboardingStatus.DOCUMENTS_COLLECTED
            
            await self._update_onboarding_session(session)
            
            # Check if all required documents are collected
            required_docs = set(self.document_requirements['mandatory'])
            collected_docs = set(session.documents_collected)
            
            if required_docs.issubset(collected_docs):
                # Proceed to verification
                verification_result = await self._initiate_verification(session)
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'documents_status': 'complete',
                    'verification_initiated': True,
                    'verification_method': verification_result.get('method'),
                    'next_step': 'Customer will receive OTP for verification'
                }
            else:
                missing_docs = required_docs - collected_docs
                return {
                    'success': True,
                    'session_id': session_id,
                    'documents_status': 'incomplete',
                    'missing_documents': list(missing_docs),
                    'next_step': f'Please collect: {", ".join(missing_docs)}'
                }
                
        except Exception as e:
            logger.error(f"❌ Error processing document collection: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def complete_offline_onboarding(
        self,
        session_id: str,
        verification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete offline onboarding process"""
        
        try:
            # Get session
            session = await self._get_onboarding_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': 'Invalid session ID'
                }
            
            # Verify customer
            verification_result = await self._verify_customer(session, verification_data)
            
            if verification_result['verified']:
                # Create GridWorks account
                account_result = await self._create_gridworks_account(session)
                
                if account_result['success']:
                    # Update session status
                    session.onboarding_status = OnboardingStatus.COMPLETED
                    session.completed_at = datetime.utcnow()
                    await self._update_onboarding_session(session)
                    
                    # Calculate and credit partner commission
                    await self._credit_partner_commission(session.partner_id)
                    
                    # Send success notifications
                    await self._send_onboarding_success_notifications(session, account_result)
                    
                    return {
                        'success': True,
                        'session_id': session_id,
                        'user_id': account_result['user_id'],
                        'account_status': 'active',
                        'onboarding_completed_at': session.completed_at.isoformat(),
                        'partner_commission': f"₹{self._get_partner_commission(session.partner_id)}",
                        'customer_benefits': [
                            'WhatsApp trading activated',
                            'Voice commands in regional language',
                            'AI financial advisor access',
                            'Micro-investing features enabled'
                        ]
                    }
                else:
                    session.onboarding_status = OnboardingStatus.FAILED
                    session.notes = account_result.get('error', 'Account creation failed')
                    await self._update_onboarding_session(session)
                    
                    return {
                        'success': False,
                        'error': 'Account creation failed',
                        'details': account_result.get('error')
                    }
            else:
                return {
                    'success': False,
                    'error': 'Customer verification failed',
                    'details': verification_result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ Error completing offline onboarding: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_partner_dashboard(self, partner_id: str) -> Dict[str, Any]:
        """Get partner dashboard with analytics and performance"""
        
        try:
            partner = await self._get_partner(partner_id)
            if not partner:
                return {'error': 'Partner not found'}
            
            # Get partner analytics
            analytics = await self._get_partner_analytics(partner_id)
            
            # Get recent onboardings
            recent_onboardings = await self._get_recent_onboardings(partner_id, limit=10)
            
            # Calculate earnings
            monthly_earnings = await self._calculate_monthly_earnings(partner_id)
            
            dashboard = {
                'partner_info': {
                    'name': partner.name,
                    'type': partner.partner_type.value,
                    'certification_level': partner.certification_level,
                    'success_rate': partner.success_rate,
                    'total_onboardings': partner.total_onboardings
                },
                'performance_metrics': {
                    'this_month': {
                        'onboardings': analytics['monthly_onboardings'],
                        'success_rate': analytics['monthly_success_rate'],
                        'earnings': monthly_earnings
                    },
                    'today': {
                        'onboardings': analytics['daily_onboardings'],
                        'capacity_used': f"{analytics['daily_onboardings']}/{partner.onboarding_capacity}"
                    }
                },
                'recent_activity': [
                    {
                        'customer_name': onboarding.customer_name,
                        'status': onboarding.onboarding_status.value,
                        'created_at': onboarding.created_at.isoformat(),
                        'commission': f"₹{partner.commission_rate}" if onboarding.onboarding_status == OnboardingStatus.COMPLETED else 'Pending'
                    }
                    for onboarding in recent_onboardings
                ],
                'training_status': {
                    'current_level': partner.certification_level,
                    'next_level': 'intermediate' if partner.certification_level == 'basic' else 'advanced',
                    'modules_completed': analytics.get('training_modules_completed', 0),
                    'modules_remaining': analytics.get('training_modules_remaining', 5)
                },
                'support_resources': [
                    'GridWorks Partner App Download',
                    'Training Videos Library',
                    'Customer Support Hotline: 1800-TRADEMATE',
                    'Partner WhatsApp Group'
                ]
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Error getting partner dashboard: {str(e)}")
            return {'error': str(e)}
    
    # Helper methods for implementation
    async def _validate_partner_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate partner registration data"""
        errors = []
        
        required_fields = ['name', 'address', 'pincode', 'contact_person', 'phone_number', 'license_number']
        for field in required_fields:
            if not data.get(field):
                errors.append(f'Missing required field: {field}')
        
        # Validate phone number
        if data.get('phone_number') and not data['phone_number'].startswith('+91'):
            errors.append('Phone number must start with +91')
        
        # Validate pincode
        if data.get('pincode') and len(data['pincode']) != 6:
            errors.append('Pincode must be 6 digits')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _mask_aadhaar(self, aadhaar: str) -> str:
        """Mask Aadhaar number for security"""
        if len(aadhaar) >= 12:
            return f"XXXX-XXXX-{aadhaar[-4:]}"
        return "XXXX-XXXX-XXXX"
    
    def _mask_pan(self, pan: str) -> str:
        """Mask PAN number for security"""
        if len(pan) >= 10:
            return f"XXXXX{pan[-4:]}"
        return "XXXXXXXXXX"
    
    async def _generate_onboarding_qr(self, session_id: str) -> str:
        """Generate QR code for onboarding session"""
        
        # Create QR code data
        qr_data = {
            'type': 'gridworks_onboarding',
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
            'url': f'https://gridworks.app/onboard/{session_id}'
        }
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for easy transmission
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return qr_base64
    
    # Additional helper methods would be implemented here...