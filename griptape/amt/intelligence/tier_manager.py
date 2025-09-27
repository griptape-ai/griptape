"""
AMT Tier Manager - Advanced tier-based task complexity assessment and staff selection.
Implements sophisticated algorithms for optimal staff allocation across 7 organizational tiers
with urgency classification, escalation protocols, and championship-level decision optimization.
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics
from collections import defaultdict, Counter

# Import from staff registry
from .staff_registry import StaffMember, TierLevel, ExpertiseArea, StaffStatus


class TaskComplexity(Enum):
    """Task complexity levels for intelligent routing."""
    SIMPLE = "simple"           # Routine operations, single-source data
    STANDARD = "standard"       # Normal coordination, moderate analysis
    COMPLEX = "complex"         # Multi-source analysis, cross-functional
    ADVANCED = "advanced"       # Strategic decisions, predictive modeling
    CRITICAL = "critical"       # Crisis management, company-wide impact
    STRATEGIC = "strategic"     # Empire-level decisions, long-term planning
    NUCLEAR = "nuclear"         # Emergency protocols, succession activation


class UrgencyLevel(Enum):
    """Request urgency classification."""
    LOW = "low"                 # 24+ hours acceptable
    MEDIUM = "medium"           # 4-8 hours target
    HIGH = "high"               # 1-2 hours required
    CRITICAL = "critical"       # 30 minutes maximum
    EMERGENCY = "emergency"     # Immediate response required


class DecisionScope(Enum):
    """Scope of decision-making authority required."""
    OPERATIONAL = "operational"      # Day-to-day operations
    DEPARTMENTAL = "departmental"    # Department-level decisions
    COMPANY = "company"              # Single company decisions
    CROSS_COMPANY = "cross_company"  # Multi-company coordination
    EMPIRE = "empire"                # Empire-wide strategic decisions
    FOUNDER = "founder"              # Founder-level authority required


class EscalationTrigger(Enum):
    """Triggers for automatic escalation."""
    TIME_EXCEEDED = "time_exceeded"
    COMPLEXITY_INCREASE = "complexity_increase"
    STAFF_UNAVAILABLE = "staff_unavailable"
    QUALITY_CONCERN = "quality_concern"
    STRATEGIC_IMPACT = "strategic_impact"
    EMERGENCY_DECLARED = "emergency_declared"


@dataclass
class ComplexityAssessment:
    """Comprehensive task complexity assessment results."""
    complexity_level: TaskComplexity
    complexity_score: float  # 0-100 scale
    contributing_factors: Dict[str, float]
    estimated_duration_minutes: int
    required_tier_level: TierLevel
    decision_scope: DecisionScope
    expertise_requirements: List[ExpertiseArea]
    data_sources_needed: List[str]
    collaboration_requirement: bool
    assessment_confidence: float  # 0-1 scale
    special_considerations: List[str] = field(default_factory=list)


@dataclass
class UrgencyAssessment:
    """Urgency classification with timing requirements."""
    urgency_level: UrgencyLevel
    urgency_score: float  # 0-100 scale
    max_response_time_minutes: int
    escalation_threshold_minutes: int
    priority_factors: Dict[str, float]
    deadline_impact: str
    assessment_reasoning: str


@dataclass
class StaffSelectionCriteria:
    """Criteria for optimal staff selection."""
    required_tier: TierLevel
    preferred_tier: Optional[TierLevel] = None
    required_expertise: List[ExpertiseArea] = field(default_factory=list)
    preferred_expertise: List[ExpertiseArea] = field(default_factory=list)
    max_workload_percentage: float = 85.0
    min_effectiveness_rating: float = 80.0
    exclude_staff_ids: List[str] = field(default_factory=list)
    collaboration_requirements: List[str] = field(default_factory=list)
    succession_fallback: bool = True


@dataclass
class StaffSelectionResult:
    """Results of staff selection optimization."""
    primary_staff: StaffMember
    supporting_staff: List[StaffMember]
    selection_score: float
    confidence_level: float
    alternative_options: List[Tuple[StaffMember, float]]
    selection_reasoning: str
    estimated_capacity_utilization: float
    projected_success_probability: float


@dataclass
class EscalationProtocol:
    """Escalation protocol definition."""
    trigger: EscalationTrigger
    from_tier: TierLevel
    to_tier: TierLevel
    conditions: Dict[str, Any]
    notification_required: bool
    approval_required: bool
    emergency_override: bool


class TierManager:
    """
    Advanced tier management system for optimal task routing and staff selection.
    
    Implements sophisticated algorithms for:
    - Task complexity assessment with multi-factor analysis
    - Urgency classification with timing optimization
    - Optimal staff selection across organizational tiers
    - Automated escalation protocols
    - Performance optimization and learning
    """
    
    def __init__(self):
        """Initialize the tier management system with optimization algorithms."""
        
        # Complexity assessment weights
        self.complexity_weights = {
            "data_sources": 15,      # Number of data sources required
            "cross_functional": 20,   # Cross-functional coordination needed
            "time_sensitivity": 10,   # Time pressure factor
            "decision_impact": 25,    # Scope of decision impact
            "technical_depth": 15,    # Technical complexity required
            "stakeholder_count": 10,  # Number of stakeholders involved
            "risk_level": 5          # Associated risk level
        }
        
        # Urgency classification matrix
        self.urgency_matrix = {
            UrgencyLevel.LOW: {"max_response": 1440, "escalation": 2880},      # 24h, 48h
            UrgencyLevel.MEDIUM: {"max_response": 240, "escalation": 480},     # 4h, 8h
            UrgencyLevel.HIGH: {"max_response": 60, "escalation": 120},        # 1h, 2h
            UrgencyLevel.CRITICAL: {"max_response": 15, "escalation": 30},     # 15min, 30min
            UrgencyLevel.EMERGENCY: {"max_response": 5, "escalation": 10}      # 5min, 10min
        }
        
        # Tier capability matrix
        self.tier_capabilities = {
            TierLevel.FOUNDER: {
                "max_complexity": 100,
                "decision_scopes": [DecisionScope.FOUNDER, DecisionScope.EMPIRE],
                "authority_level": 10,
                "specializations": ["Strategic Vision", "Triangle Defense Innovation"]
            },
            TierLevel.AI_CORE: {
                "max_complexity": 95,
                "decision_scopes": [DecisionScope.EMPIRE, DecisionScope.CROSS_COMPANY],
                "authority_level": 9,
                "specializations": ["AI Development", "Intelligence Coordination"]
            },
            TierLevel.EXECUTIVE: {
                "max_complexity": 85,
                "decision_scopes": [DecisionScope.CROSS_COMPANY, DecisionScope.COMPANY],
                "authority_level": 8,
                "specializations": ["Leadership Excellence", "Operations Excellence"]
            },
            TierLevel.STRATEGIC: {
                "max_complexity": 75,
                "decision_scopes": [DecisionScope.COMPANY, DecisionScope.DEPARTMENTAL],
                "authority_level": 7,
                "specializations": ["Strategic Planning", "Technical Leadership"]
            },
            TierLevel.ADVISORY: {
                "max_complexity": 65,
                "decision_scopes": [DecisionScope.DEPARTMENTAL, DecisionScope.OPERATIONAL],
                "authority_level": 6,
                "specializations": ["Advisory Guidance", "Communications"]
            },
            TierLevel.INNOVATION: {
                "max_complexity": 60,
                "decision_scopes": [DecisionScope.DEPARTMENTAL, DecisionScope.OPERATIONAL],
                "authority_level": 5,
                "specializations": ["Technical Innovation", "Research & Development"]
            },
            TierLevel.FOOTBALL: {
                "max_complexity": 55,
                "decision_scopes": [DecisionScope.OPERATIONAL],
                "authority_level": 4,
                "specializations": ["Football Operations", "Analytics"]
            }
        }
        
        # Escalation protocols
        self.escalation_protocols = self._initialize_escalation_protocols()
        
        # Performance tracking
        self.selection_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            "successful_selections": 0,
            "escalations_triggered": 0,
            "avg_selection_accuracy": 0.0,
            "tier_utilization": defaultdict(int),
            "complexity_distribution": defaultdict(int)
        }
        
        # Logger
        self.logger = logging.getLogger("AMT.TierManager")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Tier Manager initialized with advanced selection algorithms")
    
    def assess_task_complexity(self, 
                              request_content: str,
                              request_context: Dict[str, Any],
                              urgency_indicators: List[str] = None) -> ComplexityAssessment:
        """
        Perform comprehensive task complexity assessment.
        
        Args:
            request_content: Content of the request
            request_context: Additional context information
            urgency_indicators: Indicators of urgency
            
        Returns:
            Comprehensive complexity assessment
        """
        urgency_indicators = urgency_indicators or []
        
        # Initialize scoring factors
        factors = {
            "data_sources": self._assess_data_source_complexity(request_context),
            "cross_functional": self._assess_cross_functional_needs(request_content, request_context),
            "time_sensitivity": self._assess_time_sensitivity(urgency_indicators, request_context),
            "decision_impact": self._assess_decision_impact(request_content, request_context),
            "technical_depth": self._assess_technical_complexity(request_content),
            "stakeholder_count": self._assess_stakeholder_complexity(request_context),
            "risk_level": self._assess_risk_level(request_content, request_context)
        }
        
        # Calculate weighted complexity score
        complexity_score = sum(
            factors[factor] * (self.complexity_weights[factor] / 100)
            for factor in factors
        )
        
        # Determine complexity level
        complexity_level = self._score_to_complexity_level(complexity_score)
        
        # Determine required tier
        required_tier = self._complexity_to_tier(complexity_level, factors)
        
        # Determine decision scope
        decision_scope = self._determine_decision_scope(request_context, factors)
        
        # Extract expertise requirements
        expertise_requirements = self._extract_expertise_requirements(
            request_content, request_context, complexity_level
        )
        
        # Estimate duration
        estimated_duration = self._estimate_task_duration(complexity_level, factors)
        
        # Assess collaboration needs
        collaboration_requirement = self._assess_collaboration_needs(factors, complexity_level)
        
        # Calculate assessment confidence
        assessment_confidence = self._calculate_assessment_confidence(factors, request_context)
        
        # Generate special considerations
        special_considerations = self._generate_special_considerations(
            factors, complexity_level, request_context
        )
        
        return ComplexityAssessment(
            complexity_level=complexity_level,
            complexity_score=complexity_score,
            contributing_factors=factors,
            estimated_duration_minutes=estimated_duration,
            required_tier_level=required_tier,
            decision_scope=decision_scope,
            expertise_requirements=expertise_requirements,
            data_sources_needed=self._identify_data_sources(request_context),
            collaboration_requirement=collaboration_requirement,
            assessment_confidence=assessment_confidence,
            special_considerations=special_considerations
        )
    
    def assess_urgency(self,
                      deadline: Optional[datetime] = None,
                      priority_indicators: List[str] = None,
                      business_impact: str = "",
                      request_context: Dict[str, Any] = None) -> UrgencyAssessment:
        """
        Assess urgency level with sophisticated timing analysis.
        
        Args:
            deadline: Explicit deadline if provided
            priority_indicators: List of urgency indicators
            business_impact: Description of business impact
            request_context: Additional context for urgency assessment
            
        Returns:
            Comprehensive urgency assessment
        """
        priority_indicators = priority_indicators or []
        request_context = request_context or {}
        
        # Calculate urgency factors
        urgency_factors = {
            "deadline_pressure": self._assess_deadline_pressure(deadline),
            "business_impact": self._assess_business_impact_urgency(business_impact),
            "keyword_indicators": self._assess_keyword_urgency(priority_indicators),
            "contextual_urgency": self._assess_contextual_urgency(request_context),
            "stakeholder_pressure": self._assess_stakeholder_pressure(request_context),
            "competitive_urgency": self._assess_competitive_urgency(request_context),
            "operational_impact": self._assess_operational_impact(request_context)
        }
        
        # Calculate overall urgency score
        urgency_score = self._calculate_urgency_score(urgency_factors)
        
        # Determine urgency level
        urgency_level = self._score_to_urgency_level(urgency_score)
        
        # Get timing requirements
        timing = self.urgency_matrix[urgency_level]
        
        # Generate assessment reasoning
        reasoning = self._generate_urgency_reasoning(urgency_factors, urgency_level)
        
        # Determine deadline impact
        deadline_impact = self._assess_deadline_impact(deadline, urgency_level)
        
        return UrgencyAssessment(
            urgency_level=urgency_level,
            urgency_score=urgency_score,
            max_response_time_minutes=timing["max_response"],
            escalation_threshold_minutes=timing["escalation"],
            priority_factors=urgency_factors,
            deadline_impact=deadline_impact,
            assessment_reasoning=reasoning
        )
    
    def select_optimal_staff(self,
                           available_staff: List[StaffMember],
                           complexity_assessment: ComplexityAssessment,
                           urgency_assessment: UrgencyAssessment,
                           selection_criteria: Optional[StaffSelectionCriteria] = None) -> StaffSelectionResult:
        """
        Select optimal staff using advanced matching algorithms.
        
        Args:
            available_staff: List of available staff members
            complexity_assessment: Task complexity assessment
            urgency_assessment: Urgency assessment
            selection_criteria: Additional selection criteria
            
        Returns:
            Optimal staff selection with reasoning
        """
        if not available_staff:
            raise ValueError("No available staff provided for selection")
        
        # Use default criteria if none provided
        if selection_criteria is None:
            selection_criteria = StaffSelectionCriteria(
                required_tier=complexity_assessment.required_tier_level,
                required_expertise=complexity_assessment.expertise_requirements
            )
        
        # Filter staff by basic criteria
        eligible_staff = self._filter_eligible_staff(available_staff, selection_criteria)
        
        if not eligible_staff:
            # Attempt fallback with succession candidates
            eligible_staff = self._find_succession_candidates(available_staff, selection_criteria)
        
        if not eligible_staff:
            raise ValueError("No eligible staff found matching criteria")
        
        # Score all eligible staff
        staff_scores = []
        for staff in eligible_staff:
            score = self._calculate_staff_score(
                staff, complexity_assessment, urgency_assessment, selection_criteria
            )
            staff_scores.append((staff, score))
        
        # Sort by score (highest first)
        staff_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select primary staff (highest score)
        primary_staff, primary_score = staff_scores[0]
        
        # Select supporting staff if collaboration required
        supporting_staff = []
        if complexity_assessment.collaboration_requirement and len(staff_scores) > 1:
            supporting_staff = self._select_supporting_staff(
                staff_scores[1:], complexity_assessment, primary_staff
            )
        
        # Calculate alternative options
        alternative_options = [(staff, score) for staff, score in staff_scores[1:4]]  # Top 3 alternatives
        
        # Generate selection reasoning
        selection_reasoning = self._generate_selection_reasoning(
            primary_staff, primary_score, complexity_assessment, urgency_assessment
        )
        
        # Calculate capacity utilization impact
        capacity_utilization = self._calculate_capacity_impact(
            primary_staff, supporting_staff, complexity_assessment
        )
        
        # Project success probability
        success_probability = self._project_success_probability(
            primary_staff, supporting_staff, complexity_assessment, urgency_assessment
        )
        
        # Calculate overall confidence
        confidence_level = self._calculate_selection_confidence(
            primary_staff, primary_score, len(eligible_staff), complexity_assessment
        )
        
        result = StaffSelectionResult(
            primary_staff=primary_staff,
            supporting_staff=supporting_staff,
            selection_score=primary_score,
            confidence_level=confidence_level,
            alternative_options=alternative_options,
            selection_reasoning=selection_reasoning,
            estimated_capacity_utilization=capacity_utilization,
            projected_success_probability=success_probability
        )
        
        # Record selection for learning
        self._record_selection(result, complexity_assessment, urgency_assessment)
        
        return result
    
    def check_escalation_triggers(self,
                                 current_tier: TierLevel,
                                 time_elapsed_minutes: int,
                                 current_complexity: ComplexityAssessment,
                                 performance_indicators: Dict[str, float]) -> List[EscalationProtocol]:
        """
        Check if escalation is needed based on various triggers.
        
        Args:
            current_tier: Current tier handling the request
            time_elapsed_minutes: Time elapsed since assignment
            current_complexity: Current complexity assessment
            performance_indicators: Performance metrics
            
        Returns:
            List of triggered escalation protocols
        """
        triggered_escalations = []
        
        for protocol in self.escalation_protocols:
            if protocol.from_tier != current_tier:
                continue
            
            if self._evaluate_escalation_conditions(
                protocol, time_elapsed_minutes, current_complexity, performance_indicators
            ):
                triggered_escalations.append(protocol)
        
        return triggered_escalations
    
    def optimize_tier_allocation(self,
                               pending_requests: List[Dict[str, Any]],
                               staff_availability: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Optimize tier allocation across multiple pending requests.
        
        Args:
            pending_requests: List of pending requests with assessments
            staff_availability: Current staff availability by ID
            
        Returns:
            Optimal allocation mapping tier to request IDs
        """
        # This would implement a sophisticated optimization algorithm
        # For now, return a placeholder structure
        return {
            "tier_1_allocations": [],
            "tier_2_allocations": [],
            "tier_3_allocations": [],
            "optimization_score": 0.0,
            "reasoning": "Placeholder optimization"
        }
    
    # Private helper methods for complexity assessment
    def _assess_data_source_complexity(self, context: Dict[str, Any]) -> float:
        """Assess complexity based on required data sources."""
        data_sources = context.get("data_sources", [])
        multi_source = context.get("multi_source_analysis", False)
        
        base_score = len(data_sources) * 10
        if multi_source:
            base_score *= 1.5
        
        return min(100, base_score)
    
    def _assess_cross_functional_needs(self, content: str, context: Dict[str, Any]) -> float:
        """Assess cross-functional coordination complexity."""
        cross_functional_keywords = [
            "coordination", "collaboration", "cross-company", "multi-department",
            "empire-wide", "strategic alignment", "cross-functional"
        ]
        
        keyword_matches = sum(1 for keyword in cross_functional_keywords if keyword in content.lower())
        companies_involved = len(context.get("companies_involved", []))
        departments_involved = len(context.get("departments_involved", []))
        
        score = (keyword_matches * 15) + (companies_involved * 20) + (departments_involved * 10)
        return min(100, score)
    
    def _assess_time_sensitivity(self, urgency_indicators: List[str], context: Dict[str, Any]) -> float:
        """Assess time sensitivity complexity."""
        urgent_keywords = ["immediate", "urgent", "critical", "emergency", "asap", "deadline"]
        matches = sum(1 for indicator in urgency_indicators if any(keyword in indicator.lower() for keyword in urgent_keywords))
        
        deadline = context.get("deadline")
        if deadline and isinstance(deadline, datetime):
            time_to_deadline = (deadline - datetime.now()).total_seconds() / 3600  # hours
            if time_to_deadline < 1:
                return 100
            elif time_to_deadline < 4:
                return 80
            elif time_to_deadline < 24:
                return 60
        
        return min(100, matches * 25)
    
    def _assess_decision_impact(self, content: str, context: Dict[str, Any]) -> float:
        """Assess the impact scope of decisions required."""
        impact_keywords = {
            "strategic": 30,
            "empire": 40,
            "company-wide": 25,
            "department": 15,
            "operational": 10,
            "triangle defense": 35,  # Special weight for Triangle Defense
            "founder": 50
        }
        
        score = 0
        for keyword, weight in impact_keywords.items():
            if keyword in content.lower() or keyword in str(context).lower():
                score += weight
        
        return min(100, score)
    
    def _assess_technical_complexity(self, content: str) -> float:
        """Assess technical complexity requirements."""
        technical_keywords = {
            "algorithm": 20,
            "machine learning": 25,
            "ai": 20,
            "analytics": 15,
            "predictive": 20,
            "neural network": 30,
            "optimization": 15,
            "statistical": 15,
            "graphql": 10,
            "neo4j": 15,
            "spark": 20
        }
        
        score = 0
        content_lower = content.lower()
        for keyword, weight in technical_keywords.items():
            if keyword in content_lower:
                score += weight
        
        return min(100, score)
    
    def _assess_stakeholder_complexity(self, context: Dict[str, Any]) -> float:
        """Assess complexity based on stakeholder involvement."""
        stakeholder_count = context.get("stakeholder_count", 1)
        external_stakeholders = context.get("external_stakeholders", False)
        
        score = stakeholder_count * 10
        if external_stakeholders:
            score *= 1.5
        
        return min(100, score)
    
    def _assess_risk_level(self, content: str, context: Dict[str, Any]) -> float:
        """Assess risk level associated with the task."""
        risk_keywords = ["risk", "critical", "failure", "emergency", "crisis"]
        matches = sum(1 for keyword in risk_keywords if keyword in content.lower())
        
        risk_level = context.get("risk_level", "medium")
        risk_scores = {"low": 20, "medium": 40, "high": 70, "critical": 90}
        
        return min(100, matches * 15 + risk_scores.get(risk_level, 40))
    
    def _score_to_complexity_level(self, score: float) -> TaskComplexity:
        """Convert complexity score to complexity level."""
        if score >= 90:
            return TaskComplexity.NUCLEAR
        elif score >= 80:
            return TaskComplexity.STRATEGIC
        elif score >= 70:
            return TaskComplexity.CRITICAL
        elif score >= 60:
            return TaskComplexity.ADVANCED
        elif score >= 40:
            return TaskComplexity.COMPLEX
        elif score >= 20:
            return TaskComplexity.STANDARD
        else:
            return TaskComplexity.SIMPLE
    
    def _complexity_to_tier(self, complexity: TaskComplexity, factors: Dict[str, float]) -> TierLevel:
        """Map complexity level to required tier level."""
        tier_mapping = {
            TaskComplexity.NUCLEAR: TierLevel.FOUNDER,
            TaskComplexity.STRATEGIC: TierLevel.EXECUTIVE,
            TaskComplexity.CRITICAL: TierLevel.STRATEGIC,
            TaskComplexity.ADVANCED: TierLevel.STRATEGIC,
            TaskComplexity.COMPLEX: TierLevel.ADVISORY,
            TaskComplexity.STANDARD: TierLevel.INNOVATION,
            TaskComplexity.SIMPLE: TierLevel.FOOTBALL
        }
        
        base_tier = tier_mapping[complexity]
        
        # Adjust based on specific factors
        if factors.get("decision_impact", 0) >= 80:
            # High decision impact may require escalation
            tier_hierarchy = [TierLevel.FOOTBALL, TierLevel.INNOVATION, TierLevel.ADVISORY, 
                            TierLevel.STRATEGIC, TierLevel.EXECUTIVE, TierLevel.AI_CORE, TierLevel.FOUNDER]
            current_index = tier_hierarchy.index(base_tier)
            if current_index < len(tier_hierarchy) - 1:
                base_tier = tier_hierarchy[current_index + 1]
        
        return base_tier
    
    def _determine_decision_scope(self, context: Dict[str, Any], factors: Dict[str, float]) -> DecisionScope:
        """Determine the scope of decision-making required."""
        if factors.get("decision_impact", 0) >= 80 or "empire" in str(context).lower():
            return DecisionScope.EMPIRE
        elif factors.get("cross_functional", 0) >= 60 or len(context.get("companies_involved", [])) > 1:
            return DecisionScope.CROSS_COMPANY
        elif factors.get("decision_impact", 0) >= 50:
            return DecisionScope.COMPANY
        elif factors.get("cross_functional", 0) >= 30:
            return DecisionScope.DEPARTMENTAL
        else:
            return DecisionScope.OPERATIONAL
    
    def _extract_expertise_requirements(self, content: str, context: Dict[str, Any], complexity: TaskComplexity) -> List[ExpertiseArea]:
        """Extract required expertise areas from content and context."""
        expertise_keywords = {
            "triangle defense": ExpertiseArea.TRIANGLE_DEFENSE_MASTERY,
            "defensive": ExpertiseArea.DEFENSIVE_ANALYSIS,
            "football": ExpertiseArea.FOOTBALL_ANALYTICS,
            "analytics": ExpertiseArea.STATISTICAL_INTELLIGENCE,
            "ai": ExpertiseArea.AI_DEVELOPMENT,
            "medical": ExpertiseArea.SPORTS_MEDICINE,
            "security": ExpertiseArea.PHYSICAL_SECURITY,
            "leadership": ExpertiseArea.LEADERSHIP_EXCELLENCE,
            "strategic": ExpertiseArea.STRATEGIC_VISION
        }
        
        required_expertise = []
        content_lower = content.lower()
        
        for keyword, expertise in expertise_keywords.items():
            if keyword in content_lower:
                required_expertise.append(expertise)
        
        # Add default expertise based on complexity
        if complexity in [TaskComplexity.STRATEGIC, TaskComplexity.NUCLEAR]:
            required_expertise.append(ExpertiseArea.STRATEGIC_VISION)
        
        return list(set(required_expertise))  # Remove duplicates
    
    def _estimate_task_duration(self, complexity: TaskComplexity, factors: Dict[str, float]) -> int:
        """Estimate task duration based on complexity and factors."""
        base_durations = {
            TaskComplexity.SIMPLE: 30,
            TaskComplexity.STANDARD: 60,
            TaskComplexity.COMPLEX: 120,
            TaskComplexity.ADVANCED: 180,
            TaskComplexity.CRITICAL: 240,
            TaskComplexity.STRATEGIC: 360,
            TaskComplexity.NUCLEAR: 480
        }
        
        base_duration = base_durations[complexity]
        
        # Adjust based on factors
        if factors.get("data_sources", 0) > 60:
            base_duration *= 1.3
        if factors.get("cross_functional", 0) > 50:
            base_duration *= 1.2
        if factors.get("technical_depth", 0) > 70:
            base_duration *= 1.4
        
        return int(base_duration)
    
    def _assess_collaboration_needs(self, factors: Dict[str, float], complexity: TaskComplexity) -> bool:
        """Determine if collaboration is required."""
        return (
            factors.get("cross_functional", 0) > 40 or
            factors.get("stakeholder_count", 0) > 30 or
            complexity in [TaskComplexity.CRITICAL, TaskComplexity.STRATEGIC, TaskComplexity.NUCLEAR]
        )
    
    def _calculate_assessment_confidence(self, factors: Dict[str, float], context: Dict[str, Any]) -> float:
        """Calculate confidence in the complexity assessment."""
        # Base confidence starts high
        confidence = 0.8
        
        # Increase confidence with more context
        if len(context) > 5:
            confidence += 0.1
        
        # Decrease confidence if factors are borderline
        factor_variance = statistics.stdev(factors.values()) if len(factors) > 1 else 0
        if factor_variance > 20:  # High variance indicates uncertainty
            confidence -= 0.2
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_special_considerations(self, factors: Dict[str, float], complexity: TaskComplexity, context: Dict[str, Any]) -> List[str]:
        """Generate special considerations for the task."""
        considerations = []
        
        if complexity == TaskComplexity.NUCLEAR:
            considerations.append("Nuclear protocol - Founder authority required")
        
        if factors.get("time_sensitivity", 0) > 80:
            considerations.append("High time sensitivity - Expedited processing required")
        
        if factors.get("cross_functional", 0) > 70:
            considerations.append("Extensive cross-functional coordination needed")
        
        if "triangle defense" in str(context).lower():
            considerations.append("Triangle Defense expertise critical")
        
        return considerations
    
    def _identify_data_sources(self, context: Dict[str, Any]) -> List[str]:
        """Identify required data sources from context."""
        default_sources = ["supabase"]  # Always include real-time data
        
        context_sources = context.get("data_sources", [])
        if isinstance(context_sources, list):
            return list(set(default_sources + context_sources))
        
        return default_sources
    
    # Urgency assessment helper methods
    def _assess_deadline_pressure(self, deadline: Optional[datetime]) -> float:
        """Assess urgency based on deadline pressure."""
        if not deadline:
            return 20  # Low urgency without explicit deadline
        
        time_to_deadline = (deadline - datetime.now()).total_seconds() / 3600  # hours
        
        if time_to_deadline <= 0:
            return 100  # Past deadline
        elif time_to_deadline <= 1:
            return 90
        elif time_to_deadline <= 4:
            return 70
        elif time_to_deadline <= 24:
            return 50
        else:
            return 20
    
    def _assess_business_impact_urgency(self, business_impact: str) -> float:
        """Assess urgency based on business impact description."""
        impact_keywords = {
            "critical": 40,
            "urgent": 35,
            "immediate": 45,
            "emergency": 50,
            "revenue": 25,
            "client": 20,
            "reputation": 30
        }
        
        score = 0
        impact_lower = business_impact.lower()
        for keyword, weight in impact_keywords.items():
            if keyword in impact_lower:
                score += weight
        
        return min(100, score)
    
    def _assess_keyword_urgency(self, priority_indicators: List[str]) -> float:
        """Assess urgency based on keyword indicators."""
        urgent_keywords = ["asap", "urgent", "critical", "emergency", "immediate", "deadline"]
        matches = sum(1 for indicator in priority_indicators 
                     for keyword in urgent_keywords 
                     if keyword in indicator.lower())
        
        return min(100, matches * 30)
    
    def _assess_contextual_urgency(self, context: Dict[str, Any]) -> float:
        """Assess urgency from context clues."""
        urgency_factors = {
            "crisis_mode": 50,
            "client_escalation": 40,
            "system_down": 60,
            "competitive_threat": 35,
            "regulatory_deadline": 45
        }
        
        score = 0
        for factor, weight in urgency_factors.items():
            if context.get(factor, False):
                score += weight
        
        return min(100, score)
    
    def _assess_stakeholder_pressure(self, context: Dict[str, Any]) -> float:
        """Assess urgency based on stakeholder pressure."""
        stakeholder_urgency = context.get("stakeholder_urgency", "medium")
        urgency_scores = {"low": 10, "medium": 30, "high": 60, "critical": 80}
        
        return urgency_scores.get(stakeholder_urgency, 30)
    
    def _assess_competitive_urgency(self, context: Dict[str, Any]) -> float:
        """Assess urgency based on competitive factors."""
        competitive_indicators = context.get("competitive_indicators", [])
        return min(100, len(competitive_indicators) * 20)
    
    def _assess_operational_impact(self, context: Dict[str, Any]) -> float:
        """Assess urgency based on operational impact."""
        operational_impact = context.get("operational_impact", "low")
        impact_scores = {"low": 10, "medium": 25, "high": 50, "critical": 75}
        
        return impact_scores.get(operational_impact, 25)
    
    def _calculate_urgency_score(self, factors: Dict[str, float]) -> float:
        """Calculate overall urgency score from factors."""
        weights = {
            "deadline_pressure": 0.25,
            "business_impact": 0.20,
            "keyword_indicators": 0.15,
            "contextual_urgency": 0.15,
            "stakeholder_pressure": 0.10,
            "competitive_urgency": 0.10,
            "operational_impact": 0.05
        }
        
        weighted_score = sum(factors.get(factor, 0) * weight for factor, weight in weights.items())
        return min(100, weighted_score)
    
    def _score_to_urgency_level(self, score: float) -> UrgencyLevel:
        """Convert urgency score to urgency level."""
        if score >= 80:
            return UrgencyLevel.EMERGENCY
        elif score >= 60:
            return UrgencyLevel.CRITICAL
        elif score >= 40:
            return UrgencyLevel.HIGH
        elif score >= 20:
            return UrgencyLevel.MEDIUM
        else:
            return UrgencyLevel.LOW
    
    def _generate_urgency_reasoning(self, factors: Dict[str, float], urgency_level: UrgencyLevel) -> str:
        """Generate reasoning for urgency assessment."""
        top_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)[:3]
        
        reasoning = f"Urgency level {urgency_level.value} determined by: "
        factor_descriptions = []
        
        for factor, score in top_factors:
            if score > 20:  # Only include significant factors
                factor_descriptions.append(f"{factor.replace('_', ' ')} ({score:.1f})")
        
        if factor_descriptions:
            reasoning += ", ".join(factor_descriptions)
        else:
            reasoning += "low priority indicators across all factors"
        
        return reasoning
    
    def _assess_deadline_impact(self, deadline: Optional[datetime], urgency_level: UrgencyLevel) -> str:
        """Assess the impact of deadline on processing."""
        if not deadline:
            return "No explicit deadline provided"
        
        time_to_deadline = (deadline - datetime.now()).total_seconds() / 3600
        
        if time_to_deadline <= 0:
            return "PAST DEADLINE - Immediate attention required"
        elif urgency_level == UrgencyLevel.EMERGENCY:
            return f"Critical deadline in {time_to_deadline:.1f} hours"
        elif urgency_level == UrgencyLevel.CRITICAL:
            return f"Urgent deadline in {time_to_deadline:.1f} hours"
        else:
            return f"Deadline in {time_to_deadline:.1f} hours - manageable"
    
    # Staff selection helper methods
    def _filter_eligible_staff(self, available_staff: List[StaffMember], criteria: StaffSelectionCriteria) -> List[StaffMember]:
        """Filter staff based on selection criteria."""
        eligible = []
        
        for staff in available_staff:
            # Check tier requirement
            if not staff.can_handle_tier_requirement(criteria.required_tier):
                continue
            
            # Check workload
            if staff.workload_percentage > criteria.max_workload_percentage:
                continue
            
            # Check effectiveness rating
            if staff.effectiveness_rating < criteria.min_effectiveness_rating:
                continue
            
            # Check exclusion list
            if staff.staff_id in criteria.exclude_staff_ids:
                continue
            
            # Check required expertise
            if criteria.required_expertise:
                expertise_score = staff.get_expertise_match_score([exp.value for exp in criteria.required_expertise])
                if expertise_score < 0.3:  # Minimum 30% match for required expertise
                    continue
            
            eligible.append(staff)
        
        return eligible
    
    def _find_succession_candidates(self, available_staff: List[StaffMember], criteria: StaffSelectionCriteria) -> List[StaffMember]:
        """Find succession candidates when no direct matches available."""
        # This would implement succession logic - placeholder for now
        return []
    
    def _calculate_staff_score(self,
                              staff: StaffMember,
                              complexity: ComplexityAssessment,
                              urgency: UrgencyAssessment,
                              criteria: StaffSelectionCriteria) -> float:
        """Calculate comprehensive staff match score."""
        
        # Base scoring components
        scores = {
            "expertise_match": self._score_expertise_match(staff, complexity, criteria),
            "tier_appropriateness": self._score_tier_appropriateness(staff, complexity),
            "availability": self._score_availability(staff, urgency),
            "effectiveness": staff.effectiveness_rating / 100.0,
            "workload_capacity": 1.0 - (staff.workload_percentage / 100.0),
            "specialization_bonus": self._score_specialization_bonus(staff, complexity)
        }
        
        # Weighted final score
        weights = {
            "expertise_match": 0.30,
            "tier_appropriateness": 0.20,
            "availability": 0.15,
            "effectiveness": 0.15,
            "workload_capacity": 0.10,
            "specialization_bonus": 0.10
        }
        
        final_score = sum(scores[component] * weights[component] for component in scores)
        
        return min(1.0, final_score)
    
    def _score_expertise_match(self, staff: StaffMember, complexity: ComplexityAssessment, criteria: StaffSelectionCriteria) -> float:
        """Score expertise match quality."""
        required_expertise = [exp.value for exp in complexity.expertise_requirements]
        if criteria.required_expertise:
            required_expertise.extend([exp.value for exp in criteria.required_expertise])
        
        if not required_expertise:
            return 0.8  # Default good score when no specific expertise required
        
        return staff.get_expertise_match_score(required_expertise)
    
    def _score_tier_appropriateness(self, staff: StaffMember, complexity: ComplexityAssessment) -> float:
        """Score how appropriate the staff tier is for the complexity."""
        tier_capabilities = self.tier_capabilities[staff.tier_level]
        
        if complexity.complexity_score <= tier_capabilities["max_complexity"]:
            # Appropriate tier
            return 1.0
        else:
            # Overqualified but can handle it
            return 0.8
    
    def _score_availability(self, staff: StaffMember, urgency: UrgencyAssessment) -> float:
        """Score availability based on urgency requirements."""
        if staff.status == StaffStatus.AVAILABLE:
            return 1.0
        elif staff.status == StaffStatus.ASSIGNED and staff.workload_percentage < 50:
            return 0.7  # Can take on additional work
        else:
            return 0.3  # Limited availability
    
    def _score_specialization_bonus(self, staff: StaffMember, complexity: ComplexityAssessment) -> float:
        """Score bonus for special expertise matches."""
        bonus = 0.0
        
        # Triangle Defense specialist bonus
        if (ExpertiseArea.TRIANGLE_DEFENSE_MASTERY in staff.expertise_areas and
            "triangle defense" in str(complexity.special_considerations).lower()):
            bonus += 0.3
        
        # Leadership bonus for high complexity
        if (ExpertiseArea.LEADERSHIP_EXCELLENCE in staff.expertise_areas and
            complexity.complexity_level in [TaskComplexity.CRITICAL, TaskComplexity.STRATEGIC, TaskComplexity.NUCLEAR]):
            bonus += 0.2
        
        return min(1.0, bonus)
    
    def _select_supporting_staff(self, 
                               remaining_staff: List[Tuple[StaffMember, float]],
                               complexity: ComplexityAssessment,
                               primary_staff: StaffMember) -> List[StaffMember]:
        """Select supporting staff for collaboration."""
        supporting = []
        
        # Select up to 2 supporting staff members
        for staff, score in remaining_staff[:2]:
            # Ensure diverse expertise
            if not self._has_overlapping_expertise(staff, primary_staff):
                supporting.append(staff)
            elif score > 0.8:  # Very high score overrides diversity requirement
                supporting.append(staff)
        
        return supporting
    
    def _has_overlapping_expertise(self, staff1: StaffMember, staff2: StaffMember) -> bool:
        """Check if two staff members have significant expertise overlap."""
        overlap = set(staff1.expertise_areas) & set(staff2.expertise_areas)
        return len(overlap) > len(staff1.expertise_areas) * 0.6
    
    def _generate_selection_reasoning(self,
                                    primary_staff: StaffMember,
                                    score: float,
                                    complexity: ComplexityAssessment,
                                    urgency: UrgencyAssessment) -> str:
        """Generate reasoning for staff selection."""
        return (f"Selected {primary_staff.full_name} ({primary_staff.nickname}) "
                f"with score {score:.2f} based on {complexity.complexity_level.value} "
                f"complexity and {urgency.urgency_level.value} urgency. "
                f"Optimal expertise match in {[exp.value for exp in primary_staff.expertise_areas][:2]}.")
    
    def _calculate_capacity_impact(self,
                                 primary_staff: StaffMember,
                                 supporting_staff: List[StaffMember],
                                 complexity: ComplexityAssessment) -> float:
        """Calculate impact on team capacity utilization."""
        total_impact = complexity.estimated_duration_minutes / (8 * 60)  # Convert to workday percentage
        
        staff_count = 1 + len(supporting_staff)
        return total_impact / staff_count  # Distributed impact
    
    def _project_success_probability(self,
                                   primary_staff: StaffMember,
                                   supporting_staff: List[StaffMember],
                                   complexity: ComplexityAssessment,
                                   urgency: UrgencyAssessment) -> float:
        """Project probability of successful task completion."""
        base_probability = primary_staff.effectiveness_rating / 100.0
        
        # Adjust for complexity match
        if complexity.complexity_level in [TaskComplexity.SIMPLE, TaskComplexity.STANDARD]:
            base_probability *= 1.1  # Easier tasks boost success
        elif complexity.complexity_level in [TaskComplexity.CRITICAL, TaskComplexity.STRATEGIC]:
            base_probability *= 0.9  # Harder tasks reduce success
        
        # Team collaboration bonus
        if supporting_staff:
            collaboration_bonus = min(0.1, len(supporting_staff) * 0.05)
            base_probability += collaboration_bonus
        
        # Urgency pressure impact
        if urgency.urgency_level == UrgencyLevel.EMERGENCY:
            base_probability *= 0.85  # Pressure reduces success slightly
        
        return min(1.0, base_probability)
    
    def _calculate_selection_confidence(self,
                                      primary_staff: StaffMember,
                                      score: float,
                                      eligible_count: int,
                                      complexity: ComplexityAssessment) -> float:
        """Calculate confidence in the staff selection."""
        confidence = score  # Base confidence from selection score
        
        # Adjust for selection pool size
        if eligible_count > 5:
            confidence += 0.1  # More options increase confidence
        elif eligible_count < 3:
            confidence -= 0.1  # Fewer options decrease confidence
        
        # Adjust for assessment confidence
        confidence *= complexity.assessment_confidence
        
        return min(1.0, max(0.0, confidence))
    
    def _record_selection(self,
                         result: StaffSelectionResult,
                         complexity: ComplexityAssessment,
                         urgency: UrgencyAssessment):
        """Record selection for performance tracking and learning."""
        record = {
            "timestamp": datetime.now(),
            "primary_staff_id": result.primary_staff.staff_id,
            "selection_score": result.selection_score,
            "complexity_level": complexity.complexity_level.value,
            "urgency_level": urgency.urgency_level.value,
            "projected_success": result.projected_success_probability
        }
        
        self.selection_history.append(record)
        
        # Update metrics
        self.performance_metrics["tier_utilization"][result.primary_staff.tier_level.value] += 1
        self.performance_metrics["complexity_distribution"][complexity.complexity_level.value] += 1
    
    def _initialize_escalation_protocols(self) -> List[EscalationProtocol]:
        """Initialize escalation protocols for different scenarios."""
        protocols = []
        
        # Time-based escalations
        protocols.append(EscalationProtocol(
            trigger=EscalationTrigger.TIME_EXCEEDED,
            from_tier=TierLevel.FOOTBALL,
            to_tier=TierLevel.INNOVATION,
            conditions={"time_threshold_minutes": 120},
            notification_required=True,
            approval_required=False,
            emergency_override=False
        ))
        
        # Complexity escalations
        protocols.append(EscalationProtocol(
            trigger=EscalationTrigger.COMPLEXITY_INCREASE,
            from_tier=TierLevel.INNOVATION,
            to_tier=TierLevel.STRATEGIC,
            conditions={"complexity_increase_threshold": 20},
            notification_required=True,
            approval_required=True,
            emergency_override=False
        ))
        
        # Emergency escalations
        protocols.append(EscalationProtocol(
            trigger=EscalationTrigger.EMERGENCY_DECLARED,
            from_tier=TierLevel.STRATEGIC,
            to_tier=TierLevel.FOUNDER,
            conditions={"emergency_type": "nuclear"},
            notification_required=True,
            approval_required=False,
            emergency_override=True
        ))
        
        return protocols
    
    def _evaluate_escalation_conditions(self,
                                      protocol: EscalationProtocol,
                                      time_elapsed: int,
                                      complexity: ComplexityAssessment,
                                      performance: Dict[str, float]) -> bool:
        """Evaluate if escalation conditions are met."""
        if protocol.trigger == EscalationTrigger.TIME_EXCEEDED:
            return time_elapsed > protocol.conditions.get("time_threshold_minutes", 120)
        elif protocol.trigger == EscalationTrigger.COMPLEXITY_INCREASE:
            return complexity.complexity_score > protocol.conditions.get("complexity_increase_threshold", 80)
        elif protocol.trigger == EscalationTrigger.QUALITY_CONCERN:
            return performance.get("quality_score", 100) < protocol.conditions.get("min_quality_threshold", 70)
        
        return False
    
    def get_tier_manager_metrics(self) -> Dict[str, Any]:
        """Get comprehensive tier management metrics."""
        return {
            "selections_made": len(self.selection_history),
            "performance_metrics": self.performance_metrics,
            "tier_utilization": dict(self.performance_metrics["tier_utilization"]),
            "complexity_distribution": dict(self.performance_metrics["complexity_distribution"]),
            "escalation_protocols_active": len(self.escalation_protocols),
            "avg_selection_confidence": statistics.mean([r.get("selection_score", 0) for r in self.selection_history]) if self.selection_history else 0
        }
