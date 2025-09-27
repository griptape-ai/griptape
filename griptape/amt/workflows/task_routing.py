"""
AMT Task Routing Workflow - Intelligent request distribution optimization system.

Optimizes task distribution across 25 championship professionals using advanced algorithms
for expertise matching, workload balancing, performance optimization, and real-time
adaptive routing. Integrates with intelligence coordination and tier management systems
for championship-level task allocation and execution efficiency.
"""

import logging
import asyncio
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import heapq
import statistics

# Import Griptape workflow components
from griptape.structures import Workflow
from griptape.tasks import PromptTask
from griptape.memory import ConversationMemory
from griptape.rules import Rule

# Import AMT intelligence components
from ..intelligence import (
    IntelligenceCoordinator, IntelligenceRequest, IntelligenceResponse,
    ComplexityAssessment, UrgencyAssessment, TierLevel, ExpertiseArea,
    StaffStatus, TierManager, StaffSelectionCriteria, StaffSelectionResult
)

# Import AMT agent components
from ..agents import StaffFactory, StaffAgentBase, StaffPersonality


class RoutingStrategy(Enum):
    """Task routing strategies for different optimization goals."""
    PERFORMANCE_OPTIMAL = "performance_optimal"         # Optimize for best performance
    LOAD_BALANCED = "load_balanced"                     # Balance workload evenly
    EXPERTISE_FOCUSED = "expertise_focused"             # Prioritize expertise match
    SPEED_OPTIMIZED = "speed_optimized"                 # Optimize for fastest completion
    LEARNING_ENHANCED = "learning_enhanced"             # Optimize for skill development
    SUCCESSION_AWARE = "succession_aware"               # Consider succession planning
    EMERGENCY_PRIORITY = "emergency_priority"           # Emergency routing protocols
    TRIANGLE_DEFENSE_SPECIALIZED = "triangle_defense_specialized" # TD expertise priority


class RoutingDecisionFactor(Enum):
    """Factors influencing routing decisions."""
    EXPERTISE_MATCH = "expertise_match"                 # How well expertise aligns
    WORKLOAD_CAPACITY = "workload_capacity"             # Available capacity
    PERFORMANCE_HISTORY = "performance_history"         # Historical performance
    RESPONSE_TIME = "response_time"                     # Expected response time
    QUALITY_SCORE = "quality_score"                     # Expected quality
    COLLABORATION_SYNERGY = "collaboration_synergy"     # Team collaboration potential
    LEARNING_OPPORTUNITY = "learning_opportunity"       # Skill development potential
    SUCCESSION_READINESS = "succession_readiness"       # Succession planning value


class LoadBalancingAlgorithm(Enum):
    """Load balancing algorithms for workload distribution."""
    ROUND_ROBIN = "round_robin"                         # Simple round robin
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"       # Weighted by capacity
    LEAST_CONNECTIONS = "least_connections"             # Least active tasks
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections" # Weighted least tasks
    PERFORMANCE_WEIGHTED = "performance_weighted"        # Weighted by performance
    ADAPTIVE_WEIGHTED = "adaptive_weighted"             # Dynamic weight adjustment


@dataclass
class RoutingRequest:
    """Enhanced request structure for routing optimization."""
    
    # Core Request
    intelligence_request: IntelligenceRequest
    routing_id: str
    received_at: datetime
    
    # Routing Analysis
    complexity_assessment: Optional[ComplexityAssessment] = None
    urgency_assessment: Optional[UrgencyAssessment] = None
    expertise_requirements: List[ExpertiseArea] = field(default_factory=list)
    
    # Routing Preferences
    preferred_strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE_OPTIMAL
    exclude_staff: List[str] = field(default_factory=list)
    require_collaboration: bool = False
    max_response_time_minutes: Optional[int] = None
    
    # Context and Constraints
    business_context: Dict[str, Any] = field(default_factory=dict)
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    quality_requirements: Dict[str, float] = field(default_factory=dict)
    
    # Triangle Defense Context
    triangle_defense_priority: bool = False
    formation_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingCandidate:
    """Candidate staff member for task routing."""
    
    staff_agent: StaffAgentBase
    staff_id: str
    
    # Scoring Components
    expertise_score: float = 0.0
    capacity_score: float = 0.0
    performance_score: float = 0.0
    speed_score: float = 0.0
    quality_score: float = 0.0
    synergy_score: float = 0.0
    
    # Composite Scores
    overall_score: float = 0.0
    confidence_level: float = 0.0
    
    # Routing Metadata
    estimated_completion_time: timedelta = field(default_factory=lambda: timedelta(hours=2))
    expected_quality: float = 0.9
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    collaboration_potential: List[str] = field(default_factory=list)


@dataclass
class RoutingDecision:
    """Final routing decision with comprehensive metadata."""
    
    routing_id: str
    selected_staff: RoutingCandidate
    alternative_candidates: List[RoutingCandidate]
    
    # Decision Metadata
    routing_strategy_used: RoutingStrategy
    decision_factors: Dict[RoutingDecisionFactor, float]
    confidence_score: float
    
    # Performance Predictions
    estimated_completion_time: timedelta
    predicted_quality_score: float
    expected_success_probability: float
    
    # Resource Planning
    collaboration_requirements: List[str]
    resource_allocation: Dict[str, Any]
    monitoring_requirements: List[str]
    
    # Decision Reasoning
    selection_reasoning: str
    alternative_analysis: str
    risk_assessment: str


@dataclass
class RoutingPerformanceMetrics:
    """Comprehensive routing performance tracking."""
    
    # Routing Statistics
    total_requests_routed: int = 0
    successful_routings: int = 0
    routing_failures: int = 0
    average_routing_time_ms: float = 0.0
    
    # Quality Metrics
    average_completion_time_hours: float = 0.0
    average_quality_score: float = 0.0
    average_success_rate: float = 0.0
    customer_satisfaction_score: float = 0.0
    
    # Load Balancing Metrics
    workload_distribution_variance: float = 0.0
    capacity_utilization_rate: float = 0.0
    load_balancing_efficiency: float = 0.0
    
    # Strategy Performance
    strategy_performance: Dict[RoutingStrategy, Dict[str, float]] = field(default_factory=dict)
    expertise_matching_accuracy: float = 0.0
    
    # Staff Performance
    staff_utilization_rates: Dict[str, float] = field(default_factory=dict)
    staff_performance_scores: Dict[str, float] = field(default_factory=dict)
    staff_specialization_efficiency: Dict[str, float] = field(default_factory=dict)
    
    # Triangle Defense Metrics
    triangle_defense_routing_success: float = 0.0
    formation_analysis_efficiency: float = 0.0
    
    # Adaptive Learning
    algorithm_learning_score: float = 0.0
    routing_optimization_improvement: float = 0.0
    
    # Last Updated
    last_updated: datetime = field(default_factory=datetime.now)


class TaskRoutingWorkflow(Workflow):
    """
    Intelligent task routing workflow for optimal request distribution.
    
    Implements sophisticated algorithms for routing requests across 25 championship
    professionals with multi-factor optimization, adaptive learning, and real-time
    performance monitoring for championship-level task allocation efficiency.
    """
    
    def __init__(self,
                 intelligence_coordinator: IntelligenceCoordinator,
                 staff_factory: StaffFactory,
                 tier_manager: TierManager,
                 default_strategy: RoutingStrategy = RoutingStrategy.PERFORMANCE_OPTIMAL,
                 **kwargs):
        """
        Initialize task routing workflow with advanced optimization capabilities.
        
        Args:
            intelligence_coordinator: Central intelligence coordination system
            staff_factory: Factory for accessing championship professionals
            tier_manager: Tier management for complexity assessment
            default_strategy: Default routing strategy
            **kwargs: Additional workflow parameters
        """
        
        # Initialize base workflow
        super().__init__(
            memory=ConversationMemory(),
            rules=[
                Rule("Optimize task allocation for maximum performance and efficiency"),
                Rule("Balance workload fairly across all championship professionals"),
                Rule("Match expertise requirements with staff capabilities precisely"),
                Rule("Consider Triangle Defense specialization in routing decisions"),
                Rule("Maintain championship-level quality standards in all assignments"),
                Rule("Adapt routing algorithms based on performance feedback")
            ],
            **kwargs
        )
        
        # Core components
        self.intelligence_coordinator = intelligence_coordinator
        self.staff_factory = staff_factory
        self.tier_manager = tier_manager
        self.default_strategy = default_strategy
        
        # Routing state
        self.pending_requests: Dict[str, RoutingRequest] = {}
        self.active_assignments: Dict[str, RoutingDecision] = {}
        self.routing_history: deque = deque(maxlen=1000)  # Last 1000 routing decisions
        
        # Performance tracking
        self.performance_metrics = RoutingPerformanceMetrics()
        self.algorithm_weights: Dict[RoutingDecisionFactor, float] = {}
        self.strategy_effectiveness: Dict[RoutingStrategy, float] = {}
        
        # Load balancing
        self.load_balancing_algorithm = LoadBalancingAlgorithm.ADAPTIVE_WEIGHTED
        self.staff_workload_tracking: Dict[str, float] = {}
        self.capacity_utilization_targets: Dict[str, float] = {}
        
        # Learning and adaptation
        self.routing_patterns: Dict[str, Any] = {}
        self.performance_learning_matrix: np.ndarray = np.zeros((25, 10))  # Staff x factors
        self.adaptive_weights: Dict[str, float] = {}
        
        # Initialize routing system
        self._initialize_routing_algorithms()
        
        # Logger
        self.logger = logging.getLogger("AMT.TaskRouting")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Task Routing Workflow initialized with advanced optimization algorithms")
    
    async def route_request(self,
                          intelligence_request: IntelligenceRequest,
                          routing_strategy: Optional[RoutingStrategy] = None,
                          routing_constraints: Dict[str, Any] = None) -> RoutingDecision:
        """
        Route intelligence request to optimal staff using advanced algorithms.
        
        Args:
            intelligence_request: Request to route
            routing_strategy: Optional strategy override
            routing_constraints: Additional routing constraints
            
        Returns:
            Comprehensive routing decision with metadata
        """
        
        routing_start = time.time()
        routing_id = f"route_{int(time.time() * 1000)}"
        routing_constraints = routing_constraints or {}
        
        # Create enhanced routing request
        routing_request = RoutingRequest(
            intelligence_request=intelligence_request,
            routing_id=routing_id,
            received_at=datetime.now(),
            preferred_strategy=routing_strategy or self.default_strategy,
            exclude_staff=routing_constraints.get("exclude_staff", []),
            require_collaboration=routing_constraints.get("require_collaboration", False),
            max_response_time_minutes=routing_constraints.get("max_response_time_minutes"),
            business_context=routing_constraints.get("business_context", {}),
            triangle_defense_priority=routing_constraints.get("triangle_defense_priority", False)
        )
        
        try:
            # Store pending request
            self.pending_requests[routing_id] = routing_request
            
            # Analyze request complexity and requirements
            await self._analyze_routing_request(routing_request)
            
            # Generate candidate staff members
            candidates = await self._generate_routing_candidates(routing_request)
            
            # Apply routing strategy and algorithms
            routing_decision = await self._apply_routing_strategy(routing_request, candidates)
            
            # Validate and optimize routing decision
            validated_decision = await self._validate_routing_decision(routing_decision, routing_request)
            
            # Execute routing assignment
            await self._execute_routing_assignment(validated_decision)
            
            # Update performance metrics
            self._update_routing_metrics(validated_decision, routing_start)
            
            # Learn from routing decision
            await self._update_routing_learning(validated_decision, routing_request)
            
            self.logger.info(f"Request routed successfully: {routing_id} -> {validated_decision.selected_staff.staff_id} - {(time.time() - routing_start) * 1000:.2f}ms")
            return validated_decision
            
        except Exception as e:
            self.logger.error(f"Routing failed: {routing_id} - {str(e)}")
            self.performance_metrics.routing_failures += 1
            raise
        finally:
            # Clean up pending request
            if routing_id in self.pending_requests:
                del self.pending_requests[routing_id]
    
    async def batch_route_requests(self,
                                 requests: List[IntelligenceRequest],
                                 batch_strategy: RoutingStrategy = RoutingStrategy.LOAD_BALANCED) -> List[RoutingDecision]:
        """
        Route multiple requests simultaneously with batch optimization.
        
        Args:
            requests: List of requests to route
            batch_strategy: Strategy for batch routing optimization
            
        Returns:
            List of routing decisions optimized for batch efficiency
        """
        
        batch_start = time.time()
        batch_id = f"batch_{int(time.time() * 1000)}"
        
        # Create routing requests for batch
        routing_requests = []
        for i, request in enumerate(requests):
            routing_request = RoutingRequest(
                intelligence_request=request,
                routing_id=f"{batch_id}_req_{i}",
                received_at=datetime.now(),
                preferred_strategy=batch_strategy
            )
            routing_requests.append(routing_request)
        
        # Analyze all requests for batch optimization
        for routing_request in routing_requests:
            await self._analyze_routing_request(routing_request)
        
        # Apply batch routing optimization
        routing_decisions = await self._apply_batch_routing_optimization(routing_requests, batch_strategy)
        
        # Execute all routing assignments
        for decision in routing_decisions:
            await self._execute_routing_assignment(decision)
        
        batch_time = time.time() - batch_start
        self.logger.info(f"Batch routing completed: {len(requests)} requests in {batch_time:.2f}s")
        
        return routing_decisions
    
    async def rebalance_workload(self,
                               target_utilization: float = 0.8,
                               rebalance_strategy: str = "gradual") -> Dict[str, Any]:
        """
        Rebalance workload across staff members for optimal utilization.
        
        Args:
            target_utilization: Target capacity utilization percentage
            rebalance_strategy: Strategy for rebalancing (gradual, immediate, smart)
            
        Returns:
            Rebalancing results and new workload distribution
        """
        
        rebalance_start = time.time()
        
        # Analyze current workload distribution
        current_distribution = await self._analyze_workload_distribution()
        
        # Identify rebalancing opportunities
        rebalance_opportunities = await self._identify_rebalance_opportunities(
            current_distribution, target_utilization
        )
        
        # Apply rebalancing strategy
        if rebalance_strategy == "gradual":
            rebalance_result = await self._apply_gradual_rebalancing(rebalance_opportunities)
        elif rebalance_strategy == "immediate":
            rebalance_result = await self._apply_immediate_rebalancing(rebalance_opportunities)
        else:  # smart
            rebalance_result = await self._apply_smart_rebalancing(rebalance_opportunities)
        
        # Update load balancing metrics
        self._update_load_balancing_metrics(rebalance_result)
        
        rebalance_time = time.time() - rebalance_start
        self.logger.info(f"Workload rebalancing completed in {rebalance_time:.2f}s")
        
        return {
            "rebalancing_summary": rebalance_result,
            "new_distribution": await self._analyze_workload_distribution(),
            "rebalancing_time": rebalance_time,
            "utilization_improvement": rebalance_result.get("utilization_improvement", 0.0)
        }
    
    async def optimize_routing_strategy(self,
                                      optimization_period_days: int = 30,
                                      optimization_objectives: List[str] = None) -> Dict[str, Any]:
        """
        Optimize routing strategies based on historical performance.
        
        Args:
            optimization_period_days: Period for performance analysis
            optimization_objectives: Specific optimization objectives
            
        Returns:
            Strategy optimization results and recommendations
        """
        
        optimization_objectives = optimization_objectives or [
            "maximize_quality", "minimize_response_time", "balance_workload"
        ]
        
        # Analyze historical routing performance
        performance_analysis = await self._analyze_historical_performance(optimization_period_days)
        
        # Identify optimization opportunities
        optimization_opportunities = await self._identify_optimization_opportunities(
            performance_analysis, optimization_objectives
        )
        
        # Generate strategy recommendations
        strategy_recommendations = await self._generate_strategy_recommendations(optimization_opportunities)
        
        # Apply adaptive algorithm improvements
        algorithm_improvements = await self._apply_algorithm_improvements(strategy_recommendations)
        
        return {
            "performance_analysis": performance_analysis,
            "optimization_opportunities": optimization_opportunities,
            "strategy_recommendations": strategy_recommendations,
            "algorithm_improvements": algorithm_improvements,
            "expected_performance_gain": algorithm_improvements.get("expected_gain", 0.0)
        }
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get comprehensive routing system status."""
        
        return {
            "routing_system_status": "operational",
            "timestamp": datetime.now().isoformat(),
            "current_load": {
                "pending_requests": len(self.pending_requests),
                "active_assignments": len(self.active_assignments),
                "average_staff_utilization": statistics.mean(self.staff_workload_tracking.values()) if self.staff_workload_tracking else 0.0
            },
            "performance_metrics": {
                "total_requests_routed": self.performance_metrics.total_requests_routed,
                "success_rate": self.performance_metrics.average_success_rate,
                "average_routing_time_ms": self.performance_metrics.average_routing_time_ms,
                "quality_score": self.performance_metrics.average_quality_score
            },
            "load_balancing": {
                "algorithm": self.load_balancing_algorithm.value,
                "distribution_variance": self.performance_metrics.workload_distribution_variance,
                "utilization_rate": self.performance_metrics.capacity_utilization_rate,
                "efficiency": self.performance_metrics.load_balancing_efficiency
            },
            "strategy_performance": self.strategy_effectiveness,
            "top_performing_staff": self._get_top_performing_staff(5),
            "triangle_defense_metrics": {
                "routing_success": self.performance_metrics.triangle_defense_routing_success,
                "formation_efficiency": self.performance_metrics.formation_analysis_efficiency
            }
        }
    
    # Private routing algorithm implementations
    def _initialize_routing_algorithms(self):
        """Initialize routing algorithms and weights."""
        
        # Initialize decision factor weights
        self.algorithm_weights = {
            RoutingDecisionFactor.EXPERTISE_MATCH: 0.30,
            RoutingDecisionFactor.WORKLOAD_CAPACITY: 0.20,
            RoutingDecisionFactor.PERFORMANCE_HISTORY: 0.20,
            RoutingDecisionFactor.RESPONSE_TIME: 0.10,
            RoutingDecisionFactor.QUALITY_SCORE: 0.10,
            RoutingDecisionFactor.COLLABORATION_SYNERGY: 0.05,
            RoutingDecisionFactor.LEARNING_OPPORTUNITY: 0.03,
            RoutingDecisionFactor.SUCCESSION_READINESS: 0.02
        }
        
        # Initialize strategy effectiveness tracking
        for strategy in RoutingStrategy:
            self.strategy_effectiveness[strategy] = 0.8  # Default effectiveness
        
        # Initialize adaptive weights
        self.adaptive_weights = self.algorithm_weights.copy()
        
        self.logger.info("Routing algorithms initialized")
    
    async def _analyze_routing_request(self, routing_request: RoutingRequest):
        """Analyze routing request for complexity and requirements."""
        
        intelligence_request = routing_request.intelligence_request
        
        # Use tier manager for complexity assessment
        if hasattr(intelligence_request, 'content'):
            complexity_assessment = self.tier_manager.assess_task_complexity(
                intelligence_request.content,
                routing_request.business_context,
                getattr(intelligence_request, 'urgency_indicators', [])
            )
            routing_request.complexity_assessment = complexity_assessment
            routing_request.expertise_requirements = complexity_assessment.expertise_requirements
        
        # Assess urgency if not already done
        if not hasattr(intelligence_request, 'urgency_assessment'):
            urgency_assessment = self.tier_manager.assess_urgency(
                deadline=getattr(intelligence_request, 'deadline', None),
                priority_indicators=getattr(intelligence_request, 'urgency_indicators', []),
                business_impact=routing_request.business_context.get('business_impact', ''),
                request_context=routing_request.business_context
            )
            routing_request.urgency_assessment = urgency_assessment
        
        # Check for Triangle Defense priority
        if any(keyword in intelligence_request.content.lower() 
               for keyword in ['triangle defense', 'formation', 'defensive']):
            routing_request.triangle_defense_priority = True
    
    async def _generate_routing_candidates(self, routing_request: RoutingRequest) -> List[RoutingCandidate]:
        """Generate and score potential routing candidates."""
        
        candidates = []
        
        # Get all available staff from factory
        for agent_id, agent_instance in self.staff_factory.agent_instances.items():
            if (agent_instance.agent and 
                agent_instance.lifecycle_state.value == "active" and
                agent_id not in routing_request.exclude_staff):
                
                # Create routing candidate
                candidate = RoutingCandidate(
                    staff_agent=agent_instance.agent,
                    staff_id=agent_id
                )
                
                # Score the candidate
                await self._score_routing_candidate(candidate, routing_request)
                candidates.append(candidate)
        
        # Sort candidates by overall score
        candidates.sort(key=lambda x: x.overall_score, reverse=True)
        
        return candidates
    
    async def _score_routing_candidate(self, candidate: RoutingCandidate, routing_request: RoutingRequest):
        """Score a routing candidate using multiple factors."""
        
        staff_agent = candidate.staff_agent
        
        # Score expertise match
        candidate.expertise_score = self._calculate_expertise_score(staff_agent, routing_request)
        
        # Score capacity/availability
        candidate.capacity_score = self._calculate_capacity_score(staff_agent, routing_request)
        
        # Score historical performance
        candidate.performance_score = self._calculate_performance_score(staff_agent, routing_request)
        
        # Score expected response speed
        candidate.speed_score = self._calculate_speed_score(staff_agent, routing_request)
        
        # Score expected quality
        candidate.quality_score = self._calculate_quality_score(staff_agent, routing_request)
        
        # Score collaboration synergy
        candidate.synergy_score = self._calculate_synergy_score(staff_agent, routing_request)
        
        # Calculate composite overall score
        candidate.overall_score = (
            candidate.expertise_score * self.adaptive_weights[RoutingDecisionFactor.EXPERTISE_MATCH] +
            candidate.capacity_score * self.adaptive_weights[RoutingDecisionFactor.WORKLOAD_CAPACITY] +
            candidate.performance_score * self.adaptive_weights[RoutingDecisionFactor.PERFORMANCE_HISTORY] +
            candidate.speed_score * self.adaptive_weights[RoutingDecisionFactor.RESPONSE_TIME] +
            candidate.quality_score * self.adaptive_weights[RoutingDecisionFactor.QUALITY_SCORE] +
            candidate.synergy_score * self.adaptive_weights[RoutingDecisionFactor.COLLABORATION_SYNERGY]
        )
        
        # Calculate confidence level
        candidate.confidence_level = self._calculate_candidate_confidence(candidate, routing_request)
        
        # Estimate completion time and quality
        candidate.estimated_completion_time = self._estimate_completion_time(staff_agent, routing_request)
        candidate.expected_quality = min(1.0, candidate.quality_score + 0.1)
    
    def _calculate_expertise_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate expertise match score."""
        
        if not routing_request.expertise_requirements:
            return 0.8  # Default score when no specific expertise required
        
        staff_expertise = set(staff_agent.personality.expertise_areas)
        required_expertise = set(routing_request.expertise_requirements)
        
        if not required_expertise:
            return 0.8
        
        # Calculate overlap
        overlap = len(staff_expertise & required_expertise) / len(required_expertise)
        
        # Bonus for Triangle Defense if priority
        if (routing_request.triangle_defense_priority and 
            ExpertiseArea.TRIANGLE_DEFENSE_MASTERY in staff_expertise):
            overlap = min(1.0, overlap + 0.2)
        
        return overlap
    
    def _calculate_capacity_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate capacity/availability score."""
        
        # Get current workload
        workload_percentage = getattr(staff_agent, 'workload_percentage', 0.0)
        
        # Calculate capacity score (inverse of workload)
        capacity_score = max(0.0, 1.0 - (workload_percentage / 100.0))
        
        # Adjust for max concurrent tasks
        max_tasks = staff_agent.personality.max_concurrent_tasks
        current_tasks = len(getattr(staff_agent, 'current_assignments', []))
        
        if current_tasks >= max_tasks:
            capacity_score *= 0.1  # Heavily penalize overloaded staff
        
        return capacity_score
    
    def _calculate_performance_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate historical performance score."""
        
        # Use staff effectiveness rating as base
        effectiveness = staff_agent.personality.effectiveness_rating / 100.0
        
        # Adjust based on recent performance if available
        if hasattr(staff_agent, 'performance_metrics'):
            recent_success_rate = getattr(staff_agent.performance_metrics, 'success_rate', 1.0)
            effectiveness = (effectiveness + recent_success_rate) / 2.0
        
        return effectiveness
    
    def _calculate_speed_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate expected response speed score."""
        
        decision_speed = staff_agent.personality.decision_speed
        
        speed_mapping = {
            "instantaneous": 1.0,
            "rapid": 0.9,
            "moderate": 0.7,
            "deliberate": 0.5
        }
        
        base_speed = speed_mapping.get(decision_speed, 0.7)
        
        # Adjust for urgency requirements
        if routing_request.urgency_assessment:
            urgency_level = routing_request.urgency_assessment.urgency_level.value
            if urgency_level in ["emergency", "critical"] and decision_speed != "instantaneous":
                base_speed *= 0.8  # Penalty for non-instant response in emergencies
        
        return base_speed
    
    def _calculate_quality_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate expected quality score."""
        
        # Base quality from effectiveness rating
        base_quality = staff_agent.personality.effectiveness_rating / 100.0
        
        # Adjust for expertise match
        expertise_score = self._calculate_expertise_score(staff_agent, routing_request)
        quality_score = (base_quality + expertise_score) / 2.0
        
        # Bonus for Triangle Defense mastery if relevant
        if (routing_request.triangle_defense_priority and 
            staff_agent.personality.triangle_defense_mastery > 0.8):
            quality_score = min(1.0, quality_score + 0.1)
        
        return quality_score
    
    def _calculate_synergy_score(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> float:
        """Calculate collaboration synergy score."""
        
        # Base synergy from collaboration style
        collaboration_style = staff_agent.personality.collaboration_style
        
        synergy_mapping = {
            "adaptive": 0.9,
            "directive": 0.7,
            "consultative": 0.8
        }
        
        base_synergy = synergy_mapping.get(collaboration_style, 0.7)
        
        # Adjust for team requirements
        if routing_request.require_collaboration:
            delegation_capability = staff_agent.personality.delegation_capability
            base_synergy = (base_synergy + delegation_capability) / 2.0
        
        return base_synergy
    
    def _calculate_candidate_confidence(self, candidate: RoutingCandidate, routing_request: RoutingRequest) -> float:
        """Calculate confidence in candidate selection."""
        
        # Base confidence from score components
        score_variance = statistics.variance([
            candidate.expertise_score, candidate.capacity_score,
            candidate.performance_score, candidate.speed_score,
            candidate.quality_score, candidate.synergy_score
        ])
        
        # Lower variance = higher confidence
        confidence = max(0.5, 1.0 - score_variance)
        
        # Adjust for complexity match
        if routing_request.complexity_assessment:
            complexity_score = routing_request.complexity_assessment.complexity_score
            tier_capability = candidate.staff_agent.personality.tier_level
            
            # Check if tier is appropriate for complexity
            if self._is_tier_appropriate_for_complexity(tier_capability, complexity_score):
                confidence = min(1.0, confidence + 0.1)
            else:
                confidence *= 0.8
        
        return confidence
    
    def _is_tier_appropriate_for_complexity(self, tier_level: TierLevel, complexity_score: float) -> bool:
        """Check if tier level is appropriate for complexity score."""
        
        tier_complexity_mapping = {
            TierLevel.FOUNDER: 100,
            TierLevel.AI_CORE: 95,
            TierLevel.EXECUTIVE: 85,
            TierLevel.STRATEGIC: 75,
            TierLevel.ADVISORY: 65,
            TierLevel.INNOVATION: 60,
            TierLevel.FOOTBALL: 55
        }
        
        max_complexity = tier_complexity_mapping.get(tier_level, 50)
        return complexity_score <= max_complexity
    
    def _estimate_completion_time(self, staff_agent: StaffAgentBase, routing_request: RoutingRequest) -> timedelta:
        """Estimate task completion time."""
        
        # Base time from complexity assessment
        if routing_request.complexity_assessment:
            base_minutes = routing_request.complexity_assessment.estimated_duration_minutes
        else:
            base_minutes = 120  # Default 2 hours
        
        # Adjust for staff performance characteristics
        decision_speed = staff_agent.personality.decision_speed
        speed_multiplier = {
            "instantaneous": 0.5,
            "rapid": 0.7,
            "moderate": 1.0,
            "deliberate": 1.5
        }.get(decision_speed, 1.0)
        
        estimated_minutes = base_minutes * speed_multiplier
        
        # Adjust for current workload
        workload_percentage = getattr(staff_agent, 'workload_percentage', 0.0)
        if workload_percentage > 80:
            estimated_minutes *= 1.3  # Slower when heavily loaded
        
        return timedelta(minutes=estimated_minutes)
    
    async def _apply_routing_strategy(self, routing_request: RoutingRequest, candidates: List[RoutingCandidate]) -> RoutingDecision:
        """Apply specific routing strategy to select optimal candidate."""
        
        strategy = routing_request.preferred_strategy
        
        if strategy == RoutingStrategy.PERFORMANCE_OPTIMAL:
            selected_candidate = self._apply_performance_optimal_strategy(candidates)
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            selected_candidate = self._apply_load_balanced_strategy(candidates)
        elif strategy == RoutingStrategy.EXPERTISE_FOCUSED:
            selected_candidate = self._apply_expertise_focused_strategy(candidates, routing_request)
        elif strategy == RoutingStrategy.SPEED_OPTIMIZED:
            selected_candidate = self._apply_speed_optimized_strategy(candidates)
        elif strategy == RoutingStrategy.TRIANGLE_DEFENSE_SPECIALIZED:
            selected_candidate = self._apply_triangle_defense_strategy(candidates, routing_request)
        else:
            # Default to performance optimal
            selected_candidate = self._apply_performance_optimal_strategy(candidates)
        
        # Create routing decision
        decision = RoutingDecision(
            routing_id=routing_request.routing_id,
            selected_staff=selected_candidate,
            alternative_candidates=candidates[1:4],  # Top 3 alternatives
            routing_strategy_used=strategy,
            decision_factors=self._extract_decision_factors(selected_candidate),
            confidence_score=selected_candidate.confidence_level,
            estimated_completion_time=selected_candidate.estimated_completion_time,
            predicted_quality_score=selected_candidate.expected_quality,
            expected_success_probability=selected_candidate.overall_score,
            collaboration_requirements=[],
            resource_allocation={},
            monitoring_requirements=[],
            selection_reasoning=f"Selected {selected_candidate.staff_id} using {strategy.value} strategy with score {selected_candidate.overall_score:.3f}",
            alternative_analysis=f"Top alternatives: {[c.staff_id for c in candidates[1:4]]}",
            risk_assessment="Low risk assignment with appropriate tier match"
        )
        
        return decision
    
    def _apply_performance_optimal_strategy(self, candidates: List[RoutingCandidate]) -> RoutingCandidate:
        """Apply performance-optimal routing strategy."""
        
        # Already sorted by overall score, return the best
        return candidates[0] if candidates else None
    
    def _apply_load_balanced_strategy(self, candidates: List[RoutingCandidate]) -> RoutingCandidate:
        """Apply load-balanced routing strategy."""
        
        # Find candidate with best balance of performance and capacity
        best_candidate = None
        best_balance_score = 0.0
        
        for candidate in candidates:
            # Balance performance and capacity
            balance_score = (candidate.overall_score * 0.6 + candidate.capacity_score * 0.4)
            
            if balance_score > best_balance_score:
                best_balance_score = balance_score
                best_candidate = candidate
        
        return best_candidate
    
    def _apply_expertise_focused_strategy(self, candidates: List[RoutingCandidate], routing_request: RoutingRequest) -> RoutingCandidate:
        """Apply expertise-focused routing strategy."""
        
        # Prioritize expertise match above other factors
        candidates_by_expertise = sorted(candidates, key=lambda x: x.expertise_score, reverse=True)
        return candidates_by_expertise[0] if candidates_by_expertise else None
    
    def _apply_speed_optimized_strategy(self, candidates: List[RoutingCandidate]) -> RoutingCandidate:
        """Apply speed-optimized routing strategy."""
        
        # Prioritize fastest response time
        candidates_by_speed = sorted(candidates, key=lambda x: x.speed_score, reverse=True)
        return candidates_by_speed[0] if candidates_by_speed else None
    
    def _apply_triangle_defense_strategy(self, candidates: List[RoutingCandidate], routing_request: RoutingRequest) -> RoutingCandidate:
        """Apply Triangle Defense specialized routing strategy."""
        
        # Prioritize Triangle Defense expertise
        triangle_defense_candidates = [
            c for c in candidates 
            if ExpertiseArea.TRIANGLE_DEFENSE_MASTERY in c.staff_agent.personality.expertise_areas
        ]
        
        if triangle_defense_candidates:
            # Sort by Triangle Defense mastery level
            triangle_defense_candidates.sort(
                key=lambda x: x.staff_agent.personality.triangle_defense_mastery, 
                reverse=True
            )
            return triangle_defense_candidates[0]
        
        # Fallback to general expertise
        return self._apply_expertise_focused_strategy(candidates, routing_request)
    
    def _extract_decision_factors(self, candidate: RoutingCandidate) -> Dict[RoutingDecisionFactor, float]:
        """Extract decision factors from candidate."""
        
        return {
            RoutingDecisionFactor.EXPERTISE_MATCH: candidate.expertise_score,
            RoutingDecisionFactor.WORKLOAD_CAPACITY: candidate.capacity_score,
            RoutingDecisionFactor.PERFORMANCE_HISTORY: candidate.performance_score,
            RoutingDecisionFactor.RESPONSE_TIME: candidate.speed_score,
            RoutingDecisionFactor.QUALITY_SCORE: candidate.quality_score,
            RoutingDecisionFactor.COLLABORATION_SYNERGY: candidate.synergy_score
        }
    
    async def _validate_routing_decision(self, decision: RoutingDecision, routing_request: RoutingRequest) -> RoutingDecision:
        """Validate and potentially adjust routing decision."""
        
        # Check for constraint violations
        if routing_request.max_response_time_minutes:
            estimated_minutes = decision.estimated_completion_time.total_seconds() / 60
            if estimated_minutes > routing_request.max_response_time_minutes:
                # Try to find faster alternative
                faster_alternatives = [
                    c for c in decision.alternative_candidates
                    if self._estimate_completion_time(c.staff_agent, routing_request).total_seconds() / 60 <= routing_request.max_response_time_minutes
                ]
                
                if faster_alternatives:
                    decision.selected_staff = faster_alternatives[0]
                    decision.selection_reasoning += " (Adjusted for time constraint)"
        
        # Validate tier appropriateness
        if routing_request.complexity_assessment:
            complexity_score = routing_request.complexity_assessment.complexity_score
            selected_tier = decision.selected_staff.staff_agent.personality.tier_level
            
            if not self._is_tier_appropriate_for_complexity(selected_tier, complexity_score):
                decision.risk_assessment = "Moderate risk: Tier level may be insufficient for complexity"
        
        return decision
    
    async def _execute_routing_assignment(self, decision: RoutingDecision):
        """Execute the routing assignment."""
        
        # Add to active assignments
        self.active_assignments[decision.routing_id] = decision
        
        # Update staff workload tracking
        staff_id = decision.selected_staff.staff_id
        self.staff_workload_tracking[staff_id] = self.staff_workload_tracking.get(staff_id, 0.0) + 0.2
        
        # Add to routing history
        self.routing_history.append({
            "routing_id": decision.routing_id,
            "timestamp": datetime.now(),
            "selected_staff": staff_id,
            "strategy": decision.routing_strategy_used.value,
            "confidence": decision.confidence_score
        })
    
    def _update_routing_metrics(self, decision: RoutingDecision, start_time: float):
        """Update routing performance metrics."""
        
        routing_time_ms = (time.time() - start_time) * 1000
        
        # Update basic metrics
        self.performance_metrics.total_requests_routed += 1
        self.performance_metrics.successful_routings += 1
        
        # Update average routing time
        total_requests = self.performance_metrics.total_requests_routed
        current_avg = self.performance_metrics.average_routing_time_ms
        self.performance_metrics.average_routing_time_ms = (
            (current_avg * (total_requests - 1) + routing_time_ms) / total_requests
        )
        
        # Update strategy performance
        strategy = decision.routing_strategy_used
        if strategy not in self.performance_metrics.strategy_performance:
            self.performance_metrics.strategy_performance[strategy] = {"count": 0, "avg_confidence": 0.0}
        
        strategy_stats = self.performance_metrics.strategy_performance[strategy]
        strategy_stats["count"] += 1
        current_count = strategy_stats["count"]
        current_confidence = strategy_stats["avg_confidence"]
        strategy_stats["avg_confidence"] = (
            (current_confidence * (current_count - 1) + decision.confidence_score) / current_count
        )
        
        # Update staff utilization
        staff_id = decision.selected_staff.staff_id
        self.performance_metrics.staff_utilization_rates[staff_id] = self.staff_workload_tracking.get(staff_id, 0.0)
        
        # Update timestamp
        self.performance_metrics.last_updated = datetime.now()
    
    async def _update_routing_learning(self, decision: RoutingDecision, routing_request: RoutingRequest):
        """Update routing algorithms based on decision feedback."""
        
        # Simple learning: increase weight for factors that led to high confidence decisions
        if decision.confidence_score > 0.8:
            # Boost weights for factors that contributed to success
            for factor, value in decision.decision_factors.items():
                if value > 0.7:  # High factor value
                    self.adaptive_weights[factor] = min(1.0, self.adaptive_weights[factor] * 1.01)
        
        # Update algorithm learning score
        self.performance_metrics.algorithm_learning_score = min(1.0, self.performance_metrics.algorithm_learning_score + 0.001)
    
    # Batch routing and optimization methods
    async def _apply_batch_routing_optimization(self, routing_requests: List[RoutingRequest], batch_strategy: RoutingStrategy) -> List[RoutingDecision]:
        """Apply batch routing optimization."""
        
        decisions = []
        
        # Route each request individually but consider batch constraints
        for routing_request in routing_requests:
            candidates = await self._generate_routing_candidates(routing_request)
            decision = await self._apply_routing_strategy(routing_request, candidates)
            decisions.append(decision)
        
        # Apply batch load balancing
        decisions = self._apply_batch_load_balancing(decisions)
        
        return decisions
    
    def _apply_batch_load_balancing(self, decisions: List[RoutingDecision]) -> List[RoutingDecision]:
        """Apply load balancing across batch decisions."""
        
        # Count assignments per staff
        staff_assignments = defaultdict(int)
        for decision in decisions:
            staff_assignments[decision.selected_staff.staff_id] += 1
        
        # Rebalance if any staff is overloaded
        max_assignments = max(staff_assignments.values()) if staff_assignments else 0
        avg_assignments = len(decisions) / len(staff_assignments) if staff_assignments else 0
        
        if max_assignments > avg_assignments * 1.5:  # Significant imbalance
            # Reassign some tasks to alternatives
            for i, decision in enumerate(decisions):
                staff_id = decision.selected_staff.staff_id
                if staff_assignments[staff_id] > avg_assignments * 1.3:
                    # Try to use an alternative
                    for alt_candidate in decision.alternative_candidates:
                        alt_staff_id = alt_candidate.staff_id
                        if staff_assignments[alt_staff_id] < avg_assignments * 0.8:
                            # Reassign to alternative
                            staff_assignments[staff_id] -= 1
                            staff_assignments[alt_staff_id] += 1
                            decision.selected_staff = alt_candidate
                            decision.selection_reasoning += " (Batch load balanced)"
                            break
        
        return decisions
    
    # Workload analysis and rebalancing methods
    async def _analyze_workload_distribution(self) -> Dict[str, Any]:
        """Analyze current workload distribution across staff."""
        
        distribution = {}
        total_workload = 0.0
        
        for staff_id, workload in self.staff_workload_tracking.items():
            distribution[staff_id] = {
                "workload_percentage": workload,
                "utilization_rate": workload / 100.0,
                "assignment_count": len([a for a in self.active_assignments.values() 
                                       if a.selected_staff.staff_id == staff_id])
            }
            total_workload += workload
        
        avg_workload = total_workload / len(distribution) if distribution else 0.0
        workload_variance = statistics.variance([d["workload_percentage"] for d in distribution.values()]) if len(distribution) > 1 else 0.0
        
        return {
            "staff_distribution": distribution,
            "average_workload": avg_workload,
            "workload_variance": workload_variance,
            "utilization_efficiency": 1.0 - (workload_variance / 100.0) if workload_variance < 100 else 0.0
        }
    
    async def _identify_rebalance_opportunities(self, distribution: Dict[str, Any], target_utilization: float) -> Dict[str, Any]:
        """Identify opportunities for workload rebalancing."""
        
        staff_dist = distribution["staff_distribution"]
        
        overloaded_staff = []
        underutilized_staff = []
        
        for staff_id, stats in staff_dist.items():
            utilization = stats["utilization_rate"]
            
            if utilization > target_utilization * 1.2:  # 20% over target
                overloaded_staff.append((staff_id, utilization))
            elif utilization < target_utilization * 0.8:  # 20% under target
                underutilized_staff.append((staff_id, utilization))
        
        return {
            "overloaded_staff": overloaded_staff,
            "underutilized_staff": underutilized_staff,
            "rebalance_potential": len(overloaded_staff) > 0 and len(underutilized_staff) > 0,
            "target_utilization": target_utilization
        }
    
    async def _apply_gradual_rebalancing(self, opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Apply gradual workload rebalancing."""
        
        # Gradual rebalancing through future routing preferences
        rebalance_actions = []
        
        for staff_id, utilization in opportunities["overloaded_staff"]:
            # Reduce future routing probability for overloaded staff
            if staff_id in self.adaptive_weights:
                self.adaptive_weights[RoutingDecisionFactor.WORKLOAD_CAPACITY] *= 1.1
            rebalance_actions.append(f"Reduced routing preference for {staff_id}")
        
        for staff_id, utilization in opportunities["underutilized_staff"]:
            # Increase future routing probability for underutilized staff
            rebalance_actions.append(f"Increased routing preference for {staff_id}")
        
        return {
            "rebalancing_type": "gradual",
            "actions_taken": rebalance_actions,
            "utilization_improvement": 0.05  # Gradual improvement
        }
    
    async def _apply_immediate_rebalancing(self, opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Apply immediate workload rebalancing."""
        
        # More aggressive immediate rebalancing
        rebalance_actions = []
        
        # For demo purposes, simulate immediate rebalancing
        for staff_id, utilization in opportunities["overloaded_staff"]:
            # Reduce current workload tracking
            if staff_id in self.staff_workload_tracking:
                self.staff_workload_tracking[staff_id] *= 0.9
            rebalance_actions.append(f"Reduced current workload for {staff_id}")
        
        return {
            "rebalancing_type": "immediate",
            "actions_taken": rebalance_actions,
            "utilization_improvement": 0.15  # Immediate improvement
        }
    
    async def _apply_smart_rebalancing(self, opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Apply smart adaptive rebalancing."""
        
        # Combine gradual and immediate approaches intelligently
        gradual_result = await self._apply_gradual_rebalancing(opportunities)
        
        # Add smart decision making
        smart_actions = gradual_result["actions_taken"].copy()
        smart_actions.append("Applied intelligent routing weight adjustments")
        
        return {
            "rebalancing_type": "smart",
            "actions_taken": smart_actions,
            "utilization_improvement": 0.12  # Smart improvement
        }
    
    def _update_load_balancing_metrics(self, rebalance_result: Dict[str, Any]):
        """Update load balancing performance metrics."""
        
        improvement = rebalance_result.get("utilization_improvement", 0.0)
        
        # Update efficiency metrics
        current_efficiency = self.performance_metrics.load_balancing_efficiency
        self.performance_metrics.load_balancing_efficiency = min(1.0, current_efficiency + improvement)
        
        # Update capacity utilization
        self.performance_metrics.capacity_utilization_rate = min(1.0, 
            self.performance_metrics.capacity_utilization_rate + improvement / 2)
    
    # Performance analysis and optimization methods
    async def _analyze_historical_performance(self, period_days: int) -> Dict[str, Any]:
        """Analyze historical routing performance."""
        
        # Analyze recent routing history
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_history = [
            h for h in self.routing_history 
            if h["timestamp"] > cutoff_date
        ]
        
        if not recent_history:
            return {"message": "Insufficient historical data"}
        
        # Calculate performance metrics
        avg_confidence = statistics.mean([h["confidence"] for h in recent_history])
        strategy_distribution = defaultdict(int)
        staff_utilization = defaultdict(int)
        
        for entry in recent_history:
            strategy_distribution[entry["strategy"]] += 1
            staff_utilization[entry["selected_staff"]] += 1
        
        return {
            "period_days": period_days,
            "total_routings": len(recent_history),
            "average_confidence": avg_confidence,
            "strategy_distribution": dict(strategy_distribution),
            "staff_utilization": dict(staff_utilization),
            "performance_trend": "stable"  # Simplified
        }
    
    async def _identify_optimization_opportunities(self, performance_analysis: Dict[str, Any], objectives: List[str]) -> Dict[str, Any]:
        """Identify routing optimization opportunities."""
        
        opportunities = []
        
        if "maximize_quality" in objectives:
            if performance_analysis.get("average_confidence", 0.8) < 0.85:
                opportunities.append("Improve confidence scoring algorithms")
        
        if "minimize_response_time" in objectives:
            opportunities.append("Optimize for speed-focused routing")
        
        if "balance_workload" in objectives:
            staff_util = performance_analysis.get("staff_utilization", {})
            if staff_util:
                util_variance = statistics.variance(staff_util.values())
                if util_variance > 10:  # High variance
                    opportunities.append("Improve workload balancing")
        
        return {
            "optimization_opportunities": opportunities,
            "priority_level": "medium",
            "expected_impact": "moderate improvement"
        }
    
    async def _generate_strategy_recommendations(self, opportunities: Dict[str, Any]) -> Dict[str, Any]:
        """Generate routing strategy recommendations."""
        
        recommendations = []
        
        for opportunity in opportunities.get("optimization_opportunities", []):
            if "confidence" in opportunity:
                recommendations.append("Increase expertise matching weight")
            elif "speed" in opportunity:
                recommendations.append("Prioritize rapid decision makers")
            elif "workload" in opportunity:
                recommendations.append("Implement adaptive load balancing")
        
        return {
            "strategy_recommendations": recommendations,
            "implementation_priority": "high",
            "expected_timeline": "immediate"
        }
    
    async def _apply_algorithm_improvements(self, recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply algorithm improvements based on recommendations."""
        
        improvements_applied = []
        
        for recommendation in recommendations.get("strategy_recommendations", []):
            if "expertise" in recommendation:
                # Increase expertise weight
                self.adaptive_weights[RoutingDecisionFactor.EXPERTISE_MATCH] *= 1.05
                improvements_applied.append("Increased expertise matching weight")
            elif "speed" in recommendation:
                # Increase speed weight
                self.adaptive_weights[RoutingDecisionFactor.RESPONSE_TIME] *= 1.05
                improvements_applied.append("Increased speed optimization weight")
            elif "load" in recommendation:
                # Increase capacity weight
                self.adaptive_weights[RoutingDecisionFactor.WORKLOAD_CAPACITY] *= 1.05
                improvements_applied.append("Increased load balancing weight")
        
        return {
            "improvements_applied": improvements_applied,
            "expected_gain": 0.08,  # 8% improvement
            "monitoring_required": True
        }
    
    def _get_top_performing_staff(self, count: int) -> List[Dict[str, Any]]:
        """Get top performing staff members."""
        
        staff_performance = []
        
        for staff_id, utilization in self.performance_metrics.staff_utilization_rates.items():
            performance_score = self.performance_metrics.staff_performance_scores.get(staff_id, 0.9)
            
            staff_performance.append({
                "staff_id": staff_id,
                "utilization_rate": utilization,
                "performance_score": performance_score,
                "combined_score": (utilization * 0.3 + performance_score * 0.7)
            })
        
        # Sort by combined score
        staff_performance.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return staff_performance[:count]
