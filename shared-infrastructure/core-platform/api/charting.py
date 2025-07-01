"""
Charting API Endpoints

FastAPI endpoints for the advanced charting platform.
Provides REST API access to all charting features.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import json
import io

from app.charting.core.chart_manager import ChartManager, ChartLayout
from app.charting.core.chart_engine import ChartType, TimeFrame
from app.core.auth import get_current_user
from app.core.logging import logger

# Global chart manager instance
chart_manager = ChartManager()

# Router
router = APIRouter(prefix="/api/v1/charting", tags=["charting"])

# Pydantic models for API
class ChartCreateRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    chart_type: str = Field(default="candlestick", description="Chart type")
    timeframe: str = Field(default="5m", description="Timeframe")
    theme: str = Field(default="dark", description="Chart theme")
    show_volume: bool = Field(default=True, description="Show volume")
    enable_ai_patterns: bool = Field(default=True, description="Enable AI pattern detection")
    enable_voice_commands: bool = Field(default=True, description="Enable voice commands")

class IndicatorAddRequest(BaseModel):
    indicator_type: str = Field(..., description="Indicator type")
    params: Dict[str, Any] = Field(default_factory=dict, description="Indicator parameters")
    color: Optional[str] = Field(None, description="Indicator color")
    panel: str = Field(default="main", description="Panel to display in")

class DrawingAddRequest(BaseModel):
    drawing_type: str = Field(..., description="Drawing tool type")
    points: List[Dict[str, Any]] = Field(..., description="Drawing points")
    style: Dict[str, Any] = Field(default_factory=dict, description="Drawing style")

class VoiceCommandRequest(BaseModel):
    command: str = Field(..., description="Voice command to execute")

class AlertCreateRequest(BaseModel):
    condition: Dict[str, Any] = Field(..., description="Alert condition")
    notification_channels: List[str] = Field(..., description="Notification channels")

class ChartShareRequest(BaseModel):
    include_image: bool = Field(default=True, description="Include chart image")
    analysis_notes: Optional[str] = Field(None, description="Analysis notes")
    visibility: str = Field(default="public", description="Share visibility")

class LayoutUpdateRequest(BaseModel):
    layout_type: str = Field(..., description="Layout type")

class TemplateRequest(BaseModel):
    template_name: str = Field(..., description="Template name")

# API Response models
class ChartResponse(BaseModel):
    chart_id: str
    symbol: str
    chart_type: str
    timeframe: str
    created_at: datetime

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    charts: List[str]
    layout: str
    active_chart: Optional[str]

class IndicatorResponse(BaseModel):
    indicator_id: str
    type: str
    params: Dict[str, Any]
    added_at: datetime

class DrawingResponse(BaseModel):
    drawing_id: str
    type: str
    points: List[Dict[str, Any]]
    style: Dict[str, Any]
    created_at: datetime

class VoiceCommandResponse(BaseModel):
    success: bool
    action: Optional[str]
    message: str
    data: Optional[Dict[str, Any]]

class PatternResponse(BaseModel):
    pattern: str
    type: str
    confidence: float
    description: str

class AlertResponse(BaseModel):
    alert_id: str
    condition: Dict[str, Any]
    channels: List[str]
    created_at: datetime

class ShareResponse(BaseModel):
    share_id: str
    share_url: str
    whatsapp_url: str
    zk_proof: str
    image_url: Optional[str]


# Session Management
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    user: Dict = Depends(get_current_user),
    preferences: Optional[Dict[str, Any]] = None
):
    """Create a new charting session"""
    
    try:
        session_id = await chart_manager.create_session(
            user_id=user["id"],
            preferences=preferences
        )
        
        session = chart_manager.sessions[session_id]
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            charts=session.charts,
            layout=session.layout.value,
            active_chart=session.active_chart
        )
    
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    user: Dict = Depends(get_current_user)
):
    """Get session details"""
    
    if session_id not in chart_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chart_manager.sessions[session_id]
    
    # Check ownership
    if session.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return SessionResponse(
        session_id=session.session_id,
        user_id=session.user_id,
        charts=session.charts,
        layout=session.layout.value,
        active_chart=session.active_chart
    )


# Chart Management
@router.post("/sessions/{session_id}/charts", response_model=ChartResponse)
async def create_chart(
    session_id: str,
    request: ChartCreateRequest,
    user: Dict = Depends(get_current_user)
):
    """Create a new chart in a session"""
    
    if session_id not in chart_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chart_manager.sessions[session_id]
    if session.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Convert string enums
        chart_type = ChartType[request.chart_type.upper()]
        timeframe = TimeFrame[request.timeframe.upper()]
        
        chart_id = await chart_manager.create_chart(
            session_id=session_id,
            symbol=request.symbol,
            chart_type=chart_type,
            timeframe=timeframe,
            theme=request.theme,
            show_volume=request.show_volume,
            enable_ai_patterns=request.enable_ai_patterns,
            enable_voice_commands=request.enable_voice_commands
        )
        
        return ChartResponse(
            chart_id=chart_id,
            symbol=request.symbol,
            chart_type=request.chart_type,
            timeframe=request.timeframe,
            created_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error creating chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/{chart_id}/data")
async def get_chart_data(
    chart_id: str,
    limit: int = Query(1000, le=5000),
    user: Dict = Depends(get_current_user)
):
    """Get chart data"""
    
    if chart_id not in chart_manager.engine.charts:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        chart = chart_manager.engine.charts[chart_id]
        
        # Get recent data
        data = chart.data[-limit:] if chart.data else []
        
        return {
            "chart_id": chart_id,
            "symbol": chart.config.symbol,
            "timeframe": chart.config.timeframe.value,
            "data": [d.to_dict() for d in data],
            "indicators": {
                ind_id: {
                    "type": ind["type"],
                    "values": ind["values"].tolist() if hasattr(ind["values"], "tolist") else []
                }
                for ind_id, ind in chart.indicators.items()
            },
            "drawings": [d.to_dict() for d in chart.drawings.values()],
            "patterns": [p.__dict__ for p in chart.candle_patterns[-10:]]  # Last 10 patterns
        }
    
    except Exception as e:
        logger.error(f"Error getting chart data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/charts/{chart_id}/image")
async def get_chart_image(
    chart_id: str,
    width: int = Query(800, ge=400, le=2000),
    height: int = Query(600, ge=300, le=1500),
    format: str = Query("png", regex="^(png|jpg|svg)$"),
    user: Dict = Depends(get_current_user)
):
    """Get chart as image for sharing/WhatsApp"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        image_data = await chart_manager.get_chart_image(
            session_id=session_id,
            chart_id=chart_id,
            width=width,
            height=height
        )
        
        # Return as streaming response
        media_type = f"image/{format}"
        return StreamingResponse(
            io.BytesIO(image_data),
            media_type=media_type,
            headers={"Content-Disposition": f"inline; filename=chart.{format}"}
        )
    
    except Exception as e:
        logger.error(f"Error generating chart image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Indicators
@router.post("/charts/{chart_id}/indicators", response_model=IndicatorResponse)
async def add_indicator(
    chart_id: str,
    request: IndicatorAddRequest,
    user: Dict = Depends(get_current_user)
):
    """Add technical indicator to chart"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        # Add color to params if provided
        params = request.params.copy()
        if request.color:
            params["color"] = request.color
        params["panel"] = request.panel
        
        indicator_id = await chart_manager.add_indicator(
            session_id=session_id,
            chart_id=chart_id,
            indicator_type=request.indicator_type,
            params=params
        )
        
        return IndicatorResponse(
            indicator_id=indicator_id,
            type=request.indicator_type,
            params=params,
            added_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error adding indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/charts/{chart_id}/indicators/{indicator_id}")
async def remove_indicator(
    chart_id: str,
    indicator_id: str,
    user: Dict = Depends(get_current_user)
):
    """Remove indicator from chart"""
    
    if chart_id not in chart_manager.engine.charts:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        chart = chart_manager.engine.charts[chart_id]
        
        if indicator_id not in chart.indicators:
            raise HTTPException(status_code=404, detail="Indicator not found")
        
        chart.indicator_manager.remove_indicator(indicator_id)
        del chart.indicators[indicator_id]
        
        return {"success": True, "message": "Indicator removed"}
    
    except Exception as e:
        logger.error(f"Error removing indicator: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Drawing Tools
@router.post("/charts/{chart_id}/drawings", response_model=DrawingResponse)
async def add_drawing(
    chart_id: str,
    request: DrawingAddRequest,
    user: Dict = Depends(get_current_user)
):
    """Add drawing tool to chart"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        drawing_id = await chart_manager.add_drawing(
            session_id=session_id,
            chart_id=chart_id,
            drawing_type=request.drawing_type,
            points=request.points,
            style=request.style
        )
        
        return DrawingResponse(
            drawing_id=drawing_id,
            type=request.drawing_type,
            points=request.points,
            style=request.style,
            created_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error adding drawing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/charts/{chart_id}/drawings/{drawing_id}")
async def remove_drawing(
    chart_id: str,
    drawing_id: str,
    user: Dict = Depends(get_current_user)
):
    """Remove drawing from chart"""
    
    if chart_id not in chart_manager.engine.charts:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        chart = chart_manager.engine.charts[chart_id]
        await chart.drawing_manager.delete_drawing(drawing_id)
        
        return {"success": True, "message": "Drawing removed"}
    
    except Exception as e:
        logger.error(f"Error removing drawing: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Voice Commands
@router.post("/sessions/{session_id}/voice", response_model=VoiceCommandResponse)
async def execute_voice_command(
    session_id: str,
    request: VoiceCommandRequest,
    user: Dict = Depends(get_current_user)
):
    """Execute voice command on active chart"""
    
    if session_id not in chart_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chart_manager.sessions[session_id]
    if session.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        result = await chart_manager.execute_voice_command(
            session_id=session_id,
            command=request.command
        )
        
        return VoiceCommandResponse(
            success=result.get("success", False),
            action=result.get("action"),
            message=result.get("message", ""),
            data=result.get("data")
        )
    
    except Exception as e:
        logger.error(f"Error executing voice command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Pattern Detection
@router.get("/charts/{chart_id}/patterns", response_model=List[PatternResponse])
async def detect_patterns(
    chart_id: str,
    user: Dict = Depends(get_current_user)
):
    """Detect AI patterns on chart"""
    
    if chart_id not in chart_manager.engine.charts:
        raise HTTPException(status_code=404, detail="Chart not found")
    
    try:
        patterns = await chart_manager.engine.detect_patterns(chart_id)
        
        return [
            PatternResponse(
                pattern=p.get("pattern", "Unknown"),
                type=p.get("type", "neutral"),
                confidence=p.get("confidence", 0.0),
                description=p.get("description", "")
            )
            for p in patterns
        ]
    
    except Exception as e:
        logger.error(f"Error detecting patterns: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alerts
@router.post("/charts/{chart_id}/alerts", response_model=AlertResponse)
async def create_alert(
    chart_id: str,
    request: AlertCreateRequest,
    user: Dict = Depends(get_current_user)
):
    """Create alert on chart"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        alert_id = await chart_manager.create_alert(
            session_id=session_id,
            chart_id=chart_id,
            condition=request.condition,
            notification_channels=request.notification_channels
        )
        
        return AlertResponse(
            alert_id=alert_id,
            condition=request.condition,
            channels=request.notification_channels,
            created_at=datetime.now()
        )
    
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Sharing
@router.post("/charts/{chart_id}/share", response_model=ShareResponse)
async def share_chart(
    chart_id: str,
    request: ChartShareRequest,
    user: Dict = Depends(get_current_user)
):
    """Share chart with social features"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        share_options = {
            "include_image": request.include_image,
            "analysis_notes": request.analysis_notes,
            "visibility": request.visibility
        }
        
        share_data = await chart_manager.share_chart(
            session_id=session_id,
            chart_id=chart_id,
            share_options=share_options
        )
        
        return ShareResponse(
            share_id=share_data.get("share_id", ""),
            share_url=share_data.get("share_url", ""),
            whatsapp_url=share_data.get("whatsapp_url", ""),
            zk_proof=share_data.get("zk_proof", ""),
            image_url=share_data.get("image_url")
        )
    
    except Exception as e:
        logger.error(f"Error sharing chart: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Layouts
@router.put("/sessions/{session_id}/layout")
async def update_layout(
    session_id: str,
    request: LayoutUpdateRequest,
    user: Dict = Depends(get_current_user)
):
    """Update session layout"""
    
    if session_id not in chart_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chart_manager.sessions[session_id]
    if session.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        layout = ChartLayout[request.layout_type.upper()]
        await chart_manager.change_layout(session_id, layout)
        
        return {"success": True, "layout": layout.value}
    
    except Exception as e:
        logger.error(f"Error updating layout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layouts")
async def get_available_layouts():
    """Get all available layouts"""
    
    layouts = chart_manager.layout_manager.get_all_layouts()
    
    return {
        "layouts": [
            {
                "id": layout.id,
                "name": layout.name,
                "type": layout.type.value,
                "cells": len(layout.cells)
            }
            for layout in layouts
        ]
    }


# Templates
@router.post("/charts/{chart_id}/template")
async def save_chart_template(
    chart_id: str,
    request: TemplateRequest,
    user: Dict = Depends(get_current_user)
):
    """Save chart configuration as template"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        template_id = await chart_manager.save_chart_template(
            session_id=session_id,
            chart_id=chart_id,
            template_name=request.template_name
        )
        
        return {"template_id": template_id, "name": request.template_name}
    
    except Exception as e:
        logger.error(f"Error saving template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/charts/{chart_id}/template/{template_id}/apply")
async def apply_chart_template(
    chart_id: str,
    template_id: str,
    user: Dict = Depends(get_current_user)
):
    """Apply saved template to chart"""
    
    # Find session for chart
    session_id = None
    for sid, session in chart_manager.sessions.items():
        if chart_id in session.charts and session.user_id == user["id"]:
            session_id = sid
            break
    
    if not session_id:
        raise HTTPException(status_code=404, detail="Chart not found or access denied")
    
    try:
        await chart_manager.apply_template(
            session_id=session_id,
            chart_id=chart_id,
            template_id=template_id
        )
        
        return {"success": True, "message": "Template applied"}
    
    except Exception as e:
        logger.error(f"Error applying template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket for real-time updates
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str
):
    """WebSocket endpoint for real-time chart updates"""
    
    await websocket.accept()
    
    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                # Handle subscription
                symbols = message.get("symbols", [])
                
                # Subscribe to symbols through WebSocket manager
                for symbol in symbols:
                    await chart_manager.websocket_manager.subscribe_to_symbol(symbol)
                
                # Send confirmation
                await websocket.send_text(json.dumps({
                    "type": "subscribe_confirm",
                    "symbols": symbols
                }))
            
            elif message.get("type") == "ping":
                # Send pong
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")


# Health and Metrics
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "metrics": chart_manager.metrics
    }


@router.get("/metrics")
async def get_metrics(
    user: Dict = Depends(get_current_user)
):
    """Get detailed metrics"""
    
    # Only allow admin users
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    websocket_metrics = chart_manager.websocket_manager.get_metrics()
    
    return {
        "chart_manager": chart_manager.metrics,
        "websocket": websocket_metrics,
        "engine": {
            "active_charts": len(chart_manager.engine.charts),
            "render_times": chart_manager.engine.render_times[-10:],  # Last 10
            "data_subscriptions": len(chart_manager.engine.data_subscriptions)
        }
    }


# Initialize chart manager on startup
@router.on_event("startup")
async def startup_event():
    """Initialize chart manager"""
    await chart_manager.initialize()
    logger.info("Charting platform initialized")


@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup chart manager"""
    await chart_manager.shutdown()
    logger.info("Charting platform shut down")