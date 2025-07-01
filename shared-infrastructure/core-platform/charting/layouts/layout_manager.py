"""
Layout Manager for Multi-Chart Views

Manages chart layouts and arrangements similar to 
professional trading platforms.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

from app.core.logging import logger


class LayoutType(Enum):
    """Available layout types"""
    SINGLE = "single"
    SPLIT_HORIZONTAL = "split_horizontal"
    SPLIT_VERTICAL = "split_vertical"
    GRID_2X2 = "grid_2x2"
    GRID_3X3 = "grid_3x3"
    CUSTOM = "custom"
    TABS = "tabs"
    OVERLAY = "overlay"


@dataclass
class LayoutCell:
    """Individual cell in a layout"""
    id: str
    x: float  # 0-1 normalized position
    y: float  # 0-1 normalized position
    width: float  # 0-1 normalized width
    height: float  # 0-1 normalized height
    chart_id: Optional[str] = None
    min_width: float = 0.1
    min_height: float = 0.1
    resizable: bool = True
    movable: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "chart_id": self.chart_id,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "resizable": self.resizable,
            "movable": self.movable
        }


@dataclass
class Layout:
    """Chart layout configuration"""
    id: str
    name: str
    type: LayoutType
    cells: List[LayoutCell] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "cells": [cell.to_dict() for cell in self.cells],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class LayoutManager:
    """
    Manages chart layouts and multi-chart views
    Provides professional trading platform-like layouts
    """
    
    def __init__(self):
        self.layouts: Dict[str, Layout] = {}
        self.predefined_layouts = self._create_predefined_layouts()
        
        # Layout constraints
        self.max_charts_per_layout = 16
        self.min_cell_size = 0.05  # 5% of container
        
    def _create_predefined_layouts(self) -> Dict[str, Layout]:
        """Create predefined layouts"""
        
        layouts = {}
        
        # Single chart layout
        single = Layout(
            id="single",
            name="Single Chart",
            type=LayoutType.SINGLE,
            cells=[
                LayoutCell(
                    id="cell_1",
                    x=0, y=0,
                    width=1, height=1,
                    resizable=False,
                    movable=False
                )
            ]
        )
        layouts["single"] = single
        
        # Horizontal split
        h_split = Layout(
            id="split_horizontal",
            name="Horizontal Split",
            type=LayoutType.SPLIT_HORIZONTAL,
            cells=[
                LayoutCell(
                    id="cell_1",
                    x=0, y=0,
                    width=1, height=0.5
                ),
                LayoutCell(
                    id="cell_2",
                    x=0, y=0.5,
                    width=1, height=0.5
                )
            ]
        )
        layouts["split_horizontal"] = h_split
        
        # Vertical split
        v_split = Layout(
            id="split_vertical",
            name="Vertical Split",
            type=LayoutType.SPLIT_VERTICAL,
            cells=[
                LayoutCell(
                    id="cell_1",
                    x=0, y=0,
                    width=0.5, height=1
                ),
                LayoutCell(
                    id="cell_2",
                    x=0.5, y=0,
                    width=0.5, height=1
                )
            ]
        )
        layouts["split_vertical"] = v_split
        
        # 2x2 Grid
        grid_2x2 = Layout(
            id="grid_2x2",
            name="2x2 Grid",
            type=LayoutType.GRID_2X2,
            cells=[
                LayoutCell(id="cell_1", x=0, y=0, width=0.5, height=0.5),
                LayoutCell(id="cell_2", x=0.5, y=0, width=0.5, height=0.5),
                LayoutCell(id="cell_3", x=0, y=0.5, width=0.5, height=0.5),
                LayoutCell(id="cell_4", x=0.5, y=0.5, width=0.5, height=0.5)
            ]
        )
        layouts["grid_2x2"] = grid_2x2
        
        # 3x3 Grid
        grid_3x3 = Layout(
            id="grid_3x3",
            name="3x3 Grid",
            type=LayoutType.GRID_3X3,
            cells=[]
        )
        
        # Generate 3x3 cells
        for row in range(3):
            for col in range(3):
                cell = LayoutCell(
                    id=f"cell_{row * 3 + col + 1}",
                    x=col * (1/3),
                    y=row * (1/3),
                    width=1/3,
                    height=1/3
                )
                grid_3x3.cells.append(cell)
        
        layouts["grid_3x3"] = grid_3x3
        
        # Professional trading layout
        trading = Layout(
            id="trading",
            name="Professional Trading",
            type=LayoutType.CUSTOM,
            cells=[
                # Main chart (large)
                LayoutCell(id="main_chart", x=0, y=0, width=0.7, height=0.7),
                # Watchlist
                LayoutCell(id="watchlist", x=0.7, y=0, width=0.3, height=0.3),
                # Market depth
                LayoutCell(id="market_depth", x=0.7, y=0.3, width=0.3, height=0.4),
                # News/alerts
                LayoutCell(id="news", x=0, y=0.7, width=0.4, height=0.3),
                # Order book
                LayoutCell(id="orders", x=0.4, y=0.7, width=0.3, height=0.3),
                # Portfolio
                LayoutCell(id="portfolio", x=0.7, y=0.7, width=0.3, height=0.3)
            ]
        )
        layouts["trading"] = trading
        
        return layouts
    
    async def apply_layout(
        self,
        chart_ids: List[str],
        layout_type: LayoutType
    ) -> Layout:
        """Apply a layout to a set of charts"""
        
        # Get or create layout
        layout_id = layout_type.value
        if layout_id in self.predefined_layouts:
            layout = self.predefined_layouts[layout_id]
        else:
            layout = await self._create_custom_layout(chart_ids, layout_type)
        
        # Assign charts to cells
        assigned_layout = await self._assign_charts_to_layout(layout, chart_ids)
        
        logger.info(f"Applied {layout_type.value} layout to {len(chart_ids)} charts")
        return assigned_layout
    
    async def create_custom_layout(
        self,
        name: str,
        cells: List[Dict[str, Any]]
    ) -> str:
        """Create a custom layout"""
        
        import uuid
        layout_id = str(uuid.uuid4())
        
        # Convert cell dicts to LayoutCell objects
        layout_cells = []
        for i, cell_data in enumerate(cells):
            cell = LayoutCell(
                id=cell_data.get("id", f"cell_{i + 1}"),
                x=cell_data["x"],
                y=cell_data["y"],
                width=cell_data["width"],
                height=cell_data["height"],
                chart_id=cell_data.get("chart_id"),
                resizable=cell_data.get("resizable", True),
                movable=cell_data.get("movable", True)
            )
            layout_cells.append(cell)
        
        # Validate layout
        if not await self._validate_layout(layout_cells):
            raise ValueError("Invalid layout configuration")
        
        # Create layout
        layout = Layout(
            id=layout_id,
            name=name,
            type=LayoutType.CUSTOM,
            cells=layout_cells
        )
        
        self.layouts[layout_id] = layout
        
        logger.info(f"Created custom layout {layout_id}")
        return layout_id
    
    async def resize_cell(
        self,
        layout_id: str,
        cell_id: str,
        new_width: float,
        new_height: float
    ):
        """Resize a cell in a layout"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        
        # Find cell
        cell = None
        for c in layout.cells:
            if c.id == cell_id:
                cell = c
                break
        
        if not cell:
            raise ValueError(f"Cell {cell_id} not found in layout")
        
        if not cell.resizable:
            raise ValueError(f"Cell {cell_id} is not resizable")
        
        # Validate new size
        if new_width < cell.min_width or new_height < cell.min_height:
            raise ValueError("New size below minimum")
        
        if cell.x + new_width > 1 or cell.y + new_height > 1:
            raise ValueError("New size exceeds layout bounds")
        
        # Check for overlaps with other cells
        if await self._check_overlap_after_resize(layout, cell, new_width, new_height):
            raise ValueError("Resize would cause overlap")
        
        # Apply resize
        cell.width = new_width
        cell.height = new_height
        
        logger.info(f"Resized cell {cell_id} to {new_width}x{new_height}")
    
    async def move_cell(
        self,
        layout_id: str,
        cell_id: str,
        new_x: float,
        new_y: float
    ):
        """Move a cell in a layout"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        
        # Find cell
        cell = None
        for c in layout.cells:
            if c.id == cell_id:
                cell = c
                break
        
        if not cell:
            raise ValueError(f"Cell {cell_id} not found in layout")
        
        if not cell.movable:
            raise ValueError(f"Cell {cell_id} is not movable")
        
        # Validate new position
        if new_x < 0 or new_y < 0:
            raise ValueError("Position cannot be negative")
        
        if new_x + cell.width > 1 or new_y + cell.height > 1:
            raise ValueError("New position exceeds layout bounds")
        
        # Check for overlaps
        if await self._check_overlap_after_move(layout, cell, new_x, new_y):
            raise ValueError("Move would cause overlap")
        
        # Apply move
        cell.x = new_x
        cell.y = new_y
        
        logger.info(f"Moved cell {cell_id} to ({new_x}, {new_y})")
    
    async def add_cell(
        self,
        layout_id: str,
        x: float,
        y: float,
        width: float,
        height: float,
        chart_id: Optional[str] = None
    ) -> str:
        """Add a new cell to a layout"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        
        if len(layout.cells) >= self.max_charts_per_layout:
            raise ValueError(f"Maximum {self.max_charts_per_layout} cells allowed")
        
        # Generate cell ID
        cell_id = f"cell_{len(layout.cells) + 1}"
        
        # Create cell
        cell = LayoutCell(
            id=cell_id,
            x=x, y=y,
            width=width, height=height,
            chart_id=chart_id
        )
        
        # Validate position and size
        if not await self._validate_cell(cell, layout.cells):
            raise ValueError("Invalid cell position or size")
        
        # Add to layout
        layout.cells.append(cell)
        
        logger.info(f"Added cell {cell_id} to layout {layout_id}")
        return cell_id
    
    async def remove_cell(
        self,
        layout_id: str,
        cell_id: str
    ):
        """Remove a cell from a layout"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        
        # Find and remove cell
        for i, cell in enumerate(layout.cells):
            if cell.id == cell_id:
                layout.cells.pop(i)
                logger.info(f"Removed cell {cell_id} from layout {layout_id}")
                return
        
        raise ValueError(f"Cell {cell_id} not found in layout")
    
    async def save_layout(
        self,
        layout_id: str,
        name: str
    ) -> str:
        """Save current layout configuration"""
        
        if layout_id not in self.layouts:
            raise ValueError(f"Layout {layout_id} not found")
        
        layout = self.layouts[layout_id]
        
        # Create saved layout
        import uuid
        saved_id = str(uuid.uuid4())
        
        saved_layout = Layout(
            id=saved_id,
            name=name,
            type=layout.type,
            cells=[
                LayoutCell(
                    id=cell.id,
                    x=cell.x, y=cell.y,
                    width=cell.width, height=cell.height,
                    chart_id=cell.chart_id,
                    resizable=cell.resizable,
                    movable=cell.movable
                )
                for cell in layout.cells
            ]
        )
        
        self.layouts[saved_id] = saved_layout
        
        logger.info(f"Saved layout as {name} with ID {saved_id}")
        return saved_id
    
    def get_layout(self, layout_id: str) -> Optional[Layout]:
        """Get layout by ID"""
        
        # Check predefined layouts first
        if layout_id in self.predefined_layouts:
            return self.predefined_layouts[layout_id]
        
        # Check custom layouts
        return self.layouts.get(layout_id)
    
    def get_all_layouts(self) -> List[Layout]:
        """Get all available layouts"""
        
        all_layouts = []
        all_layouts.extend(self.predefined_layouts.values())
        all_layouts.extend(self.layouts.values())
        
        return all_layouts
    
    async def _create_custom_layout(
        self,
        chart_ids: List[str],
        layout_type: LayoutType
    ) -> Layout:
        """Create custom layout for specific charts"""
        
        import uuid
        layout_id = str(uuid.uuid4())
        
        # Generate layout based on number of charts
        num_charts = len(chart_ids)
        cells = []
        
        if num_charts == 1:
            cells = [LayoutCell(id="cell_1", x=0, y=0, width=1, height=1)]
        elif num_charts == 2:
            cells = [
                LayoutCell(id="cell_1", x=0, y=0, width=0.5, height=1),
                LayoutCell(id="cell_2", x=0.5, y=0, width=0.5, height=1)
            ]
        elif num_charts <= 4:
            # 2x2 grid
            positions = [(0, 0), (0.5, 0), (0, 0.5), (0.5, 0.5)]
            for i in range(num_charts):
                x, y = positions[i]
                cells.append(LayoutCell(
                    id=f"cell_{i + 1}",
                    x=x, y=y,
                    width=0.5, height=0.5
                ))
        elif num_charts <= 9:
            # 3x3 grid
            for i in range(num_charts):
                row = i // 3
                col = i % 3
                cells.append(LayoutCell(
                    id=f"cell_{i + 1}",
                    x=col * (1/3), y=row * (1/3),
                    width=1/3, height=1/3
                ))
        else:
            # Dynamic grid for more charts
            cols = int(np.ceil(np.sqrt(num_charts)))
            rows = int(np.ceil(num_charts / cols))
            
            for i in range(num_charts):
                row = i // cols
                col = i % cols
                cells.append(LayoutCell(
                    id=f"cell_{i + 1}",
                    x=col * (1/cols), y=row * (1/rows),
                    width=1/cols, height=1/rows
                ))
        
        return Layout(
            id=layout_id,
            name=f"Custom {num_charts} Charts",
            type=layout_type,
            cells=cells
        )
    
    async def _assign_charts_to_layout(
        self,
        layout: Layout,
        chart_ids: List[str]
    ) -> Layout:
        """Assign chart IDs to layout cells"""
        
        # Create a copy of the layout
        assigned_layout = Layout(
            id=layout.id,
            name=layout.name,
            type=layout.type,
            cells=[]
        )
        
        # Assign charts to cells
        for i, cell in enumerate(layout.cells):
            new_cell = LayoutCell(
                id=cell.id,
                x=cell.x, y=cell.y,
                width=cell.width, height=cell.height,
                chart_id=chart_ids[i] if i < len(chart_ids) else None,
                resizable=cell.resizable,
                movable=cell.movable
            )
            assigned_layout.cells.append(new_cell)
        
        return assigned_layout
    
    async def _validate_layout(self, cells: List[LayoutCell]) -> bool:
        """Validate layout configuration"""
        
        for cell in cells:
            if not await self._validate_cell(cell, [c for c in cells if c != cell]):
                return False
        
        return True
    
    async def _validate_cell(
        self,
        cell: LayoutCell,
        other_cells: List[LayoutCell]
    ) -> bool:
        """Validate individual cell"""
        
        # Check bounds
        if (cell.x < 0 or cell.y < 0 or
            cell.x + cell.width > 1 or cell.y + cell.height > 1):
            return False
        
        # Check minimum size
        if cell.width < self.min_cell_size or cell.height < self.min_cell_size:
            return False
        
        # Check overlaps
        for other in other_cells:
            if self._cells_overlap(cell, other):
                return False
        
        return True
    
    def _cells_overlap(self, cell1: LayoutCell, cell2: LayoutCell) -> bool:
        """Check if two cells overlap"""
        
        return not (
            cell1.x + cell1.width <= cell2.x or
            cell2.x + cell2.width <= cell1.x or
            cell1.y + cell1.height <= cell2.y or
            cell2.y + cell2.height <= cell1.y
        )
    
    async def _check_overlap_after_resize(
        self,
        layout: Layout,
        cell: LayoutCell,
        new_width: float,
        new_height: float
    ) -> bool:
        """Check if resize would cause overlap"""
        
        # Create temporary cell with new size
        temp_cell = LayoutCell(
            id=cell.id,
            x=cell.x, y=cell.y,
            width=new_width, height=new_height
        )
        
        # Check against all other cells
        for other in layout.cells:
            if other.id != cell.id and self._cells_overlap(temp_cell, other):
                return True
        
        return False
    
    async def _check_overlap_after_move(
        self,
        layout: Layout,
        cell: LayoutCell,
        new_x: float,
        new_y: float
    ) -> bool:
        """Check if move would cause overlap"""
        
        # Create temporary cell with new position
        temp_cell = LayoutCell(
            id=cell.id,
            x=new_x, y=new_y,
            width=cell.width, height=cell.height
        )
        
        # Check against all other cells
        for other in layout.cells:
            if other.id != cell.id and self._cells_overlap(temp_cell, other):
                return True
        
        return False