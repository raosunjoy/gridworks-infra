"""
GridWorks Black - Premium Exclusive Trading Platform
The "Amex Black Card of Trading" for ultra-HNI users
"""

from .app_core import GridWorksBlackApp
from .market_butler import MarketButler
from .authentication import BlackAuthentication
from .luxury_ux import LuxuryUIComponents
from .concierge_services import ConciergeServices

__all__ = [
    'GridWorksBlackApp',
    'MarketButler', 
    'BlackAuthentication',
    'LuxuryUIComponents',
    'ConciergeServices'
]

__version__ = '1.0.0'
__tier__ = 'BLACK'