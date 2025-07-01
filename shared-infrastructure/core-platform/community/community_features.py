"""
Community Features Expansion
===========================

Advanced community platform with group challenges, leaderboards,
social trading competitions, educational content, and gamification
to foster financial literacy and engagement.

Features:
- Investment challenges and competitions
- Community leaderboards and rankings
- Group portfolio challenges
- Educational content and quizzes
- Social trading tournaments
- Achievement system and badges
- Mentorship programs
- Discussion forums and market insights
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ChallengeType(Enum):
    PORTFOLIO_PERFORMANCE = "PORTFOLIO_PERFORMANCE"
    TRADING_VOLUME = "TRADING_VOLUME"
    LEARNING_QUIZ = "LEARNING_QUIZ"
    SAVINGS_GOAL = "SAVINGS_GOAL"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    DIVERSIFICATION = "DIVERSIFICATION"
    DIVIDEND_COLLECTION = "DIVIDEND_COLLECTION"
    LONG_TERM_HOLDING = "LONG_TERM_HOLDING"


class ChallengeStatus(Enum):
    UPCOMING = "UPCOMING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class UserLevel(Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"
    MASTER = "MASTER"


class BadgeType(Enum):
    FIRST_INVESTMENT = "FIRST_INVESTMENT"
    DIVERSIFICATION_MASTER = "DIVERSIFICATION_MASTER"
    RISK_MANAGER = "RISK_MANAGER"
    DIVIDEND_COLLECTOR = "DIVIDEND_COLLECTOR"
    LONG_TERM_INVESTOR = "LONG_TERM_INVESTOR"
    LEARNING_CHAMPION = "LEARNING_CHAMPION"
    COMMUNITY_LEADER = "COMMUNITY_LEADER"
    CHALLENGE_WINNER = "CHALLENGE_WINNER"
    MENTOR = "MENTOR"
    TOP_PERFORMER = "TOP_PERFORMER"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    level: UserLevel
    total_score: int
    portfolio_value: float
    join_date: datetime
    last_active: datetime
    achievements: List[str] = field(default_factory=list)
    badges: List[BadgeType] = field(default_factory=list)
    followers: List[str] = field(default_factory=list)
    following: List[str] = field(default_factory=list)
    groups: List[str] = field(default_factory=list)


@dataclass
class Challenge:
    challenge_id: str
    title: str
    description: str
    challenge_type: ChallengeType
    start_date: datetime
    end_date: datetime
    status: ChallengeStatus
    entry_fee: float
    prize_pool: float
    max_participants: int
    participants: List[str] = field(default_factory=list)
    rules: Dict[str, Any] = field(default_factory=dict)
    leaderboard: List[Dict] = field(default_factory=list)
    created_by: str = "GridWorks"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Group:
    group_id: str
    name: str
    description: str
    type: str  # "PUBLIC", "PRIVATE", "INVITE_ONLY"
    admin: str
    members: List[str]
    max_members: int
    created_at: datetime
    total_portfolio_value: float = 0.0
    group_performance: float = 0.0
    current_challenges: List[str] = field(default_factory=list)


@dataclass
class Achievement:
    achievement_id: str
    user_id: str
    badge_type: BadgeType
    title: str
    description: str
    earned_date: datetime
    points_awarded: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeaderboardEntry:
    user_id: str
    username: str
    score: float
    rank: int
    performance_metric: str
    period: str
    last_updated: datetime


@dataclass
class LearningContent:
    content_id: str
    title: str
    description: str
    content_type: str  # "ARTICLE", "VIDEO", "QUIZ", "TUTORIAL"
    difficulty_level: UserLevel
    estimated_time: int  # minutes
    content_data: Dict[str, Any]
    tags: List[str] = field(default_factory=list)
    completion_count: int = 0
    average_rating: float = 0.0


@dataclass
class Quiz:
    quiz_id: str
    title: str
    questions: List[Dict[str, Any]]
    difficulty: UserLevel
    passing_score: int
    time_limit: int  # minutes
    points_reward: int
    attempts_allowed: int = 3


@dataclass
class ForumPost:
    post_id: str
    user_id: str
    username: str
    title: str
    content: str
    category: str
    tags: List[str]
    likes: int
    replies: List[str]
    created_at: datetime
    last_updated: datetime


class CommunityEngine:
    """Main community features engine."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        
        # Data stores
        self.users = {}
        self.challenges = {}
        self.groups = {}
        self.achievements = defaultdict(list)
        self.leaderboards = defaultdict(list)
        self.learning_content = {}
        self.forum_posts = {}
        self.quiz_results = defaultdict(list)
        
        # Active tracking
        self.active_challenges = []
        self.daily_leaderboard = []
        self.weekly_leaderboard = []
        self.monthly_leaderboard = []
        
        self.running = False
        
    def _default_config(self) -> Dict:
        return {
            "max_challenges_per_user": 5,
            "default_challenge_duration": 30,  # days
            "leaderboard_refresh_interval": 300,  # 5 minutes
            "achievement_check_interval": 3600,   # 1 hour
            "max_group_size": 50,
            "min_challenge_participants": 3,
            "learning_points_multiplier": 10,
            "challenge_points_multiplier": 100
        }
    
    async def start_community_engine(self):
        """Start the community engine."""
        self.running = True
        logger.info("🔄 Community Engine started")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self._update_leaderboards()),
            asyncio.create_task(self._check_achievements()),
            asyncio.create_task(self._manage_challenges()),
            asyncio.create_task(self._generate_daily_content())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"❌ Community engine error: {e}")
        finally:
            self.running = False
    
    def stop_community_engine(self):
        """Stop the community engine."""
        self.running = False
        logger.info("⏹️ Community Engine stopped")
    
    # User Management
    async def register_user(self, user_data: Dict[str, Any]) -> User:
        """Register a new user in the community."""
        user_id = str(uuid.uuid4())
        
        user = User(
            user_id=user_id,
            username=user_data["username"],
            email=user_data["email"],
            level=UserLevel.BEGINNER,
            total_score=0,
            portfolio_value=user_data.get("portfolio_value", 0.0),
            join_date=datetime.now(),
            last_active=datetime.now()
        )
        
        self.users[user_id] = user
        
        # Award first achievement
        await self._award_achievement(user_id, BadgeType.FIRST_INVESTMENT, "Welcome to GridWorks!", 100)
        
        logger.info(f"👤 New user registered: {user.username}")
        return user
    
    async def update_user_portfolio(self, user_id: str, portfolio_value: float, performance: float):
        """Update user's portfolio information."""
        if user_id in self.users:
            user = self.users[user_id]
            old_value = user.portfolio_value
            user.portfolio_value = portfolio_value
            user.last_active = datetime.now()
            
            # Check for performance-based achievements
            await self._check_portfolio_achievements(user_id, old_value, portfolio_value, performance)
    
    # Challenge Management
    async def create_challenge(self, challenge_data: Dict[str, Any]) -> Challenge:
        """Create a new community challenge."""
        challenge_id = str(uuid.uuid4())
        
        challenge = Challenge(
            challenge_id=challenge_id,
            title=challenge_data["title"],
            description=challenge_data["description"],
            challenge_type=ChallengeType(challenge_data["type"]),
            start_date=datetime.fromisoformat(challenge_data["start_date"]),
            end_date=datetime.fromisoformat(challenge_data["end_date"]),
            status=ChallengeStatus.UPCOMING,
            entry_fee=challenge_data.get("entry_fee", 0.0),
            prize_pool=challenge_data.get("prize_pool", 1000.0),
            max_participants=challenge_data.get("max_participants", 100),
            rules=challenge_data.get("rules", {}),
            created_by=challenge_data.get("created_by", "GridWorks")
        )
        
        self.challenges[challenge_id] = challenge
        logger.info(f"🏆 New challenge created: {challenge.title}")
        
        return challenge
    
    async def join_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Join a user to a challenge."""
        if challenge_id not in self.challenges or user_id not in self.users:
            return False
        
        challenge = self.challenges[challenge_id]
        
        # Check if user can join
        if (len(challenge.participants) >= challenge.max_participants or
            user_id in challenge.participants or
            challenge.status != ChallengeStatus.UPCOMING):
            return False
        
        challenge.participants.append(user_id)
        
        # Deduct entry fee if applicable
        if challenge.entry_fee > 0:
            # In real implementation, handle payment
            pass
        
        logger.info(f"🎯 User {self.users[user_id].username} joined challenge: {challenge.title}")
        return True
    
    async def get_active_challenges(self, user_id: Optional[str] = None) -> List[Challenge]:
        """Get active challenges, optionally filtered by user."""
        active = [c for c in self.challenges.values() if c.status == ChallengeStatus.ACTIVE]
        
        if user_id:
            # Include challenges user can join or is already in
            user_challenges = [c for c in active if user_id in c.participants or len(c.participants) < c.max_participants]
            return user_challenges
        
        return active
    
    # Group Management
    async def create_group(self, creator_id: str, group_data: Dict[str, Any]) -> Group:
        """Create a new investment group."""
        group_id = str(uuid.uuid4())
        
        group = Group(
            group_id=group_id,
            name=group_data["name"],
            description=group_data["description"],
            type=group_data.get("type", "PUBLIC"),
            admin=creator_id,
            members=[creator_id],
            max_members=group_data.get("max_members", self.config["max_group_size"]),
            created_at=datetime.now()
        )
        
        self.groups[group_id] = group
        
        # Add group to user's groups
        if creator_id in self.users:
            self.users[creator_id].groups.append(group_id)
        
        logger.info(f"👥 New group created: {group.name}")
        return group
    
    async def join_group(self, user_id: str, group_id: str) -> bool:
        """Join a user to a group."""
        if group_id not in self.groups or user_id not in self.users:
            return False
        
        group = self.groups[group_id]
        
        if (len(group.members) >= group.max_members or 
            user_id in group.members):
            return False
        
        group.members.append(user_id)
        self.users[user_id].groups.append(group_id)
        
        logger.info(f"👥 User {self.users[user_id].username} joined group: {group.name}")
        return True
    
    async def create_group_challenge(self, group_id: str, challenge_data: Dict[str, Any]) -> Optional[Challenge]:
        """Create a challenge specific to a group."""
        if group_id not in self.groups:
            return None
        
        group = self.groups[group_id]
        challenge_data["title"] = f"[{group.name}] {challenge_data['title']}"
        challenge_data["max_participants"] = len(group.members)
        
        challenge = await self.create_challenge(challenge_data)
        
        # Auto-enroll group members
        for member_id in group.members:
            await self.join_challenge(member_id, challenge.challenge_id)
        
        group.current_challenges.append(challenge.challenge_id)
        return challenge
    
    # Learning & Education
    async def create_learning_content(self, content_data: Dict[str, Any]) -> LearningContent:
        """Create new educational content."""
        content_id = str(uuid.uuid4())
        
        content = LearningContent(
            content_id=content_id,
            title=content_data["title"],
            description=content_data["description"],
            content_type=content_data["type"],
            difficulty_level=UserLevel(content_data["difficulty"]),
            estimated_time=content_data["estimated_time"],
            content_data=content_data["content"],
            tags=content_data.get("tags", [])
        )
        
        self.learning_content[content_id] = content
        logger.info(f"📚 New learning content created: {content.title}")
        
        return content
    
    async def complete_learning_content(self, user_id: str, content_id: str, rating: int = 5) -> int:
        """Mark learning content as completed by user."""
        if content_id not in self.learning_content or user_id not in self.users:
            return 0
        
        content = self.learning_content[content_id]
        user = self.users[user_id]
        
        # Award points based on difficulty and content type
        points_multiplier = {
            UserLevel.BEGINNER: 1,
            UserLevel.INTERMEDIATE: 2,
            UserLevel.ADVANCED: 3,
            UserLevel.EXPERT: 4,
            UserLevel.MASTER: 5
        }
        
        points = self.config["learning_points_multiplier"] * points_multiplier[content.difficulty_level]
        user.total_score += points
        
        # Update content statistics
        content.completion_count += 1
        content.average_rating = ((content.average_rating * (content.completion_count - 1)) + rating) / content.completion_count
        
        # Check for learning achievements
        await self._check_learning_achievements(user_id)
        
        return points
    
    async def create_quiz(self, quiz_data: Dict[str, Any]) -> Quiz:
        """Create a new quiz."""
        quiz_id = str(uuid.uuid4())
        
        quiz = Quiz(
            quiz_id=quiz_id,
            title=quiz_data["title"],
            questions=quiz_data["questions"],
            difficulty=UserLevel(quiz_data["difficulty"]),
            passing_score=quiz_data.get("passing_score", 70),
            time_limit=quiz_data.get("time_limit", 30),
            points_reward=quiz_data.get("points_reward", 50)
        )
        
        return quiz
    
    async def submit_quiz_attempt(self, user_id: str, quiz_id: str, answers: List[Any]) -> Dict[str, Any]:
        """Submit a quiz attempt."""
        # In real implementation, validate answers and calculate score
        score = 85  # Simulated score
        passed = score >= 70
        
        result = {
            "user_id": user_id,
            "quiz_id": quiz_id,
            "score": score,
            "passed": passed,
            "timestamp": datetime.now(),
            "answers": answers
        }
        
        self.quiz_results[user_id].append(result)
        
        if passed:
            # Award points
            user = self.users[user_id]
            user.total_score += 50  # Quiz points
            await self._check_learning_achievements(user_id)
        
        return result
    
    # Forum & Discussion
    async def create_forum_post(self, user_id: str, post_data: Dict[str, Any]) -> ForumPost:
        """Create a new forum post."""
        post_id = str(uuid.uuid4())
        
        post = ForumPost(
            post_id=post_id,
            user_id=user_id,
            username=self.users[user_id].username,
            title=post_data["title"],
            content=post_data["content"],
            category=post_data["category"],
            tags=post_data.get("tags", []),
            likes=0,
            replies=[],
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.forum_posts[post_id] = post
        return post
    
    async def like_post(self, user_id: str, post_id: str) -> bool:
        """Like a forum post."""
        if post_id in self.forum_posts:
            self.forum_posts[post_id].likes += 1
            return True
        return False
    
    # Leaderboards
    async def _update_leaderboards(self):
        """Update community leaderboards."""
        while self.running:
            try:
                # Daily leaderboard (portfolio performance)
                daily_entries = []
                for user_id, user in self.users.items():
                    # In real implementation, calculate daily performance
                    daily_performance = 0.02  # Simulated 2% gain
                    
                    entry = LeaderboardEntry(
                        user_id=user_id,
                        username=user.username,
                        score=daily_performance,
                        rank=0,  # Will be set after sorting
                        performance_metric="Daily Return",
                        period="Daily",
                        last_updated=datetime.now()
                    )
                    daily_entries.append(entry)
                
                # Sort and assign ranks
                daily_entries.sort(key=lambda x: x.score, reverse=True)
                for i, entry in enumerate(daily_entries):
                    entry.rank = i + 1
                
                self.daily_leaderboard = daily_entries
                
                # Update weekly and monthly leaderboards similarly
                await self._update_weekly_leaderboard()
                await self._update_monthly_leaderboard()
                
                await asyncio.sleep(self.config["leaderboard_refresh_interval"])
                
            except Exception as e:
                logger.error(f"❌ Leaderboard update error: {e}")
                await asyncio.sleep(60)
    
    async def _update_weekly_leaderboard(self):
        """Update weekly leaderboard."""
        # Similar implementation to daily but with weekly performance
        pass
    
    async def _update_monthly_leaderboard(self):
        """Update monthly leaderboard."""
        # Similar implementation to daily but with monthly performance
        pass
    
    async def get_leaderboard(self, period: str = "daily", limit: int = 50) -> List[LeaderboardEntry]:
        """Get leaderboard for specified period."""
        if period.lower() == "daily":
            return self.daily_leaderboard[:limit]
        elif period.lower() == "weekly":
            return self.weekly_leaderboard[:limit]
        elif period.lower() == "monthly":
            return self.monthly_leaderboard[:limit]
        else:
            return self.daily_leaderboard[:limit]
    
    # Achievements & Badges
    async def _check_achievements(self):
        """Check and award achievements to users."""
        while self.running:
            try:
                for user_id in self.users.keys():
                    await self._check_user_achievements(user_id)
                
                await asyncio.sleep(self.config["achievement_check_interval"])
                
            except Exception as e:
                logger.error(f"❌ Achievement check error: {e}")
                await asyncio.sleep(300)
    
    async def _check_user_achievements(self, user_id: str):
        """Check achievements for a specific user."""
        user = self.users[user_id]
        
        # Check various achievement criteria
        await self._check_portfolio_achievements(user_id, 0, user.portfolio_value, 0)
        await self._check_activity_achievements(user_id)
        await self._check_learning_achievements(user_id)
        await self._check_community_achievements(user_id)
    
    async def _check_portfolio_achievements(self, user_id: str, old_value: float, new_value: float, performance: float):
        """Check portfolio-related achievements."""
        user = self.users[user_id]
        
        # Diversification Master
        if BadgeType.DIVERSIFICATION_MASTER not in user.badges:
            # In real implementation, check actual portfolio diversification
            if new_value > 100000:  # Simulated condition
                await self._award_achievement(user_id, BadgeType.DIVERSIFICATION_MASTER, "Portfolio well diversified across sectors", 500)
        
        # Long-term Investor
        if BadgeType.LONG_TERM_INVESTOR not in user.badges:
            days_since_join = (datetime.now() - user.join_date).days
            if days_since_join > 365 and new_value > old_value:
                await self._award_achievement(user_id, BadgeType.LONG_TERM_INVESTOR, "Invested for over 1 year with positive returns", 1000)
    
    async def _check_learning_achievements(self, user_id: str):
        """Check learning-related achievements."""
        user = self.users[user_id]
        
        # Learning Champion
        if BadgeType.LEARNING_CHAMPION not in user.badges:
            completed_quizzes = len([r for r in self.quiz_results[user_id] if r["passed"]])
            if completed_quizzes >= 10:
                await self._award_achievement(user_id, BadgeType.LEARNING_CHAMPION, "Completed 10 educational quizzes", 300)
    
    async def _check_activity_achievements(self, user_id: str):
        """Check activity-related achievements."""
        # Implementation for activity-based achievements
        pass
    
    async def _check_community_achievements(self, user_id: str):
        """Check community-related achievements."""
        user = self.users[user_id]
        
        # Community Leader
        if BadgeType.COMMUNITY_LEADER not in user.badges:
            if len(user.followers) >= 50:
                await self._award_achievement(user_id, BadgeType.COMMUNITY_LEADER, "Gained 50+ followers", 750)
    
    async def _award_achievement(self, user_id: str, badge_type: BadgeType, description: str, points: int):
        """Award an achievement to a user."""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        
        if badge_type not in user.badges:
            achievement = Achievement(
                achievement_id=str(uuid.uuid4()),
                user_id=user_id,
                badge_type=badge_type,
                title=badge_type.value.replace('_', ' ').title(),
                description=description,
                earned_date=datetime.now(),
                points_awarded=points
            )
            
            user.badges.append(badge_type)
            user.total_score += points
            self.achievements[user_id].append(achievement)
            
            logger.info(f"🏆 Achievement awarded to {user.username}: {achievement.title}")
    
    # Challenge Management Background Tasks
    async def _manage_challenges(self):
        """Manage challenge lifecycle."""
        while self.running:
            try:
                current_time = datetime.now()
                
                for challenge in self.challenges.values():
                    # Start upcoming challenges
                    if (challenge.status == ChallengeStatus.UPCOMING and 
                        current_time >= challenge.start_date):
                        challenge.status = ChallengeStatus.ACTIVE
                        logger.info(f"🚀 Challenge started: {challenge.title}")
                    
                    # End active challenges
                    elif (challenge.status == ChallengeStatus.ACTIVE and 
                          current_time >= challenge.end_date):
                        await self._complete_challenge(challenge)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Challenge management error: {e}")
                await asyncio.sleep(60)
    
    async def _complete_challenge(self, challenge: Challenge):
        """Complete a challenge and award prizes."""
        challenge.status = ChallengeStatus.COMPLETED
        
        # Calculate final leaderboard
        final_leaderboard = await self._calculate_challenge_results(challenge)
        challenge.leaderboard = final_leaderboard
        
        # Award prizes
        if final_leaderboard:
            # First place
            winner = final_leaderboard[0]
            await self._award_challenge_prize(winner["user_id"], challenge, 1)
            
            # Second and third place
            if len(final_leaderboard) > 1:
                await self._award_challenge_prize(final_leaderboard[1]["user_id"], challenge, 2)
            if len(final_leaderboard) > 2:
                await self._award_challenge_prize(final_leaderboard[2]["user_id"], challenge, 3)
        
        logger.info(f"🏁 Challenge completed: {challenge.title}")
    
    async def _calculate_challenge_results(self, challenge: Challenge) -> List[Dict]:
        """Calculate challenge results and rankings."""
        results = []
        
        for user_id in challenge.participants:
            if user_id in self.users:
                user = self.users[user_id]
                
                # Calculate score based on challenge type
                if challenge.challenge_type == ChallengeType.PORTFOLIO_PERFORMANCE:
                    score = 0.15  # Simulated 15% return
                elif challenge.challenge_type == ChallengeType.LEARNING_QUIZ:
                    user_quizzes = [r for r in self.quiz_results[user_id] if r["passed"]]
                    score = len(user_quizzes)
                else:
                    score = user.total_score
                
                results.append({
                    "user_id": user_id,
                    "username": user.username,
                    "score": score,
                    "rank": 0  # Will be set after sorting
                })
        
        # Sort by score and assign ranks
        results.sort(key=lambda x: x["score"], reverse=True)
        for i, result in enumerate(results):
            result["rank"] = i + 1
        
        return results
    
    async def _award_challenge_prize(self, user_id: str, challenge: Challenge, position: int):
        """Award prize to challenge winner."""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        
        # Prize distribution
        prize_distribution = {1: 0.6, 2: 0.3, 3: 0.1}  # 60%, 30%, 10%
        prize_amount = challenge.prize_pool * prize_distribution.get(position, 0)
        
        # Award points (in real implementation, would handle actual prizes)
        bonus_points = int(prize_amount)
        user.total_score += bonus_points
        
        # Award winner badge
        if position == 1:
            await self._award_achievement(user_id, BadgeType.CHALLENGE_WINNER, 
                                        f"Won challenge: {challenge.title}", bonus_points)
        
        logger.info(f"🎉 Prize awarded to {user.username}: Position {position}, Points: {bonus_points}")
    
    # Content Generation
    async def _generate_daily_content(self):
        """Generate daily educational content and challenges."""
        while self.running:
            try:
                # Generate daily tip
                await self._create_daily_tip()
                
                # Check if new challenges should be created
                await self._create_weekly_challenges()
                
                # Sleep until next day
                await asyncio.sleep(86400)  # 24 hours
                
            except Exception as e:
                logger.error(f"❌ Content generation error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _create_daily_tip(self):
        """Create daily financial tip."""
        tips = [
            "Diversify your portfolio across different sectors to reduce risk.",
            "Start investing early to benefit from compound growth.",
            "Review your portfolio regularly but avoid overtrading.",
            "Keep an emergency fund before investing in markets.",
            "Understand the fundamentals before investing in any stock."
        ]
        
        tip = {
            "title": "Daily Financial Tip",
            "description": tips[datetime.now().day % len(tips)],
            "type": "ARTICLE",
            "difficulty": "BEGINNER",
            "estimated_time": 2,
            "content": {"text": tips[datetime.now().day % len(tips)]},
            "tags": ["daily", "tip", "education"]
        }
        
        await self.create_learning_content(tip)
    
    async def _create_weekly_challenges(self):
        """Create weekly challenges."""
        if datetime.now().weekday() == 0:  # Monday
            challenge_templates = [
                {
                    "title": "Weekly Portfolio Performance Challenge",
                    "description": "Achieve the highest portfolio return this week",
                    "type": "PORTFOLIO_PERFORMANCE",
                    "prize_pool": 5000.0,
                    "duration_days": 7
                },
                {
                    "title": "Learning Challenge: Complete 3 Quizzes",
                    "description": "Complete 3 educational quizzes this week",
                    "type": "LEARNING_QUIZ",
                    "prize_pool": 2000.0,
                    "duration_days": 7
                }
            ]
            
            template = challenge_templates[datetime.now().isocalendar()[1] % len(challenge_templates)]
            
            challenge_data = {
                **template,
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=template["duration_days"])).isoformat(),
                "max_participants": 100
            }
            
            await self.create_challenge(challenge_data)
    
    # API Methods
    async def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get user's community dashboard."""
        if user_id not in self.users:
            return {}
        
        user = self.users[user_id]
        
        # Get user's rank in daily leaderboard
        user_rank = None
        for entry in self.daily_leaderboard:
            if entry.user_id == user_id:
                user_rank = entry.rank
                break
        
        # Get active challenges user is participating in
        user_challenges = [
            c for c in self.challenges.values() 
            if user_id in c.participants and c.status == ChallengeStatus.ACTIVE
        ]
        
        # Get recent achievements
        recent_achievements = sorted(
            self.achievements[user_id], 
            key=lambda x: x.earned_date, 
            reverse=True
        )[:5]
        
        return {
            "user": {
                "username": user.username,
                "level": user.level.value,
                "total_score": user.total_score,
                "portfolio_value": user.portfolio_value,
                "badges_count": len(user.badges),
                "followers_count": len(user.followers),
                "following_count": len(user.following)
            },
            "rankings": {
                "daily_rank": user_rank,
                "total_users": len(self.users)
            },
            "active_challenges": [
                {
                    "id": c.challenge_id,
                    "title": c.title,
                    "type": c.challenge_type.value,
                    "end_date": c.end_date.isoformat(),
                    "participants": len(c.participants)
                } for c in user_challenges
            ],
            "recent_achievements": [
                {
                    "title": a.title,
                    "description": a.description,
                    "points": a.points_awarded,
                    "date": a.earned_date.isoformat()
                } for a in recent_achievements
            ],
            "groups": [
                {
                    "id": group_id,
                    "name": self.groups[group_id].name if group_id in self.groups else "Unknown"
                } for group_id in user.groups
            ]
        }
    
    async def get_community_stats(self) -> Dict[str, Any]:
        """Get overall community statistics."""
        total_users = len(self.users)
        active_challenges = len([c for c in self.challenges.values() if c.status == ChallengeStatus.ACTIVE])
        total_groups = len(self.groups)
        total_achievements = sum(len(achievements) for achievements in self.achievements.values())
        
        return {
            "total_users": total_users,
            "active_challenges": active_challenges,
            "total_groups": total_groups,
            "total_achievements": total_achievements,
            "total_portfolio_value": sum(u.portfolio_value for u in self.users.values()),
            "learning_content_count": len(self.learning_content),
            "forum_posts_count": len(self.forum_posts)
        }


# Demo usage
async def demo_community_features():
    """Demonstrate the community features system."""
    engine = CommunityEngine()
    
    print("🔄 Starting Community Features Demo...")
    
    # Register demo users
    users = []
    for i in range(5):
        user_data = {
            "username": f"trader_{i+1}",
            "email": f"trader{i+1}@example.com",
            "portfolio_value": 100000 + i * 50000
        }
        user = await engine.register_user(user_data)
        users.append(user)
    
    print(f"👥 Registered {len(users)} demo users")
    
    # Create a group
    group_data = {
        "name": "Beginner Investors",
        "description": "Group for new investors to learn together",
        "type": "PUBLIC",
        "max_members": 20
    }
    group = await engine.create_group(users[0].user_id, group_data)
    
    # Join users to group
    for user in users[1:3]:
        await engine.join_group(user.user_id, group.group_id)
    
    print(f"👥 Created group: {group.name} with {len(group.members)} members")
    
    # Create challenges
    challenge_data = {
        "title": "Weekly Performance Challenge",
        "description": "Achieve highest returns this week",
        "type": "PORTFOLIO_PERFORMANCE",
        "start_date": datetime.now().isoformat(),
        "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "prize_pool": 10000.0,
        "max_participants": 50
    }
    challenge = await engine.create_challenge(challenge_data)
    
    # Join users to challenge
    for user in users[:3]:
        await engine.join_challenge(user.user_id, challenge.challenge_id)
    
    print(f"🏆 Created challenge: {challenge.title} with {len(challenge.participants)} participants")
    
    # Create learning content
    content_data = {
        "title": "Introduction to Stock Analysis",
        "description": "Learn the basics of fundamental analysis",
        "type": "ARTICLE",
        "difficulty": "BEGINNER",
        "estimated_time": 15,
        "content": {"text": "Fundamental analysis involves..."},
        "tags": ["stocks", "analysis", "beginner"]
    }
    content = await engine.create_learning_content(content_data)
    
    # Complete learning content
    points = await engine.complete_learning_content(users[0].user_id, content.content_id, 5)
    print(f"📚 User completed learning content and earned {points} points")
    
    # Update leaderboards (simulate)
    await engine._update_leaderboards()
    
    # Get community stats
    stats = await engine.get_community_stats()
    print(f"\n📊 Community Stats:")
    print(f"  Total Users: {stats['total_users']}")
    print(f"  Active Challenges: {stats['active_challenges']}")
    print(f"  Total Groups: {stats['total_groups']}")
    print(f"  Total Achievements: {stats['total_achievements']}")
    
    # Get user dashboard
    dashboard = await engine.get_user_dashboard(users[0].user_id)
    print(f"\n👤 User Dashboard for {dashboard['user']['username']}:")
    print(f"  Level: {dashboard['user']['level']}")
    print(f"  Total Score: {dashboard['user']['total_score']}")
    print(f"  Active Challenges: {len(dashboard['active_challenges'])}")
    print(f"  Recent Achievements: {len(dashboard['recent_achievements'])}")
    
    print("✅ Community Features Demo Complete")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_community_features())