#!/bin/bash
# TradeMate Session Setup Script
# Run this at the start of every new session for project continuity

echo "🚀 TradeMate Session Setup - Ensuring Project Continuity"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Check if in correct directory
if [ ! -f "PROJECT_STATUS.md" ]; then
    echo -e "${RED}❌ Error: Not in TradeMate project root directory${NC}"
    echo "Please navigate to the TradeMate project directory first"
    exit 1
fi

echo -e "${GREEN}✅ In TradeMate project directory${NC}"

# Step 2: Check git status
echo -e "\n${BLUE}📊 Git Status Check${NC}"
echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log -1 --oneline)"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}⚠️  Warning: You have uncommitted changes${NC}"
    git status --short
    echo ""
else
    echo -e "${GREEN}✅ Working tree is clean${NC}"
fi

# Step 3: Quick test run
echo -e "\n${BLUE}🧪 Running Quick Health Check${NC}"
if command -v python &> /dev/null; then
    if python -m pytest tests/ --tb=no -q --disable-warnings 2>/dev/null; then
        echo -e "${GREEN}✅ All tests passing${NC}"
    else
        echo -e "${RED}❌ Some tests are failing - Fix before proceeding!${NC}"
        echo "Run 'python -m pytest tests/ -v' for details"
    fi
else
    echo -e "${YELLOW}⚠️  Python not found - skipping test check${NC}"
fi

# Step 4: Show current project status
echo -e "\n${BLUE}📋 Current Project Status${NC}"
echo "Reading PROJECT_STATUS.md..."

# Extract key information from status file
if [ -f "PROJECT_STATUS.md" ]; then
    # Get last updated time
    LAST_UPDATED=$(grep "Last Updated" PROJECT_STATUS.md | head -1 | sed 's/.*Last Updated.*: //' | sed 's/ |.*//')
    
    # Get phase status
    PHASE_STATUS=$(grep "Current Phase" PROJECT_STATUS.md | head -1 | sed 's/.*Current Phase.*: //')
    
    echo "Last Updated: $LAST_UPDATED"
    echo "Current Phase: $PHASE_STATUS"
    
    # Show Phase 3 progress
    echo -e "\n${YELLOW}Phase 3 Task Status:${NC}"
    echo "🔄 Options Flow Analyzer: In Progress (40% complete)"
    echo "⏳ Algorithmic Alerts: Pending (20% complete)"
    echo "⏳ Integration Testing: Pending"
    echo "⏳ Portfolio Analytics Advanced: Pending"
    echo "⏳ Community Features: Pending"
else
    echo -e "${RED}❌ PROJECT_STATUS.md not found${NC}"
fi

# Step 5: Show next priority tasks
echo -e "\n${BLUE}🎯 Next Priority Tasks (HIGH PRIORITY)${NC}"
echo "1. Complete Options Flow Analyzer (app/trading/options_analyzer.py)"
echo "2. Build Algorithmic Alerts Engine (app/ai/alert_engine.py)"
echo "3. Add Phase 2 Integration Tests (tests/integration/)"

# Step 6: Show key files for reference
echo -e "\n${BLUE}📁 Key Files for Current Session${NC}"
echo "Status Tracking:"
echo "  - PROJECT_STATUS.md (main status tracker)"
echo "  - SESSION_CONTINUITY.md (session guide)"
echo ""
echo "Phase 3 Development:"
echo "  - app/trading/options_analyzer.py (40% complete)"
echo "  - app/ai/alert_engine.py (20% complete)"
echo "  - tests/integration/ (pending)"

# Step 7: Performance and coverage check
echo -e "\n${BLUE}📊 System Health Metrics${NC}"
if [ -f "coverage.json" ]; then
    COVERAGE=$(python -c "import json; print(f\"{json.load(open('coverage.json'))['totals']['percent_covered']:.1f}%\")" 2>/dev/null || echo "Unknown")
    echo "Test Coverage: $COVERAGE"
else
    echo "Test Coverage: Run tests to check"
fi

# Step 8: Show development reminders
echo -e "\n${YELLOW}🚨 Development Reminders${NC}"
echo "✅ Always maintain 100% test coverage"
echo "⚡ Keep API responses under 100ms"
echo "🔒 Maintain enterprise security standards"
echo "📝 Update PROJECT_STATUS.md when completing tasks"
echo "🧪 Run tests before committing changes"

# Step 9: Quick commands reference
echo -e "\n${BLUE}⚡ Quick Commands for This Session${NC}"
echo "# Run all tests:"
echo "python -m pytest tests/ -v"
echo ""
echo "# Check test coverage:"
echo "python -m pytest tests/ --cov=app --cov-report=term-missing"
echo ""
echo "# Update project status:"
echo "python scripts/update_status.py"
echo ""
echo "# Check performance:"
echo "python -m pytest tests/ --benchmark-only"

# Step 10: Final checklist
echo -e "\n${GREEN}✅ Session Setup Complete!${NC}"
echo -e "\n${YELLOW}📋 Pre-Development Checklist:${NC}"
echo "□ Read PROJECT_STATUS.md for current state"
echo "□ Check SESSION_CONTINUITY.md for workflow"
echo "□ Verify all tests pass"
echo "□ Select HIGH priority task to work on"
echo "□ Understand performance targets"
echo "□ Ready to maintain 100% test coverage"

echo -e "\n${BLUE}🎯 Current Focus: Complete Phase 3 HIGH priority tasks${NC}"
echo "Happy coding! 🚀"
echo "=================================================="