"""
AMT Staff Registry - Comprehensive management system for 25 championship professionals.
Handles tier-based coordination, expertise matching, availability tracking, and succession protocols.
Integrates with Airtable intelligence brain for real-time staff coordination.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict
import uuid


class TierLevel(Enum):
    """Hierarchical tier levels for staff organization."""
    FOUNDER = "founder"           # Tier 1: Supreme command
    AI_CORE = "ai_core"          # Tier 2: Digital intelligence
    EXECUTIVE = "executive"       # Tier 3: Executive command
    STRATEGIC = "strategic"       # Tier 4: Strategic leadership
    ADVISORY = "advisory"         # Tier 5: Senior advisory
    INNOVATION = "innovation"     # Tier 6: Innovation & technical
    FOOTBALL = "football"         # Tier 7: Football operations


class StaffStatus(Enum):
    """Current availability status of staff members."""
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    BUSY = "busy"
    OFFLINE = "offline"
    EMERGENCY_ONLY = "emergency_only"


class ExpertiseArea(Enum):
    """Specialized expertise areas for staff members."""
    # Strategic & Leadership
    STRATEGIC_VISION = "Strategic Vision"
    LEADERSHIP_EXCELLENCE = "Leadership Excellence"
    OPERATIONS_EXCELLENCE = "Operations Excellence"
    
    # Triangle Defense & Football
    TRIANGLE_DEFENSE_MASTERY = "Triangle Defense Mastery"
    TRIANGLE_DEFENSE_INNOVATION = "Triangle Defense Innovation"
    DEFENSIVE_ANALYSIS = "Defensive Analysis"
    FOOTBALL_ANALYTICS = "Football Analytics"
    PASS_RUSH_EXCELLENCE = "Pass Rush Excellence"
    
    # Technical & Innovation
    AI_DEVELOPMENT = "AI Development"
    STATISTICAL_INTELLIGENCE = "Statistical Intelligence"
    DEVOPS_EXCELLENCE = "DevOps Excellence"
    UX_UI_DESIGN = "UX/UI Design"
    ALGORITHM_OPTIMIZATION = "Algorithm Optimization"
    
    # Medical & Psychology
    SPORTS_MEDICINE = "Sports Medicine"
    MENTAL_PERFORMANCE = "Mental Performance"
    PLAYER_PSYCHOLOGY = "Player Psychology"
    
    # Security & Operations
    PHYSICAL_SECURITY = "Physical Security"
    DATA_PROTECTION = "Data Protection"
    RISK_MANAGEMENT = "Risk Management"
    
    # Communications & Development
    MEDIA_RELATIONS = "Media Relations"
    TALENT_DEVELOPMENT = "Talent Development"
    COACH_DEVELOPMENT = "Coach Development"
    
    # Analytics & Intelligence
    COMPETITIVE_INTELLIGENCE = "Competitive Intelligence"
    PREDICTIVE_ANALYTICS = "Predictive Analytics"
    PATTERN_RECOGNITION = "Pattern Recognition"


@dataclass
class StaffMember:
    """Complete profile for a championship professional."""
    staff_id: str
    full_name: str
    nickname: str
    role_title: str
    department: str
    tier_level: TierLevel
    
    # Authority and succession
    succession_role: str
    authority_level: str
    emergency_contact_priority: int
    
    # Skills and background
    background_education: str
    expertise_areas: List[ExpertiseArea]
    specializations: List[str] = field(default_factory=list)
    
    # Current status
    status: StaffStatus = StaffStatus.AVAILABLE
    current_assignment: Optional[str] = None
    workload_percentage: float = 0.0
    
    # Performance metrics
    effectiveness_rating: float = 95.0
    succession_readiness: float = 90.0
    leadership_effectiveness: float = 92.0
    team_collaboration_rating: float = 94.0
    
    # Availability tracking
    last_updated: datetime = field(default_factory=datetime.now)
    available_until: Optional[datetime] = None
    preferred_assignment_types: List[str] = field(default_factory=list)
    
    # Crisis and emergency capabilities
    crisis_function: str = ""
    emergency_response_capability: float = 90.0
    cross_functional_integration: float = 88.0
    
    # AI coordination
    has_ai_agent: bool = True
    agent_personality_config: Dict[str, Any] = field(default_factory=dict)
    
    def is_available_for_assignment(self) -> bool:
        """Check if staff member is available for new assignments."""
        return (
            self.status in [StaffStatus.AVAILABLE, StaffStatus.ASSIGNED] and
            self.workload_percentage < 90.0 and
            (self.available_until is None or self.available_until > datetime.now())
        )
    
    def can_handle_tier_requirement(self, required_tier: TierLevel) -> bool:
        """Check if staff member can handle requests at the required tier level."""
        tier_hierarchy = {
            TierLevel.FOUNDER: 7,
            TierLevel.AI_CORE: 6,
            TierLevel.EXECUTIVE: 5,
            TierLevel.STRATEGIC: 4,
            TierLevel.ADVISORY: 3,
            TierLevel.INNOVATION: 2,
            TierLevel.FOOTBALL: 1
        }
        
        return tier_hierarchy[self.tier_level] >= tier_hierarchy[required_tier]
    
    def get_expertise_match_score(self, required_expertise: List[str]) -> float:
        """Calculate how well this staff member matches required expertise."""
        if not required_expertise:
            return 1.0
        
        staff_expertise_names = [exp.value for exp in self.expertise_areas]
        matches = sum(1 for req in required_expertise if req in staff_expertise_names)
        
        return matches / len(required_expertise)


@dataclass
class AssignmentRecord:
    """Record of staff assignments for tracking and metrics."""
    assignment_id: str
    staff_id: str
    request_id: str
    assignment_type: str
    assigned_at: datetime
    estimated_duration_minutes: int
    actual_duration_minutes: Optional[int] = None
    completed_at: Optional[datetime] = None
    success_rating: Optional[float] = None
    notes: str = ""


@dataclass
class StaffUtilizationMetrics:
    """Utilization and performance metrics for staff members."""
    staff_id: str
    total_assignments: int = 0
    avg_assignment_duration: float = 0.0
    success_rate: float = 100.0
    utilization_percentage: float = 0.0
    peak_performance_hours: List[int] = field(default_factory=list)
    collaboration_partners: Dict[str, int] = field(default_factory=dict)
    expertise_usage_frequency: Dict[str, int] = field(default_factory=dict)


class StaffRegistry:
    """
    Comprehensive registry managing all 25 championship professionals.
    
    Provides expertise matching, availability tracking, tier-based coordination,
    and integration with Airtable intelligence brain for real-time staff management.
    """
    
    def __init__(self):
        """Initialize the staff registry with all championship professionals."""
        self.staff_members: Dict[str, StaffMember] = {}
        self.assignment_history: List[AssignmentRecord] = []
        self.active_assignments: Dict[str, AssignmentRecord] = {}
        self.utilization_metrics: Dict[str, StaffUtilizationMetrics] = {}
        
        # Tier organization for quick access
        self.staff_by_tier: Dict[TierLevel, List[str]] = defaultdict(list)
        self.staff_by_expertise: Dict[ExpertiseArea, List[str]] = defaultdict(list)
        
        # Emergency succession chains
        self.succession_chains: Dict[str, List[str]] = {}
        
        # Logger
        self.logger = logging.getLogger("AMT.StaffRegistry")
        self.logger.setLevel(logging.INFO)
        
        # Initialize all staff members
        self._initialize_championship_staff()
        
        self.logger.info("Staff Registry initialized with 25 championship professionals")
    
    def _initialize_championship_staff(self):
        """Initialize all 25 championship professionals with complete profiles."""
        
        # Tier 1: Founder Authority
        self._add_staff_member(StaffMember(
            staff_id="denauld-brown",
            full_name="Denauld Brown",
            nickname="The Mastermind",
            role_title="Founder, CEO & Defensive Coordinator",
            department="Executive Leadership",
            tier_level=TierLevel.FOUNDER,
            succession_role="Cannot be replaced (Founder status permanent)",
            authority_level="Maximum (System Creator)",
            emergency_contact_priority=1,
            background_education="All-American at Kutztown → NFL/NFL Europe → Division I DC → AI Innovation Pioneer",
            expertise_areas=[
                ExpertiseArea.TRIANGLE_DEFENSE_INNOVATION,
                ExpertiseArea.STRATEGIC_VISION,
                ExpertiseArea.LEADERSHIP_EXCELLENCE
            ],
            crisis_function="Ultimate authority and strategic guidance",
            effectiveness_rating=100.0,
            agent_personality_config={
                "leadership_style": "visionary_mastermind",
                "decision_authority": "supreme",
                "triangle_defense_mastery": "creator_level"
            }
        ))
        
        # Tier 2: AI Core
        self._add_staff_member(StaffMember(
            staff_id="mel-ai",
            full_name="M.E.L.",
            nickname="The Digital Twin",
            role_title="Master Intelligence Engine",
            department="AI Core",
            tier_level=TierLevel.AI_CORE,
            succession_role="Intelligence Operations Continuity",
            authority_level="Intelligence Distribution and Coordination",
            emergency_contact_priority=2,
            background_education="AI system embodying Denauld Brown's complete methodology",
            expertise_areas=[
                ExpertiseArea.TRIANGLE_DEFENSE_MASTERY,
                ExpertiseArea.AI_DEVELOPMENT,
                ExpertiseArea.STRATEGIC_VISION
            ],
            crisis_function="Maintains intelligence operations and coaching continuity",
            effectiveness_rating=99.0,
            agent_personality_config={
                "intelligence_type": "digital_twin",
                "processing_speed": "instantaneous",
                "knowledge_depth": "comprehensive"
            }
        ))
        
        # Tier 3: Executive Command
        self._add_staff_member(StaffMember(
            staff_id="courtney-sellars",
            full_name="Courtney Sellars",
            nickname="The Shield",
            role_title="CEO / Acting Chief Legal Officer",
            department="Legal Strategy",
            tier_level=TierLevel.EXECUTIVE,
            succession_role="Emergency Operational Command (Alexandra unavailable)",
            authority_level="Full Legal Autonomy with Override Power",
            emergency_contact_priority=2,
            background_education="Case Western (JD), Wake Forest (Psychology, Former Pharmaceutical Executive)",
            expertise_areas=[
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.STRATEGIC_VISION,
                ExpertiseArea.RISK_MANAGEMENT
            ],
            crisis_function="Legal protection and strategic legal intelligence"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="alexandra-martinez",
            full_name="Alexandra Martinez",
            nickname="The Coordinator",
            role_title="Chief Administrative Officer",
            department="Mission Control",
            tier_level=TierLevel.EXECUTIVE,
            succession_role="Emergency Operational Leadership (Victoria unavailable)",
            authority_level="Full Operational Autonomy with Emergency Command",
            emergency_contact_priority=3,
            background_education="Harvard MBA + Stanford Engineering Management",
            expertise_areas=[
                ExpertiseArea.OPERATIONS_EXCELLENCE,
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.STRATEGIC_VISION
            ],
            crisis_function="Emergency operational leadership and mission control"
        ))
        
        # Tier 4: Strategic Leadership
        self._add_staff_member(StaffMember(
            staff_id="marcus-sterling",
            full_name="Marcus Sterling",
            nickname="The Architect",
            role_title="General Manager",
            department="Strategic Operations",
            tier_level=TierLevel.STRATEGIC,
            succession_role="Emergency CEO (Tier 3 unavailable)",
            authority_level="Strategic Operations and Personnel Decisions",
            emergency_contact_priority=5,
            background_education="Stanford MBA + MIT Systems Engineering, Former NFL linebacker",
            expertise_areas=[
                ExpertiseArea.STRATEGIC_VISION,
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.OPERATIONS_EXCELLENCE
            ],
            crisis_function="Business continuity leadership and emergency CEO authority"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="darius-washington",
            full_name="Darius Washington",
            nickname="The Virtuoso",
            role_title="Head Coach",
            department="Football Operations",
            tier_level=TierLevel.STRATEGIC,
            succession_role="Chief Operating Officer (Nuclear Protocol)",
            authority_level="Football Operations and Player Development",
            emergency_contact_priority=6,
            background_education="Harvard Psychology + Northwestern Kellogg, Former college quarterback",
            expertise_areas=[
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.FOOTBALL_ANALYTICS,
                ExpertiseArea.PLAYER_PSYCHOLOGY
            ],
            crisis_function="Operational execution leadership and football continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="dr-james-wright",
            full_name="Dr. James Wright",
            nickname="The Algorithm",
            role_title="Chief Data Officer",
            department="Technology Strategy",
            tier_level=TierLevel.STRATEGIC,
            succession_role="Chief Technology Officer (Nuclear Protocol)",
            authority_level="Technology Strategy and Data Analytics",
            emergency_contact_priority=7,
            background_education="MIT PhD Data Science + Stanford Statistics Masters",
            expertise_areas=[
                ExpertiseArea.STATISTICAL_INTELLIGENCE,
                ExpertiseArea.PREDICTIVE_ANALYTICS,
                ExpertiseArea.AI_DEVELOPMENT
            ],
            crisis_function="Technology operations continuity and data protection"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="dr-sarah-chen",
            full_name="Dr. Sarah Chen",
            nickname="The Healer",
            role_title="Chief Medical Officer",
            department="Health Operations",
            tier_level=TierLevel.STRATEGIC,
            succession_role="Chief Health & Safety Officer (Nuclear Protocol)",
            authority_level="Medical Operations and Safety Protocols",
            emergency_contact_priority=8,
            background_education="Stanford Medical School + Sports Medicine Fellowship",
            expertise_areas=[
                ExpertiseArea.SPORTS_MEDICINE,
                ExpertiseArea.PLAYER_PSYCHOLOGY,
                ExpertiseArea.RISK_MANAGEMENT
            ],
            crisis_function="Health and safety continuity and medical emergency response"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="captain-rodriguez",
            full_name="Captain Michael Rodriguez",
            nickname="The Fortress",
            role_title="Chief Security Officer",
            department="Security Operations",
            tier_level=TierLevel.STRATEGIC,
            succession_role="Chief Risk Management Officer (Nuclear Protocol)",
            authority_level="Security and Risk Management",
            emergency_contact_priority=9,
            background_education="Military Leadership Academy + Cybersecurity Certification",
            expertise_areas=[
                ExpertiseArea.PHYSICAL_SECURITY,
                ExpertiseArea.DATA_PROTECTION,
                ExpertiseArea.RISK_MANAGEMENT
            ],
            crisis_function="Security and risk management continuity"
        ))
        
        # Tier 5: Senior Advisory & Communications
        self._add_staff_member(StaffMember(
            staff_id="bill-mckenzie",
            full_name="Bill McKenzie",
            nickname="The Professor",
            role_title="Senior Advisor",
            department="Advisory Leadership",
            tier_level=TierLevel.ADVISORY,
            succession_role="Senior Strategic Advisor (Nuclear Protocol)",
            authority_level="Strategic Advisory and Mentorship",
            emergency_contact_priority=10,
            background_education="30+ years coaching experience with analytical expertise",
            expertise_areas=[
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.COACH_DEVELOPMENT,
                ExpertiseArea.FOOTBALL_ANALYTICS
            ],
            crisis_function="Strategic guidance and organizational stability"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="patricia-williams",
            full_name="Patricia Williams",
            nickname="The Developer",
            role_title="Career Development Specialist",
            department="Human Capital",
            tier_level=TierLevel.ADVISORY,
            succession_role="Chief Human Resources Officer (Nuclear Protocol)",
            authority_level="Human Capital Development and Career Pathways",
            emergency_contact_priority=11,
            background_education="Human Resources Leadership + Career Development Expertise",
            expertise_areas=[
                ExpertiseArea.TALENT_DEVELOPMENT,
                ExpertiseArea.LEADERSHIP_EXCELLENCE,
                ExpertiseArea.OPERATIONS_EXCELLENCE
            ],
            crisis_function="Personnel operations and staff welfare continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="elena-vasquez",
            full_name="Elena Vasquez",
            nickname="The Voice",
            role_title="Chief Communications Officer",
            department="Communications Strategy",
            tier_level=TierLevel.ADVISORY,
            succession_role="Chief External Relations Officer (Nuclear Protocol)",
            authority_level="Media Relations and Brand Strategy",
            emergency_contact_priority=12,
            background_education="Communications Leadership + Public Relations Expertise",
            expertise_areas=[
                ExpertiseArea.MEDIA_RELATIONS,
                ExpertiseArea.STRATEGIC_VISION,
                ExpertiseArea.OPERATIONS_EXCELLENCE
            ],
            crisis_function="External communications and reputation management"
        ))
        
        # Tier 6: Innovation & Technical Operations
        self._add_staff_member(StaffMember(
            staff_id="david-kim",
            full_name="Professor David Kim",
            nickname="The Architect",
            role_title="Chief Innovation Officer",
            department="Innovation Strategy",
            tier_level=TierLevel.INNOVATION,
            succession_role="Innovation Continuity Director",
            authority_level="R&D Strategy and Future Technology",
            emergency_contact_priority=13,
            background_education="PhD Engineering + Innovation Management",
            expertise_areas=[
                ExpertiseArea.STRATEGIC_VISION,
                ExpertiseArea.COMPETITIVE_INTELLIGENCE,
                ExpertiseArea.AI_DEVELOPMENT
            ],
            crisis_function="Innovation pipeline and competitive advantage maintenance"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="rachel-foster",
            full_name="Dr. Rachel Foster",
            nickname="The Algorithm",
            role_title="Senior AI Research Scientist",
            department="AI Research",
            tier_level=TierLevel.INNOVATION,
            succession_role="Acting Chief Technology Officer (Technical Crisis)",
            authority_level="AI Development and Machine Learning",
            emergency_contact_priority=14,
            background_education="PhD Computer Science + AI Research Expertise",
            expertise_areas=[
                ExpertiseArea.AI_DEVELOPMENT,
                ExpertiseArea.ALGORITHM_OPTIMIZATION,
                ExpertiseArea.PREDICTIVE_ANALYTICS
            ],
            crisis_function="AI system continuity and technical innovation"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="jake-morrison",
            full_name="Jake Morrison",
            nickname="The Pipeline",
            role_title="Senior DevOps Engineer",
            department="Infrastructure Operations",
            tier_level=TierLevel.INNOVATION,
            succession_role="Infrastructure Operations Director",
            authority_level="System Architecture and Cloud Operations",
            emergency_contact_priority=15,
            background_education="Engineering Leadership + Cloud Architecture Expertise",
            expertise_areas=[
                ExpertiseArea.DEVOPS_EXCELLENCE,
                ExpertiseArea.DATA_PROTECTION,
                ExpertiseArea.OPERATIONS_EXCELLENCE
            ],
            crisis_function="Technical infrastructure and system reliability continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="maya-patel",
            full_name="Maya Patel",
            nickname="The Interface",
            role_title="Senior UX/UI Designer",
            department="User Experience",
            tier_level=TierLevel.INNOVATION,
            succession_role="User Experience Continuity Director",
            authority_level="Design Systems and User Experience",
            emergency_contact_priority=16,
            background_education="Design Leadership + User Experience Expertise",
            expertise_areas=[
                ExpertiseArea.UX_UI_DESIGN,
                ExpertiseArea.OPERATIONS_EXCELLENCE,
                ExpertiseArea.COMPETITIVE_INTELLIGENCE
            ],
            crisis_function="User experience and platform usability continuity"
        ))
        
        # Tier 7: Football Operations & Analytics
        self._add_staff_member(StaffMember(
            staff_id="tony-rivera",
            full_name="Tony Rivera",
            nickname="The Triangle Specialist",
            role_title="Defensive Analyst (Triangle Defense Specialist)",
            department="Football Analytics",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Acting Defensive Coordinator",
            authority_level="Triangle Defense Implementation and Defensive Analysis",
            emergency_contact_priority=17,
            background_education="Football Analytics + Triangle Defense Expertise",
            expertise_areas=[
                ExpertiseArea.TRIANGLE_DEFENSE_MASTERY,
                ExpertiseArea.DEFENSIVE_ANALYSIS,
                ExpertiseArea.FOOTBALL_ANALYTICS
            ],
            crisis_function="Defensive operations continuity and Triangle Defense preservation"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="derek-thompson",
            full_name="Derek Thompson",
            nickname="The Pressure Specialist",
            role_title="Pass Rush Analyst (Pressure Warfare)",
            department="Football Analytics",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Pass Rush Operations Director",
            authority_level="Pass Rush Coordination and Pressure Analysis",
            emergency_contact_priority=18,
            background_education="Athletic Performance + Competitive Intelligence",
            expertise_areas=[
                ExpertiseArea.PASS_RUSH_EXCELLENCE,
                ExpertiseArea.COMPETITIVE_INTELLIGENCE,
                ExpertiseArea.FOOTBALL_ANALYTICS
            ],
            crisis_function="Pressure warfare continuity and pass rush operations"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="marcus-johnson",
            full_name="Dr. Marcus Johnson",
            nickname="The Mind",
            role_title="Sports Psychology Director",
            department="Player Development",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Mental Performance Continuity Director",
            authority_level="Mental Performance and Psychological Assessment",
            emergency_contact_priority=19,
            background_education="PhD Sports Psychology + Performance Optimization",
            expertise_areas=[
                ExpertiseArea.MENTAL_PERFORMANCE,
                ExpertiseArea.PLAYER_PSYCHOLOGY,
                ExpertiseArea.TALENT_DEVELOPMENT
            ],
            crisis_function="Player mental health and performance continuity"
        ))
        
        # Continue with remaining football staff...
        self._add_staff_member(StaffMember(
            staff_id="amanda-thompson",
            full_name="Coach Amanda Thompson",
            nickname="The Mentor",
            role_title="Director of Coach Development",
            department="Coach Development",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Coaching Education Continuity Director",
            authority_level="Coach Training and Certification Development",
            emergency_contact_priority=20,
            background_education="Coaching Excellence + Educational Leadership",
            expertise_areas=[
                ExpertiseArea.COACH_DEVELOPMENT,
                ExpertiseArea.TALENT_DEVELOPMENT,
                ExpertiseArea.LEADERSHIP_EXCELLENCE
            ],
            crisis_function="Coach development and education continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="roberto-gutierrez",
            full_name="Roberto Gutierrez",
            nickname="The Scout",
            role_title="Director of Player Personnel",
            department="Scouting Operations",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Scouting Operations Director",
            authority_level="Player Evaluation and Talent Identification",
            emergency_contact_priority=21,
            background_education="Scouting Excellence + Personnel Evaluation",
            expertise_areas=[
                ExpertiseArea.COMPETITIVE_INTELLIGENCE,
                ExpertiseArea.TALENT_DEVELOPMENT,
                ExpertiseArea.FOOTBALL_ANALYTICS
            ],
            crisis_function="Player personnel and scouting continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="sam-williams",
            full_name="Sam Williams",
            nickname="The Teacher",
            role_title="Offensive Analyst (Teaching Excellence)",
            department="Football Analytics",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Offensive Analysis Director",
            authority_level="Offensive Analysis and Educational Methodology",
            emergency_contact_priority=22,
            background_education="Football Analytics + Teaching Excellence",
            expertise_areas=[
                ExpertiseArea.FOOTBALL_ANALYTICS,
                ExpertiseArea.COACH_DEVELOPMENT,
                ExpertiseArea.TALENT_DEVELOPMENT
            ],
            crisis_function="Offensive intelligence continuity and educational leadership"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="alex-chen",
            full_name="Alex Chen",
            nickname="The Optimizer",
            role_title="Special Teams Analyst (Statistical Optimization)",
            department="Football Analytics",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Statistical Analysis Director",
            authority_level="Statistical Analysis and Special Teams Optimization",
            emergency_contact_priority=23,
            background_education="Statistics + Football Analytics Expertise",
            expertise_areas=[
                ExpertiseArea.STATISTICAL_INTELLIGENCE,
                ExpertiseArea.FOOTBALL_ANALYTICS,
                ExpertiseArea.PREDICTIVE_ANALYTICS
            ],
            crisis_function="Analytics and metrics continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="marcus-lewis",
            full_name="Marcus Lewis",
            nickname="The Coordinator",
            role_title="Head Analytics Coordinator",
            department="Football Analytics",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Analytics Operations Director",
            authority_level="Analytics Team Coordination and Data Integration",
            emergency_contact_priority=24,
            background_education="Football Analytics Leadership + Team Coordination",
            expertise_areas=[
                ExpertiseArea.FOOTBALL_ANALYTICS,
                ExpertiseArea.OPERATIONS_EXCELLENCE,
                ExpertiseArea.LEADERSHIP_EXCELLENCE
            ],
            crisis_function="Analytics coordination and data continuity"
        ))
        
        self._add_staff_member(StaffMember(
            staff_id="michael-rodriguez",
            full_name="Michael Rodriguez",
            nickname="The Wall",
            role_title="Defensive Coordinator",
            department="Football Operations",
            tier_level=TierLevel.FOOTBALL,
            succession_role="Field Operations Director",
            authority_level="Defensive Operations and Triangle Defense Implementation",
            emergency_contact_priority=25,
            background_education="15 years defensive coordination + Triangle Defense specialization",
            expertise_areas=[
                ExpertiseArea.TRIANGLE_DEFENSE_MASTERY,
                ExpertiseArea.DEFENSIVE_ANALYSIS,
                ExpertiseArea.LEADERSHIP_EXCELLENCE
            ],
            crisis_function="On-field defensive execution and Triangle Defense application"
        ))
    
    def _add_staff_member(self, staff: StaffMember):
        """Add a staff member to the registry and update indices."""
        self.staff_members[staff.staff_id] = staff
        self.staff_by_tier[staff.tier_level].append(staff.staff_id)
        
        for expertise in staff.expertise_areas:
            self.staff_by_expertise[expertise].append(staff.staff_id)
        
        # Initialize utilization metrics
        self.utilization_metrics[staff.staff_id] = StaffUtilizationMetrics(
            staff_id=staff.staff_id
        )
    
    async def get_staff_member(self, staff_id: str) -> Optional[StaffMember]:
        """Retrieve a staff member by ID."""
        return self.staff_members.get(staff_id)
    
    async def get_available_staff(self,
                                tier_level: Optional[TierLevel] = None,
                                expertise_areas: Optional[List[str]] = None,
                                exclude_staff: Optional[List[str]] = None) -> List[StaffMember]:
        """
        Get available staff members matching criteria.
        
        Args:
            tier_level: Minimum tier level required
            expertise_areas: Required expertise areas
            exclude_staff: Staff IDs to exclude
            
        Returns:
            List of available staff members matching criteria
        """
        available_staff = []
        exclude_staff = exclude_staff or []
        
        for staff_id, staff in self.staff_members.items():
            if staff_id in exclude_staff:
                continue
            
            if not staff.is_available_for_assignment():
                continue
            
            # Check tier level requirement
            if tier_level and not staff.can_handle_tier_requirement(tier_level):
                continue
            
            # Check expertise requirements
            if expertise_areas:
                expertise_score = staff.get_expertise_match_score(expertise_areas)
                if expertise_score < 0.5:  # Minimum 50% expertise match
                    continue
            
            available_staff.append(staff)
        
        # Sort by effectiveness rating and availability
        available_staff.sort(
            key=lambda s: (s.effectiveness_rating, -s.workload_percentage),
            reverse=True
        )
        
        return available_staff
    
    async def assign_staff_to_request(self,
                                    staff_id: str,
                                    request_id: str,
                                    assignment_type: str,
                                    estimated_duration_minutes: int) -> bool:
        """
        Assign a staff member to a request.
        
        Args:
            staff_id: ID of staff member to assign
            request_id: ID of the request
            assignment_type: Type of assignment
            estimated_duration_minutes: Estimated duration
            
        Returns:
            True if assignment successful, False otherwise
        """
        staff = self.staff_members.get(staff_id)
        if not staff or not staff.is_available_for_assignment():
            return False
        
        # Create assignment record
        assignment = AssignmentRecord(
            assignment_id=str(uuid.uuid4()),
            staff_id=staff_id,
            request_id=request_id,
            assignment_type=assignment_type,
            assigned_at=datetime.now(),
            estimated_duration_minutes=estimated_duration_minutes
        )
        
        # Update staff status
        staff.status = StaffStatus.ASSIGNED
        staff.current_assignment = request_id
        
        # Calculate new workload (simplified estimation)
        current_workload_minutes = staff.workload_percentage * 8 * 60 / 100  # Convert to minutes
        new_workload_minutes = current_workload_minutes + estimated_duration_minutes
        staff.workload_percentage = min(100.0, (new_workload_minutes / (8 * 60)) * 100)
        
        staff.last_updated = datetime.now()
        
        # Store assignment
        self.active_assignments[assignment.assignment_id] = assignment
        
        self.logger.info(f"Assigned {staff.full_name} to request {request_id}")
        return True
    
    async def complete_assignment(self,
                                assignment_id: str,
                                success_rating: float,
                                notes: str = "") -> bool:
        """
        Complete an assignment and update metrics.
        
        Args:
            assignment_id: ID of the assignment to complete
            success_rating: Success rating (0.0 - 1.0)
            notes: Optional notes about the assignment
            
        Returns:
            True if completion successful, False otherwise
        """
        assignment = self.active_assignments.get(assignment_id)
        if not assignment:
            return False
        
        # Update assignment record
        assignment.completed_at = datetime.now()
        assignment.success_rating = success_rating
        assignment.notes = notes
        assignment.actual_duration_minutes = int(
            (assignment.completed_at - assignment.assigned_at).total_seconds() / 60
        )
        
        # Update staff member
        staff = self.staff_members.get(assignment.staff_id)
        if staff:
            staff.status = StaffStatus.AVAILABLE
            staff.current_assignment = None
            
            # Reduce workload
            completed_workload = (assignment.actual_duration_minutes / (8 * 60)) * 100
            staff.workload_percentage = max(0.0, staff.workload_percentage - completed_workload)
            
            staff.last_updated = datetime.now()
        
        # Update utilization metrics
        metrics = self.utilization_metrics.get(assignment.staff_id)
        if metrics:
            metrics.total_assignments += 1
            
            # Update average duration
            total_duration = (metrics.avg_assignment_duration * (metrics.total_assignments - 1) + 
                            assignment.actual_duration_minutes)
            metrics.avg_assignment_duration = total_duration / metrics.total_assignments
            
            # Update success rate
            total_success = (metrics.success_rate * (metrics.total_assignments - 1) + 
                           success_rating * 100)
            metrics.success_rate = total_success / metrics.total_assignments
        
        # Move to history
        self.assignment_history.append(assignment)
        del self.active_assignments[assignment_id]
        
        self.logger.info(f"Completed assignment {assignment_id} with rating {success_rating}")
        return True
    
    async def get_staff_by_tier(self, tier_level: TierLevel) -> List[StaffMember]:
        """Get all staff members at a specific tier level."""
        staff_ids = self.staff_by_tier.get(tier_level, [])
        return [self.staff_members[staff_id] for staff_id in staff_ids]
    
    async def get_staff_by_expertise(self, expertise: ExpertiseArea) -> List[StaffMember]:
        """Get all staff members with specific expertise."""
        staff_ids = self.staff_by_expertise.get(expertise, [])
        return [self.staff_members[staff_id] for staff_id in staff_ids]
    
    async def get_succession_chain(self, staff_id: str) -> List[StaffMember]:
        """Get succession chain for a staff member in case of unavailability."""
        staff = self.staff_members.get(staff_id)
        if not staff:
            return []
        
        # Find staff members with similar expertise and higher availability
        similar_staff = []
        
        for other_staff in self.staff_members.values():
            if other_staff.staff_id == staff_id:
                continue
            
            # Check if they have overlapping expertise
            expertise_overlap = set(staff.expertise_areas) & set(other_staff.expertise_areas)
            if expertise_overlap and other_staff.is_available_for_assignment():
                similarity_score = len(expertise_overlap) / len(staff.expertise_areas)
                similar_staff.append((other_staff, similarity_score))
        
        # Sort by similarity and effectiveness
        similar_staff.sort(key=lambda x: (x[1], x[0].effectiveness_rating), reverse=True)
        
        return [staff for staff, _ in similar_staff[:3]]  # Top 3 succession candidates
    
    async def get_staff_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary of all staff."""
        status_counts = defaultdict(int)
        tier_utilization = defaultdict(list)
        
        for staff in self.staff_members.values():
            status_counts[staff.status.value] += 1
            tier_utilization[staff.tier_level.value].append(staff.workload_percentage)
        
        # Calculate average utilization by tier
        avg_tier_utilization = {}
        for tier, utilizations in tier_utilization.items():
            avg_tier_utilization[tier] = sum(utilizations) / len(utilizations)
        
        return {
            "total_staff": len(self.staff_members),
            "status_breakdown": dict(status_counts),
            "tier_utilization": avg_tier_utilization,
            "active_assignments": len(self.active_assignments),
            "avg_effectiveness": sum(s.effectiveness_rating for s in self.staff_members.values()) / len(self.staff_members),
            "high_performers": len([s for s in self.staff_members.values() if s.effectiveness_rating >= 95.0])
        }
    
    async def get_staff_recommendations(self,
                                     required_expertise: List[str],
                                     tier_preference: Optional[TierLevel] = None,
                                     max_recommendations: int = 3) -> List[Tuple[StaffMember, float]]:
        """
        Get staff recommendations with match scores.
        
        Args:
            required_expertise: Required expertise areas
            tier_preference: Preferred tier level
            max_recommendations: Maximum number of recommendations
            
        Returns:
            List of (staff_member, match_score) tuples
        """
        recommendations = []
        
        for staff in self.staff_members.values():
            if not staff.is_available_for_assignment():
                continue
            
            # Calculate comprehensive match score
            expertise_score = staff.get_expertise_match_score(required_expertise)
            effectiveness_score = staff.effectiveness_rating / 100.0
            availability_score = 1.0 - (staff.workload_percentage / 100.0)
            
            # Tier preference bonus
            tier_bonus = 0.0
            if tier_preference and staff.tier_level == tier_preference:
                tier_bonus = 0.1
            
            total_score = (expertise_score * 0.4 + 
                          effectiveness_score * 0.3 + 
                          availability_score * 0.2 + 
                          tier_bonus * 0.1)
            
            recommendations.append((staff, total_score))
        
        # Sort by match score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:max_recommendations]
    
    async def update_staff_from_airtable(self, staff_updates: List[Dict[str, Any]]):
        """Update staff information from Airtable synchronization."""
        for update in staff_updates:
            staff_id = update.get("staff_id")
            staff = self.staff_members.get(staff_id)
            
            if staff:
                # Update specific fields that can change
                if "status" in update:
                    staff.status = StaffStatus(update["status"])
                if "workload_percentage" in update:
                    staff.workload_percentage = update["workload_percentage"]
                if "effectiveness_rating" in update:
                    staff.effectiveness_rating = update["effectiveness_rating"]
                
                staff.last_updated = datetime.now()
                
                self.logger.info(f"Updated staff {staff.full_name} from Airtable sync")
    
    def get_registry_metrics(self) -> Dict[str, Any]:
        """Get comprehensive registry metrics."""
        return {
            "total_staff": len(self.staff_members),
            "staff_by_tier": {tier.value: len(staff_ids) for tier, staff_ids in self.staff_by_tier.items()},
            "expertise_coverage": {exp.value: len(staff_ids) for exp, staff_ids in self.staff_by_expertise.items()},
            "active_assignments": len(self.active_assignments),
            "total_assignments_completed": len(self.assignment_history),
            "avg_staff_effectiveness": sum(s.effectiveness_rating for s in self.staff_members.values()) / len(self.staff_members)
        }
