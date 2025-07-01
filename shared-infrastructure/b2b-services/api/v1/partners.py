"""
GridWorks Infra - Partners Portal API
Enterprise client management and service provisioning endpoints
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field, UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from ...auth.enterprise_auth import (
    get_current_user, get_api_key_data, PermissionChecker,
    TokenData, APIKeyData, auth_handler
)
from ...database.models import (
    EnterpriseClient, User, APIKey, B2BService,
    ClientSubscription, UsageRecord, Invoice
)
from ...database.session import get_db
from ...utils.validators import validate_company_registration
from ...utils.notifications import send_notification
from ...config import settings


router = APIRouter(prefix="/api/v1/partners", tags=["partners"])


# Request/Response Models
class ClientRegistrationRequest(BaseModel):
    """Enterprise client registration"""
    company_name: str = Field(..., min_length=3, max_length=255)
    legal_entity_name: str = Field(..., min_length=3, max_length=255)
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    
    primary_contact_name: str = Field(..., min_length=2, max_length=255)
    primary_contact_email: EmailStr
    primary_contact_phone: Optional[str] = None
    
    address_line1: str
    city: str
    state: str
    country: str = "India"
    postal_code: str
    
    requested_tier: str = Field(default="growth")
    requested_services: List[str] = []
    expected_monthly_volume: Optional[int] = None


class ClientResponse(BaseModel):
    """Client information response"""
    id: UUID4
    company_name: str
    tier: str
    is_active: bool
    is_verified: bool
    onboarding_date: datetime
    api_rate_limit: int
    services: List[Dict[str, Any]]
    subscription: Optional[Dict[str, Any]]


class ServiceActivationRequest(BaseModel):
    """Service activation request"""
    service_id: UUID4
    configuration: Dict[str, Any] = {}
    accept_terms: bool = Field(..., description="Must accept service terms")


class APIKeyCreateRequest(BaseModel):
    """API key creation request"""
    name: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    permissions: List[str] = []
    rate_limit: int = Field(default=1000, ge=100, le=100000)
    expires_in_days: Optional[int] = Field(None, ge=1, le=365)
    allowed_ips: List[str] = []


class UsageReportRequest(BaseModel):
    """Usage report parameters"""
    start_date: datetime
    end_date: datetime
    service_type: Optional[str] = None
    group_by: str = Field(default="day", pattern="^(hour|day|week|month)$")


# Client Registration & Management
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_client(
    request: ClientRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new enterprise client
    Public endpoint for initial registration
    """
    
    # Check if company already exists
    existing = await db.execute(
        select(EnterpriseClient).where(
            or_(
                EnterpriseClient.company_name == request.company_name,
                EnterpriseClient.primary_contact_email == request.primary_contact_email
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Company or email already registered"
        )
    
    # Validate registration if provided
    if request.registration_number:
        is_valid = await validate_company_registration(
            request.registration_number,
            request.country
        )
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid company registration number"
            )
    
    # Create client
    client = EnterpriseClient(
        company_name=request.company_name,
        legal_entity_name=request.legal_entity_name,
        registration_number=request.registration_number,
        tax_id=request.tax_id,
        primary_contact_name=request.primary_contact_name,
        primary_contact_email=request.primary_contact_email,
        primary_contact_phone=request.primary_contact_phone,
        billing_email=request.primary_contact_email,
        technical_email=request.primary_contact_email,
        address_line1=request.address_line1,
        city=request.city,
        state=request.state,
        country=request.country,
        postal_code=request.postal_code,
        tier=request.requested_tier,
        metadata={
            "requested_services": request.requested_services,
            "expected_monthly_volume": request.expected_monthly_volume,
            "registration_source": "api"
        }
    )
    
    db.add(client)
    
    # Create initial admin user
    admin_user = User(
        client_id=client.id,
        email=request.primary_contact_email,
        full_name=request.primary_contact_name,
        phone_number=request.primary_contact_phone,
        is_admin=True,
        is_active=True
    )
    
    db.add(admin_user)
    
    # Create trial subscription
    trial_end = datetime.utcnow() + timedelta(days=30)
    subscription = ClientSubscription(
        client_id=client.id,
        tier=request.requested_tier,
        billing_cycle="monthly",
        base_amount=0,
        final_amount=0,
        start_date=datetime.utcnow(),
        end_date=trial_end,
        trial_end_date=trial_end,
        status="trial",
        service_limits={
            "api_requests_per_minute": 1000,
            "users": 5,
            "api_keys": 3
        }
    )
    
    db.add(subscription)
    await db.commit()
    
    # Send welcome notification
    await send_notification(
        "email",
        request.primary_contact_email,
        "Welcome to GridWorks Infrastructure",
        {
            "template": "client_welcome",
            "company_name": request.company_name,
            "trial_days": 30
        }
    )
    
    return {
        "client_id": str(client.id),
        "company_name": client.company_name,
        "status": "pending_verification",
        "trial_end_date": trial_end,
        "next_steps": [
            "Verify your email address",
            "Complete KYC documentation",
            "Schedule onboarding call",
            "Explore API documentation"
        ]
    }


@router.get("/profile", response_model=ClientResponse)
async def get_client_profile(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current client profile and subscription details"""
    
    # Get client with relationships
    result = await db.execute(
        select(EnterpriseClient)
        .where(EnterpriseClient.id == current_user.client_id)
        .options(
            selectinload(EnterpriseClient.services),
            selectinload(EnterpriseClient.subscriptions)
        )
    )
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Get active subscription
    active_subscription = None
    for sub in client.subscriptions:
        if sub.status == "active" and sub.end_date > datetime.utcnow():
            active_subscription = {
                "tier": sub.tier,
                "billing_cycle": sub.billing_cycle,
                "start_date": sub.start_date,
                "end_date": sub.end_date,
                "auto_renew": sub.auto_renew,
                "status": sub.status
            }
            break
    
    # Format services
    services = [
        {
            "id": str(service.id),
            "name": service.name,
            "display_name": service.display_name,
            "is_active": service.is_active
        }
        for service in client.services
    ]
    
    return ClientResponse(
        id=client.id,
        company_name=client.company_name,
        tier=client.tier,
        is_active=client.is_active,
        is_verified=client.is_verified,
        onboarding_date=client.onboarding_date,
        api_rate_limit=client.api_rate_limit,
        services=services,
        subscription=active_subscription
    )


# Service Management
@router.get("/services/available")
async def list_available_services(
    tier: Optional[str] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List available B2B services for client's tier"""
    
    # Build query
    query = select(B2BService).where(
        and_(
            B2BService.is_active == True,
            B2BService.is_beta == False
        )
    )
    
    result = await db.execute(query)
    services = result.scalars().all()
    
    # Filter by tier pricing availability
    available_services = []
    for service in services:
        if tier and tier in service.pricing:
            price_info = service.pricing[tier]
        else:
            price_info = service.pricing.get(current_user.tier, {})
        
        if price_info:
            available_services.append({
                "id": str(service.id),
                "service_type": service.service_type,
                "name": service.name,
                "display_name": service.display_name,
                "description": service.description,
                "features": service.features,
                "pricing": price_info,
                "documentation_url": service.documentation_url
            })
    
    return {
        "services": available_services,
        "count": len(available_services)
    }


@router.post("/services/activate")
async def activate_service(
    request: ServiceActivationRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["services.activate"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Activate a B2B service for the client"""
    
    if not request.accept_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must accept service terms and conditions"
        )
    
    # Get service
    result = await db.execute(
        select(B2BService).where(B2BService.id == request.service_id)
    )
    service = result.scalar_one_or_none()
    
    if not service or not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found or not available"
        )
    
    # Check if already activated
    result = await db.execute(
        select(client_services).where(
            and_(
                client_services.c.client_id == current_user.client_id,
                client_services.c.service_id == request.service_id
            )
        )
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service already activated"
        )
    
    # Activate service
    await db.execute(
        client_services.insert().values(
            client_id=current_user.client_id,
            service_id=request.service_id,
            enabled_at=datetime.utcnow(),
            configuration=request.configuration
        )
    )
    
    await db.commit()
    
    # Send activation confirmation
    await send_notification(
        "email",
        current_user.email,
        f"{service.display_name} Activated",
        {
            "template": "service_activated",
            "service_name": service.display_name,
            "documentation_url": service.documentation_url
        }
    )
    
    return {
        "status": "activated",
        "service_id": str(service.id),
        "service_name": service.display_name,
        "configuration": request.configuration,
        "api_endpoints": service.api_endpoints,
        "documentation_url": service.documentation_url
    }


# API Key Management
@router.post("/api-keys")
async def create_api_key(
    request: APIKeyCreateRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["api_keys.create"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Create new API key for client"""
    
    # Check API key limit
    key_count = await db.execute(
        select(func.count(APIKey.id))
        .where(
            and_(
                APIKey.client_id == current_user.client_id,
                APIKey.is_active == True
            )
        )
    )
    current_count = key_count.scalar()
    
    # Get client to check limits
    client_result = await db.execute(
        select(EnterpriseClient).where(
            EnterpriseClient.id == current_user.client_id
        )
    )
    client = client_result.scalar_one()
    
    if current_count >= client.max_api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key limit reached ({client.max_api_keys})"
        )
    
    # Create API key
    key_data = await auth_handler.create_api_key(
        client_id=str(current_user.client_id),
        name=request.name,
        permissions=request.permissions or current_user.permissions,
        rate_limit=min(request.rate_limit, client.api_rate_limit),
        expires_in_days=request.expires_in_days,
        db=db
    )
    
    return key_data


@router.get("/api-keys")
async def list_api_keys(
    is_active: Optional[bool] = Query(None),
    current_user: TokenData = Depends(
        PermissionChecker(["api_keys.read"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """List client's API keys"""
    
    query = select(APIKey).where(
        APIKey.client_id == current_user.client_id
    )
    
    if is_active is not None:
        query = query.where(APIKey.is_active == is_active)
    
    result = await db.execute(query.order_by(APIKey.created_at.desc()))
    keys = result.scalars().all()
    
    return {
        "api_keys": [
            {
                "id": str(key.id),
                "name": key.name,
                "key_prefix": key.key_prefix,
                "permissions": key.permissions,
                "rate_limit": key.rate_limit,
                "is_active": key.is_active,
                "created_at": key.created_at,
                "expires_at": key.expires_at,
                "last_used_at": key.last_used_at,
                "request_count": key.request_count
            }
            for key in keys
        ],
        "count": len(keys)
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: UUID4,
    current_user: TokenData = Depends(
        PermissionChecker(["api_keys.delete"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Revoke an API key"""
    
    result = await db.execute(
        select(APIKey).where(
            and_(
                APIKey.id == key_id,
                APIKey.client_id == current_user.client_id
            )
        )
    )
    key = result.scalar_one_or_none()
    
    if not key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    key.is_active = False
    await db.commit()
    
    # Clear from cache
    # TODO: Implement cache invalidation
    
    return {"status": "revoked", "key_id": str(key_id)}


# Usage & Analytics
@router.post("/usage/report")
async def get_usage_report(
    request: UsageReportRequest,
    current_user: TokenData = Depends(
        PermissionChecker(["usage.read"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """Generate usage report for specified period"""
    
    # Validate date range
    if request.end_date <= request.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    if (request.end_date - request.start_date).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days"
        )
    
    # Build query
    query = select(UsageRecord).where(
        and_(
            UsageRecord.client_id == current_user.client_id,
            UsageRecord.timestamp >= request.start_date,
            UsageRecord.timestamp < request.end_date
        )
    )
    
    if request.service_type:
        query = query.where(UsageRecord.service_type == request.service_type)
    
    result = await db.execute(query)
    records = result.scalars().all()
    
    # Aggregate data based on grouping
    aggregated_data = {}
    for record in records:
        # Determine grouping key
        if request.group_by == "hour":
            key = record.timestamp.strftime("%Y-%m-%d %H:00")
        elif request.group_by == "day":
            key = record.timestamp.strftime("%Y-%m-%d")
        elif request.group_by == "week":
            key = record.timestamp.strftime("%Y-W%W")
        else:  # month
            key = record.timestamp.strftime("%Y-%m")
        
        if key not in aggregated_data:
            aggregated_data[key] = {
                "period": key,
                "request_count": 0,
                "total_cost": 0,
                "services": {}
            }
        
        aggregated_data[key]["request_count"] += record.request_count
        aggregated_data[key]["total_cost"] += record.total_cost
        
        if record.service_type not in aggregated_data[key]["services"]:
            aggregated_data[key]["services"][record.service_type] = {
                "request_count": 0,
                "total_cost": 0
            }
        
        aggregated_data[key]["services"][record.service_type]["request_count"] += record.request_count
        aggregated_data[key]["services"][record.service_type]["total_cost"] += record.total_cost
    
    return {
        "start_date": request.start_date,
        "end_date": request.end_date,
        "group_by": request.group_by,
        "data": list(aggregated_data.values()),
        "summary": {
            "total_requests": sum(r.request_count for r in records),
            "total_cost": sum(r.total_cost for r in records),
            "unique_services": len(set(r.service_type for r in records))
        }
    }


@router.get("/billing/invoices")
async def list_invoices(
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: TokenData = Depends(
        PermissionChecker(["billing.read"])
    ),
    db: AsyncSession = Depends(get_db)
):
    """List client invoices"""
    
    query = select(Invoice).where(
        Invoice.client_id == current_user.client_id
    )
    
    if status:
        query = query.where(Invoice.status == status)
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Invoice.id)).where(
            Invoice.client_id == current_user.client_id
        )
    )
    total_count = count_result.scalar()
    
    # Get paginated results
    result = await db.execute(
        query
        .order_by(Invoice.invoice_date.desc())
        .limit(limit)
        .offset(offset)
    )
    invoices = result.scalars().all()
    
    return {
        "invoices": [
            {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date,
                "due_date": invoice.due_date,
                "total_amount": invoice.total_amount,
                "currency": invoice.currency,
                "status": invoice.status,
                "invoice_url": invoice.invoice_url
            }
            for invoice in invoices
        ],
        "pagination": {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
    }


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "partners-api",
        "version": settings.API_VERSION,
        "timestamp": datetime.utcnow()
    }