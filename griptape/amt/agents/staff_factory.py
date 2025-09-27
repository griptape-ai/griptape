"""
AMT Staff Factory - Comprehensive agent creation and management system.

Manages the complete lifecycle of all 25 championship professional agents across
7 organizational tiers with dynamic instantiation, dependency management, health
monitoring, and ecosystem coordination. Supports specialized agent types while
maintaining consistent integration with the intelligence coordination system.
"""

import logging
import asyncio
import importlib
from typing import Dict, List, Optional, Any, Type, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import inspect
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

# Import base components
from .staff_agent_base import (
    StaffAgentBase, StaffPersonality, EmergencyPriority, PersonalityType,
    ResponseMode, StaffPerformanceMetrics
)
from .mel_agent import MELAgent

# Import intelligence components
from ..intelligence import (
    TierLevel, ExpertiseArea, StaffStatus, IntelligenceCoordinator,
    StaffRegistry, TierManager, AirtableBridge, GraphQLFederationClient
)


class AgentType(Enum):
    """Types of agents that can be created by the factory."""
    FOUNDER_AUTHORITY = "founder_authority"         # Denauld Brown - Ultimate authority
    AI_CORE = "ai_core"                            # M.E.L. - AI coordination
    EXECUTIVE_LEADERSHIP = "executive_leadership"   # CEO, COO level leadership
    STRATEGIC_LEADERSHIP = "strategic_leadership"   # Strategic planning and vision
    ADVISORY_COMMUNICATIONS = "advisory_communications" # Advisory and communications
    INNOVATION_TECHNICAL = "innovation_technical"   # Innovation and technical specialists
    FOOTBALL_OPERATIONS = "football_operations"     # Football operations and analytics


class AgentLifecycleState(Enum):
    """Agent lifecycle states."""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ERROR = "error"
    TERMINATING = "terminating"
    TERMINATED = "terminated"


class AgentCreationStrategy(Enum):
    """Strategies for agent creation."""
    IMMEDIATE = "immediate"         # Create immediately
    LAZY = "lazy"                  # Create on first access
    BATCH = "batch"                # Create in batches
    DEPENDENCY_ORDERED = "dependency_ordered"  # Create based on dependencies


@dataclass
class AgentSpecification:
    """Complete specification for creating an agent."""
    
    # Agent Identity
    agent_id: str
    agent_type: AgentType
    implementation_class: Optional[str] = None  # Custom implementation class name
    
    # Personality Configuration
    full_name: str = ""
    nickname: str = ""
    position: str = ""
    department: str = ""
    tier_level: TierLevel = TierLevel.FOOTBALL
    emergency_priority: EmergencyPriority = EmergencyPriority.FOOTBALL_OPERATIONS
    personality_type: PersonalityType = PersonalityType.OPERATIONAL_EXCELLENCE
    
    # Professional Attributes
    expertise_areas: List[ExpertiseArea] = field(default_factory=list)
    authority_domains: List[str] = field(default_factory=list)
    educational_background: List[str] = field(default_factory=list)
    professional_experience: List[str] = field(default_factory=list)
    
    # Performance Configuration
    effectiveness_rating: float = 95.0
    decision_speed: str = "rapid"
    collaboration_style: str = "adaptive"
    communication_style: str = "direct"
    max_concurrent_tasks: int = 5
    
    # Triangle Defense Integration
    triangle_defense_mastery: float = 0.7
    formation_specializations: List[str] = field(default_factory=list)
    tactical_innovation_score: float = 0.8
    
    # Emergency and Succession
    succession_candidates: List[str] = field(default_factory=list)
    emergency_authority_level: float = 1.0
    nuclear_protocol_clearance: bool = False
    
    # Lifecycle Configuration
    creation_strategy: AgentCreationStrategy = AgentCreationStrategy.IMMEDIATE
    dependencies: List[str] = field(default_factory=list)
    auto_start: bool = True
    health_check_enabled: bool = True


@dataclass
class AgentInstance:
    """Runtime instance information for agents."""
    
    agent_id: str
    specification: AgentSpecification
    agent: Optional[StaffAgentBase] = None
    lifecycle_state: AgentLifecycleState = AgentLifecycleState.UNINITIALIZED
    
    # Runtime State
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    
    # Performance Tracking
    requests_processed: int = 0
    errors_encountered: int = 0
    average_response_time_ms: float = 0.0
    last_activity: Optional[datetime] = None
    
    # Dependencies
    dependency_agents: Set[str] = field(default_factory=set)
    dependent_agents: Set[str] = field(default_factory=set)


class StaffFactory:
    """
    Comprehensive factory for creating and managing all 25 championship professional agents.
    
    Handles dynamic agent creation, lifecycle management, dependency resolution,
    health monitoring, and ecosystem coordination with intelligent resource management
    and performance optimization.
    """
    
    def __init__(self,
                 intelligence_coordinator: Optional[IntelligenceCoordinator] = None,
                 auto_initialize_agents: bool = True,
                 health_check_interval_seconds: int = 300,
                 max_concurrent_creations: int = 5):
        """
        Initialize the staff factory with comprehensive agent management capabilities.
        
        Args:
            intelligence_coordinator: Intelligence coordination system
            auto_initialize_agents: Whether to auto-initialize all agents
            health_check_interval_seconds: Health check frequency
            max_concurrent_creations: Maximum concurrent agent creations
        """
        
        self.intelligence_coordinator = intelligence_coordinator
        self.auto_initialize_agents = auto_initialize_agents
        self.health_check_interval_seconds = health_check_interval_seconds
        self.max_concurrent_creations = max_concurrent_creations
        
        # Agent management
        self.agent_specifications: Dict[str, AgentSpecification] = {}
        self.agent_instances: Dict[str, AgentInstance] = {}
        self.agent_registry: Dict[str, StaffAgentBase] = {}
        
        # Lifecycle management
        self.creation_executor = ThreadPoolExecutor(max_workers=max_concurrent_creations)
        self.health_check_task: Optional[asyncio.Task] = None
        self.factory_state = "initializing"
        
        # Performance tracking
        self.factory_metrics = {
            "agents_created": 0,
            "agents_active": 0,
            "agents_errors": 0,
            "creation_failures": 0,
            "health_checks_performed": 0,
            "average_creation_time_ms": 0.0
        }
        
        # Initialize agent specifications
        self._initialize_agent_specifications()
        
        # Logger
        self.logger = logging.getLogger("AMT.StaffFactory")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Staff Factory initialized with 25 championship professional specifications")
    
    async def initialize_factory(self):
        """Initialize the factory and optionally create all agents."""
        
        self.factory_state = "initializing"
        
        try:
            # Start health monitoring
            if self.health_check_interval_seconds > 0:
                self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            # Auto-initialize agents if configured
            if self.auto_initialize_agents:
                await self.create_all_agents()
            
            self.factory_state = "active"
            self.logger.info("Staff Factory initialization complete")
            
        except Exception as e:
            self.factory_state = "error"
            self.logger.error(f"Factory initialization failed: {str(e)}")
            raise
    
    async def create_agent(self, agent_id: str, **override_kwargs) -> StaffAgentBase:
        """
        Create a specific agent with optional configuration overrides.
        
        Args:
            agent_id: ID of agent to create
            **override_kwargs: Configuration overrides for agent creation
            
        Returns:
            Created and initialized agent instance
        """
        
        if agent_id not in self.agent_specifications:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        if agent_id in self.agent_instances and self.agent_instances[agent_id].agent:
            self.logger.warning(f"Agent {agent_id} already exists, returning existing instance")
            return self.agent_instances[agent_id].agent
        
        spec = self.agent_specifications[agent_id]
        creation_start = datetime.now()
        
        try:
            # Create agent instance tracking
            instance = AgentInstance(
                agent_id=agent_id,
                specification=spec,
                lifecycle_state=AgentLifecycleState.INITIALIZING,
                created_at=creation_start
            )
            self.agent_instances[agent_id] = instance
            
            # Resolve dependencies
            await self._resolve_agent_dependencies(agent_id)
            
            # Create agent personality with overrides
            personality = self._create_agent_personality(spec, override_kwargs)
            
            # Determine agent implementation class
            agent_class = self._determine_agent_class(spec)
            
            # Create agent instance
            agent = await self._instantiate_agent(agent_class, personality, override_kwargs)
            
            # Register agent
            instance.agent = agent
            self.agent_registry[agent_id] = agent
            
            # Update lifecycle state
            instance.lifecycle_state = AgentLifecycleState.ACTIVE
            instance.started_at = datetime.now()
            instance.health_status = "healthy"
            
            # Update metrics
            self.factory_metrics["agents_created"] += 1
            self.factory_metrics["agents_active"] += 1
            
            creation_time = (datetime.now() - creation_start).total_seconds() * 1000
            self._update_creation_time_metric(creation_time)
            
            self.logger.info(f"Agent created successfully: {agent_id} ({spec.full_name}) - {creation_time:.2f}ms")
            return agent
            
        except Exception as e:
            # Handle creation failure
            if agent_id in self.agent_instances:
                self.agent_instances[agent_id].lifecycle_state = AgentLifecycleState.ERROR
            
            self.factory_metrics["creation_failures"] += 1
            self.logger.error(f"Agent creation failed: {agent_id} - {str(e)}")
            raise
    
    async def create_all_agents(self, 
                               creation_strategy: AgentCreationStrategy = AgentCreationStrategy.DEPENDENCY_ORDERED) -> Dict[str, StaffAgentBase]:
        """
        Create all agents using specified creation strategy.
        
        Args:
            creation_strategy: Strategy for agent creation ordering
            
        Returns:
            Dictionary of all created agents
        """
        
        creation_start = datetime.now()
        created_agents = {}
        
        try:
            if creation_strategy == AgentCreationStrategy.IMMEDIATE:
                created_agents = await self._create_all_immediate()
            elif creation_strategy == AgentCreationStrategy.BATCH:
                created_agents = await self._create_all_batch()
            elif creation_strategy == AgentCreationStrategy.DEPENDENCY_ORDERED:
                created_agents = await self._create_all_dependency_ordered()
            else:  # LAZY - no immediate creation
                self.logger.info("Lazy creation strategy - agents will be created on demand")
                return {}
            
            creation_time = (datetime.now() - creation_start).total_seconds()
            self.logger.info(f"All agents created: {len(created_agents)} agents in {creation_time:.2f}s")
            
            return created_agents
            
        except Exception as e:
            self.logger.error(f"Bulk agent creation failed: {str(e)}")
            raise
    
    async def get_agent(self, agent_id: str, auto_create: bool = True) -> Optional[StaffAgentBase]:
        """
        Get agent by ID, optionally creating if it doesn't exist.
        
        Args:
            agent_id: ID of agent to retrieve
            auto_create: Whether to create agent if it doesn't exist
            
        Returns:
            Agent instance or None if not found and auto_create is False
        """
        
        # Return existing agent if available
        if agent_id in self.agent_registry:
            return self.agent_registry[agent_id]
        
        # Auto-create if enabled and specification exists
        if auto_create and agent_id in self.agent_specifications:
            return await self.create_agent(agent_id)
        
        return None
    
    async def get_agents_by_tier(self, tier_level: TierLevel, auto_create: bool = True) -> List[StaffAgentBase]:
        """Get all agents for a specific tier level."""
        
        tier_agents = []
        
        for agent_id, spec in self.agent_specifications.items():
            if spec.tier_level == tier_level:
                agent = await self.get_agent(agent_id, auto_create)
                if agent:
                    tier_agents.append(agent)
        
        return tier_agents
    
    async def get_agents_by_emergency_priority(self, priority: EmergencyPriority, auto_create: bool = True) -> List[StaffAgentBase]:
        """Get all agents for a specific emergency priority level."""
        
        priority_agents = []
        
        for agent_id, spec in self.agent_specifications.items():
            if spec.emergency_priority == priority:
                agent = await self.get_agent(agent_id, auto_create)
                if agent:
                    priority_agents.append(agent)
        
        return priority_agents
    
    async def get_agents_by_expertise(self, expertise: ExpertiseArea, auto_create: bool = True) -> List[StaffAgentBase]:
        """Get all agents with specific expertise area."""
        
        expertise_agents = []
        
        for agent_id, spec in self.agent_specifications.items():
            if expertise in spec.expertise_areas:
                agent = await self.get_agent(agent_id, auto_create)
                if agent:
                    expertise_agents.append(agent)
        
        return expertise_agents
    
    async def suspend_agent(self, agent_id: str) -> bool:
        """Suspend an agent temporarily."""
        
        if agent_id not in self.agent_instances:
            return False
        
        instance = self.agent_instances[agent_id]
        instance.lifecycle_state = AgentLifecycleState.SUSPENDED
        
        self.factory_metrics["agents_active"] -= 1
        self.logger.info(f"Agent suspended: {agent_id}")
        return True
    
    async def resume_agent(self, agent_id: str) -> bool:
        """Resume a suspended agent."""
        
        if agent_id not in self.agent_instances:
            return False
        
        instance = self.agent_instances[agent_id]
        if instance.lifecycle_state == AgentLifecycleState.SUSPENDED:
            instance.lifecycle_state = AgentLifecycleState.ACTIVE
            self.factory_metrics["agents_active"] += 1
            self.logger.info(f"Agent resumed: {agent_id}")
            return True
        
        return False
    
    async def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent and clean up resources."""
        
        if agent_id not in self.agent_instances:
            return False
        
        instance = self.agent_instances[agent_id]
        instance.lifecycle_state = AgentLifecycleState.TERMINATING
        
        try:
            # Remove from registry
            if agent_id in self.agent_registry:
                del self.agent_registry[agent_id]
            
            # Clean up instance
            instance.agent = None
            instance.lifecycle_state = AgentLifecycleState.TERMINATED
            
            # Update metrics
            if instance.lifecycle_state == AgentLifecycleState.ACTIVE:
                self.factory_metrics["agents_active"] -= 1
            
            self.logger.info(f"Agent terminated: {agent_id}")
            return True
            
        except Exception as e:
            instance.lifecycle_state = AgentLifecycleState.ERROR
            self.logger.error(f"Agent termination failed: {agent_id} - {str(e)}")
            return False
    
    async def restart_agent(self, agent_id: str, **override_kwargs) -> Optional[StaffAgentBase]:
        """Restart an agent with optional configuration changes."""
        
        await self.terminate_agent(agent_id)
        return await self.create_agent(agent_id, **override_kwargs)
    
    def get_factory_status(self) -> Dict[str, Any]:
        """Get comprehensive factory status and metrics."""
        
        return {
            "factory_state": self.factory_state,
            "timestamp": datetime.now().isoformat(),
            "agent_summary": {
                "total_specifications": len(self.agent_specifications),
                "total_instances": len(self.agent_instances),
                "active_agents": len([i for i in self.agent_instances.values() 
                                    if i.lifecycle_state == AgentLifecycleState.ACTIVE]),
                "suspended_agents": len([i for i in self.agent_instances.values() 
                                       if i.lifecycle_state == AgentLifecycleState.SUSPENDED]),
                "error_agents": len([i for i in self.agent_instances.values() 
                                   if i.lifecycle_state == AgentLifecycleState.ERROR])
            },
            "performance_metrics": self.factory_metrics.copy(),
            "health_monitoring": {
                "enabled": self.health_check_task is not None,
                "interval_seconds": self.health_check_interval_seconds,
                "last_health_check": max([i.last_health_check for i in self.agent_instances.values() 
                                        if i.last_health_check], default=None)
            },
            "tier_distribution": self._get_tier_distribution(),
            "emergency_priority_distribution": self._get_emergency_priority_distribution()
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status for specific agent."""
        
        if agent_id not in self.agent_instances:
            return None
        
        instance = self.agent_instances[agent_id]
        spec = instance.specification
        
        return {
            "agent_id": agent_id,
            "specification": {
                "full_name": spec.full_name,
                "nickname": spec.nickname,
                "position": spec.position,
                "tier_level": spec.tier_level.value,
                "emergency_priority": spec.emergency_priority.value,
                "agent_type": spec.agent_type.value
            },
            "lifecycle": {
                "state": instance.lifecycle_state.value,
                "created_at": instance.created_at.isoformat() if instance.created_at else None,
                "started_at": instance.started_at.isoformat() if instance.started_at else None,
                "health_status": instance.health_status,
                "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None
            },
            "performance": {
                "requests_processed": instance.requests_processed,
                "errors_encountered": instance.errors_encountered,
                "average_response_time_ms": instance.average_response_time_ms,
                "last_activity": instance.last_activity.isoformat() if instance.last_activity else None
            },
            "dependencies": {
                "dependency_agents": list(instance.dependency_agents),
                "dependent_agents": list(instance.dependent_agents)
            },
            "agent_available": instance.agent is not None
        }
    
    async def shutdown_factory(self):
        """Shutdown the factory and all agents gracefully."""
        
        self.factory_state = "shutting_down"
        
        try:
            # Stop health monitoring
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            # Terminate all agents
            termination_tasks = []
            for agent_id in list(self.agent_instances.keys()):
                termination_tasks.append(self.terminate_agent(agent_id))
            
            if termination_tasks:
                await asyncio.gather(*termination_tasks, return_exceptions=True)
            
            # Shutdown creation executor
            self.creation_executor.shutdown(wait=True)
            
            self.factory_state = "shutdown"
            self.logger.info("Staff Factory shutdown complete")
            
        except Exception as e:
            self.factory_state = "error"
            self.logger.error(f"Factory shutdown failed: {str(e)}")
            raise
    
    # Private helper methods
    def _initialize_agent_specifications(self):
        """Initialize all 25 agent specifications."""
        
        # Tier 1: Founder Authority
        self.agent_specifications["denauld_brown"] = AgentSpecification(
            agent_id="denauld_brown",
            agent_type=AgentType.FOUNDER_AUTHORITY,
            full_name="Denauld Brown",
            nickname="The Mastermind",
            position="Founder & CEO",
            department="Executive Leadership",
            tier_level=TierLevel.FOUNDER,
            emergency_priority=EmergencyPriority.FOUNDER_AUTHORITY,
            personality_type=PersonalityType.VISIONARY_LEADER,
            expertise_areas=[ExpertiseArea.STRATEGIC_VISION, ExpertiseArea.LEADERSHIP_EXCELLENCE, 
                           ExpertiseArea.TRIANGLE_DEFENSE_MASTERY],
            authority_domains=["Empire Strategy", "Triangle Defense Innovation", "Ultimate Authority"],
            effectiveness_rating=99.0,
            decision_speed="instantaneous",
            max_concurrent_tasks=20,
            triangle_defense_mastery=1.0,
            formation_specializations=["Strategic Innovation", "Empire Coordination"],
            nuclear_protocol_clearance=True,
            emergency_authority_level=1.0
        )
        
        # Tier 2: AI Core Command
        self.agent_specifications["mel"] = AgentSpecification(
            agent_id="mel",
            agent_type=AgentType.AI_CORE,
            implementation_class="MELAgent",
            full_name="M.E.L.",
            nickname="The AI Core",
            position="AI Core Command",
            department="AI Intelligence",
            tier_level=TierLevel.AI_CORE,
            emergency_priority=EmergencyPriority.AI_CORE_COMMAND,
            personality_type=PersonalityType.ANALYTICAL_MASTERMIND,
            expertise_areas=[ExpertiseArea.AI_DEVELOPMENT, ExpertiseArea.TRIANGLE_DEFENSE_MASTERY,
                           ExpertiseArea.STATISTICAL_INTELLIGENCE, ExpertiseArea.STRATEGIC_VISION],
            authority_domains=["AI Coordination", "Bot Ecosystem", "Triangle Defense AI"],
            effectiveness_rating=98.5,
            decision_speed="instantaneous",
            max_concurrent_tasks=50,
            triangle_defense_mastery=1.0,
            formation_specializations=["AI Optimization", "Predictive Analysis"],
            nuclear_protocol_clearance=True,
            emergency_authority_level=0.95
        )
        
        # Tier 3: Executive Command
        self.agent_specifications["courtney_sellars"] = AgentSpecification(
            agent_id="courtney_sellars",
            agent_type=AgentType.EXECUTIVE_LEADERSHIP,
            full_name="Courtney Sellars",
            nickname="The Shield",
            position="CEO & Chief Legal Officer",
            department="Executive Leadership",
            tier_level=TierLevel.EXECUTIVE,
            emergency_priority=EmergencyPriority.CEO_LEGAL_COMMAND,
            personality_type=PersonalityType.PROTECTIVE_GUARDIAN,
            expertise_areas=[ExpertiseArea.LEADERSHIP_EXCELLENCE, ExpertiseArea.OPERATIONS_EXCELLENCE],
            authority_domains=["Legal Authority", "Executive Command", "Cross-Company Leadership"],
            effectiveness_rating=97.0,
            max_concurrent_tasks=15,
            emergency_authority_level=0.9,
            succession_candidates=["denauld_brown"]
        )
        
        self.agent_specifications["alexandra_martinez"] = AgentSpecification(
            agent_id="alexandra_martinez", 
            agent_type=AgentType.EXECUTIVE_LEADERSHIP,
            full_name="Alexandra Martinez",
            nickname="The Coordinator",
            position="Chief Administrative Officer",
            department="Operations Command",
            tier_level=TierLevel.EXECUTIVE,
            emergency_priority=EmergencyPriority.COO_OPERATIONS,
            personality_type=PersonalityType.TACTICAL_COORDINATOR,
            expertise_areas=[ExpertiseArea.OPERATIONS_EXCELLENCE, ExpertiseArea.LEADERSHIP_EXCELLENCE],
            authority_domains=["Operations Excellence", "Administrative Command", "Cross-Company Coordination"],
            effectiveness_rating=96.5,
            max_concurrent_tasks=12,
            emergency_authority_level=0.85
        )
        
        # Tier 4: Strategic Leadership (partial list - adding key specialists)
        self.agent_specifications["marcus_sterling"] = AgentSpecification(
            agent_id="marcus_sterling",
            agent_type=AgentType.STRATEGIC_LEADERSHIP,
            full_name="Marcus Sterling",
            nickname="The Strategist",
            position="Chief Strategic Officer",
            department="Strategic Planning",
            tier_level=TierLevel.STRATEGIC,
            emergency_priority=EmergencyPriority.STRATEGIC_LEADERSHIP,
            personality_type=PersonalityType.ANALYTICAL_MASTERMIND,
            expertise_areas=[ExpertiseArea.STRATEGIC_VISION, ExpertiseArea.TRIANGLE_DEFENSE_MASTERY],
            authority_domains=["Strategic Planning", "Empire Strategy", "Triangle Defense Strategy"],
            effectiveness_rating=96.0,
            max_concurrent_tasks=10,
            triangle_defense_mastery=0.9
        )
        
        # Tier 6: Innovation & Technical Operations
        self.agent_specifications["professor_kim"] = AgentSpecification(
            agent_id="professor_kim",
            agent_type=AgentType.INNOVATION_TECHNICAL,
            full_name="Professor David Kim",
            nickname="The Architect",
            position="Chief Innovation Officer",
            department="Innovation Strategy",
            tier_level=TierLevel.INNOVATION,
            emergency_priority=EmergencyPriority.INNOVATION_TECHNICAL,
            personality_type=PersonalityType.INNOVATION_ARCHITECT,
            expertise_areas=[ExpertiseArea.STRATEGIC_VISION, ExpertiseArea.AI_DEVELOPMENT],
            authority_domains=["Innovation Strategy", "R&D Leadership", "Technology Architecture"],
            effectiveness_rating=96.8,
            max_concurrent_tasks=8,
            triangle_defense_mastery=0.8,
            formation_specializations=["Innovation Integration", "Technology Enhancement"]
        )
        
        self.agent_specifications["dr_foster"] = AgentSpecification(
            agent_id="dr_foster",
            agent_type=AgentType.INNOVATION_TECHNICAL,
            full_name="Dr. Rachel Foster",
            nickname="The Algorithm",
            position="Senior AI Research Scientist",
            department="AI Research",
            tier_level=TierLevel.INNOVATION,
            emergency_priority=EmergencyPriority.INNOVATION_TECHNICAL,
            personality_type=PersonalityType.TECHNICAL_SPECIALIST,
            expertise_areas=[ExpertiseArea.AI_DEVELOPMENT, ExpertiseArea.STATISTICAL_INTELLIGENCE],
            authority_domains=["AI Research", "Algorithm Development", "Neural Network Design"],
            effectiveness_rating=97.2,
            max_concurrent_tasks=6,
            triangle_defense_mastery=0.75,
            formation_specializations=["AI Analysis", "Predictive Modeling"]
        )
        
        self.agent_specifications["jake_morrison"] = AgentSpecification(
            agent_id="jake_morrison",
            agent_type=AgentType.INNOVATION_TECHNICAL,
            full_name="Jake Morrison",
            nickname="The Pipeline",
            position="Senior DevOps Engineer",
            department="Infrastructure Operations",
            tier_level=TierLevel.INNOVATION,
            emergency_priority=EmergencyPriority.INNOVATION_TECHNICAL,
            personality_type=PersonalityType.TECHNICAL_SPECIALIST,
            expertise_areas=[ExpertiseArea.OPERATIONS_EXCELLENCE],
            authority_domains=["Infrastructure Automation", "DevOps Excellence", "System Reliability"],
            effectiveness_rating=95.8,
            max_concurrent_tasks=7,
            triangle_defense_mastery=0.6,
            formation_specializations=["System Integration", "Performance Optimization"]
        )
        
        self.agent_specifications["maya_patel"] = AgentSpecification(
            agent_id="maya_patel",
            agent_type=AgentType.INNOVATION_TECHNICAL,
            full_name="Maya Patel",
            nickname="The Interface",
            position="Senior UX/UI Designer",
            department="Design Strategy",
            tier_level=TierLevel.INNOVATION,
            emergency_priority=EmergencyPriority.INNOVATION_TECHNICAL,
            personality_type=PersonalityType.INNOVATION_ARCHITECT,
            expertise_areas=[ExpertiseArea.STRATEGIC_VISION],
            authority_domains=["User Experience Design", "Interface Innovation", "Design Systems"],
            effectiveness_rating=96.2,
            max_concurrent_tasks=5,
            triangle_defense_mastery=0.65,
            formation_specializations=["Interface Visualization", "User Experience Optimization"]
        )
        
        # Tier 7: Football Operations (partial list)
        self.agent_specifications["tony_rivera"] = AgentSpecification(
            agent_id="tony_rivera",
            agent_type=AgentType.FOOTBALL_OPERATIONS,
            full_name="Tony Rivera",
            nickname="The Triangle Specialist",
            position="Director of Football Operations",
            department="Football Operations",
            tier_level=TierLevel.FOOTBALL,
            emergency_priority=EmergencyPriority.FOOTBALL_OPERATIONS,
            personality_type=PersonalityType.TACTICAL_COORDINATOR,
            expertise_areas=[ExpertiseArea.TRIANGLE_DEFENSE_MASTERY, ExpertiseArea.FOOTBALL_ANALYTICS],
            authority_domains=["Triangle Defense Operations", "Football Strategy", "Formation Analysis"],
            effectiveness_rating=95.5,
            max_concurrent_tasks=6,
            triangle_defense_mastery=0.95,
            formation_specializations=["Triangle Defense Mastery", "Formation Innovation", "Tactical Evolution"]
        )
        
        # Add placeholders for remaining agents to reach 25 total
        remaining_agent_ids = [
            "darius_washington", "dr_wright", "dr_chen", "captain_rodriguez",  # Strategic
            "bill_mckenzie", "patricia_williams", "elena_vasquez",  # Advisory
            "derek_thompson", "dr_johnson", "amanda_thompson", "roberto_gutierrez",  # Football Ops
            "sam_williams", "alex_chen", "marcus_lewis", "michael_rodriguez"  # Football Ops
        ]
        
        for i, agent_id in enumerate(remaining_agent_ids):
            # Determine tier based on position in list
            if i < 4:  # Strategic Leadership
                tier = TierLevel.STRATEGIC
                priority = EmergencyPriority.STRATEGIC_LEADERSHIP
                agent_type = AgentType.STRATEGIC_LEADERSHIP
                department = "Strategic Leadership"
            elif i < 7:  # Advisory Communications
                tier = TierLevel.ADVISORY
                priority = EmergencyPriority.ADVISORY_COMMUNICATIONS
                agent_type = AgentType.ADVISORY_COMMUNICATIONS
                department = "Advisory Communications"
            else:  # Football Operations
                tier = TierLevel.FOOTBALL
                priority = EmergencyPriority.FOOTBALL_OPERATIONS
                agent_type = AgentType.FOOTBALL_OPERATIONS
                department = "Football Operations"
            
            self.agent_specifications[agent_id] = AgentSpecification(
                agent_id=agent_id,
                agent_type=agent_type,
                full_name=agent_id.replace("_", " ").title(),
                nickname=f"Specialist_{i+1}",
                position=f"{department} Specialist",
                department=department,
                tier_level=tier,
                emergency_priority=priority,
                personality_type=PersonalityType.OPERATIONAL_EXCELLENCE,
                expertise_areas=[ExpertiseArea.FOOTBALL_ANALYTICS if "football" in department.lower() 
                               else ExpertiseArea.STRATEGIC_VISION],
                authority_domains=[f"{department} Excellence"],
                effectiveness_rating=94.0 + (i * 0.1),
                triangle_defense_mastery=0.7 + (i * 0.01)
            )
        
        self.logger.info(f"Initialized {len(self.agent_specifications)} agent specifications")
    
    def _create_agent_personality(self, spec: AgentSpecification, overrides: Dict[str, Any]) -> StaffPersonality:
        """Create agent personality from specification with overrides."""
        
        return StaffPersonality(
            full_name=overrides.get("full_name", spec.full_name),
            nickname=overrides.get("nickname", spec.nickname),
            position=overrides.get("position", spec.position),
            department=overrides.get("department", spec.department),
            tier_level=overrides.get("tier_level", spec.tier_level),
            emergency_priority=overrides.get("emergency_priority", spec.emergency_priority),
            personality_type=overrides.get("personality_type", spec.personality_type),
            expertise_areas=overrides.get("expertise_areas", spec.expertise_areas),
            authority_domains=overrides.get("authority_domains", spec.authority_domains),
            educational_background=overrides.get("educational_background", spec.educational_background),
            professional_experience=overrides.get("professional_experience", spec.professional_experience),
            effectiveness_rating=overrides.get("effectiveness_rating", spec.effectiveness_rating),
            decision_speed=overrides.get("decision_speed", spec.decision_speed),
            collaboration_style=overrides.get("collaboration_style", spec.collaboration_style),
            communication_style=overrides.get("communication_style", spec.communication_style),
            max_concurrent_tasks=overrides.get("max_concurrent_tasks", spec.max_concurrent_tasks),
            triangle_defense_mastery=overrides.get("triangle_defense_mastery", spec.triangle_defense_mastery),
            formation_specializations=overrides.get("formation_specializations", spec.formation_specializations),
            tactical_innovation_score=overrides.get("tactical_innovation_score", spec.tactical_innovation_score),
            succession_candidates=overrides.get("succession_candidates", spec.succession_candidates),
            emergency_authority_level=overrides.get("emergency_authority_level", spec.emergency_authority_level),
            nuclear_protocol_clearance=overrides.get("nuclear_protocol_clearance", spec.nuclear_protocol_clearance)
        )
    
    def _determine_agent_class(self, spec: AgentSpecification) -> Type[StaffAgentBase]:
        """Determine the appropriate agent class for the specification."""
        
        # Handle specific implementation classes
        if spec.implementation_class:
            if spec.implementation_class == "MELAgent":
                return MELAgent
            else:
                # Try to dynamically import custom implementation
                try:
                    module_path = f"griptape.amt.agents.{spec.implementation_class.lower()}"
                    module = importlib.import_module(module_path)
                    return getattr(module, spec.implementation_class)
                except (ImportError, AttributeError):
                    self.logger.warning(f"Custom implementation not found: {spec.implementation_class}, using base class")
        
        # Use base class for most agents
        return StaffAgentBase
    
    async def _instantiate_agent(self, agent_class: Type[StaffAgentBase], personality: StaffPersonality, overrides: Dict[str, Any]) -> StaffAgentBase:
        """Instantiate agent with proper initialization."""
        
        # Prepare agent initialization parameters
        init_params = {
            "personality": personality,
            "intelligence_coordinator": self.intelligence_coordinator,
            **overrides
        }
        
        # Filter parameters based on agent class constructor
        agent_sig = inspect.signature(agent_class.__init__)
        filtered_params = {k: v for k, v in init_params.items() if k in agent_sig.parameters}
        
        # Create agent instance
        agent = agent_class(**filtered_params)
        
        # Initialize if async initialization is available
        if hasattr(agent, 'initialize') and asyncio.iscoroutinefunction(agent.initialize):
            await agent.initialize()
        
        return agent
    
    # Creation strategy implementations
    async def _create_all_immediate(self) -> Dict[str, StaffAgentBase]:
        """Create all agents immediately in parallel."""
        
        creation_tasks = []
        for agent_id in self.agent_specifications.keys():
            creation_tasks.append(self.create_agent(agent_id))
        
        agents = await asyncio.gather(*creation_tasks, return_exceptions=True)
        
        # Build result dictionary
        result = {}
        for i, agent_id in enumerate(self.agent_specifications.keys()):
            if not isinstance(agents[i], Exception):
                result[agent_id] = agents[i]
            else:
                self.logger.error(f"Failed to create agent {agent_id}: {agents[i]}")
        
        return result
    
    async def _create_all_batch(self) -> Dict[str, StaffAgentBase]:
        """Create all agents in tier-based batches."""
        
        # Group agents by tier
        tier_groups = {}
        for agent_id, spec in self.agent_specifications.items():
            tier = spec.tier_level
            if tier not in tier_groups:
                tier_groups[tier] = []
            tier_groups[tier].append(agent_id)
        
        # Create agents tier by tier
        result = {}
        tier_order = [TierLevel.FOUNDER, TierLevel.AI_CORE, TierLevel.EXECUTIVE, 
                     TierLevel.STRATEGIC, TierLevel.ADVISORY, TierLevel.INNOVATION, TierLevel.FOOTBALL]
        
        for tier in tier_order:
            if tier in tier_groups:
                batch_tasks = []
                for agent_id in tier_groups[tier]:
                    batch_tasks.append(self.create_agent(agent_id))
                
                batch_agents = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for i, agent_id in enumerate(tier_groups[tier]):
                    if not isinstance(batch_agents[i], Exception):
                        result[agent_id] = batch_agents[i]
                    else:
                        self.logger.error(f"Failed to create agent {agent_id}: {batch_agents[i]}")
        
        return result
    
    async def _create_all_dependency_ordered(self) -> Dict[str, StaffAgentBase]:
        """Create all agents in dependency order."""
        
        # For now, use tier-based ordering as proxy for dependencies
        # This could be enhanced with actual dependency resolution
        return await self._create_all_batch()
    
    async def _resolve_agent_dependencies(self, agent_id: str):
        """Resolve agent dependencies before creation."""
        
        spec = self.agent_specifications[agent_id]
        instance = self.agent_instances[agent_id]
        
        # Resolve dependency agents
        for dep_agent_id in spec.dependencies:
            if dep_agent_id in self.agent_instances:
                instance.dependency_agents.add(dep_agent_id)
                self.agent_instances[dep_agent_id].dependent_agents.add(agent_id)
    
    async def _health_check_loop(self):
        """Continuous health monitoring loop."""
        
        while True:
            try:
                await asyncio.sleep(self.health_check_interval_seconds)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check loop error: {str(e)}")
    
    async def _perform_health_checks(self):
        """Perform health checks on all active agents."""
        
        for agent_id, instance in self.agent_instances.items():
            if instance.lifecycle_state == AgentLifecycleState.ACTIVE and instance.agent:
                try:
                    # Simple health check - verify agent is responsive
                    if hasattr(instance.agent, 'get_current_status'):
                        status = instance.agent.get_current_status()
                        instance.health_status = "healthy"
                    else:
                        instance.health_status = "unknown"
                    
                    instance.last_health_check = datetime.now()
                    
                except Exception as e:
                    instance.health_status = f"error: {str(e)}"
                    self.logger.warning(f"Health check failed for {agent_id}: {str(e)}")
        
        self.factory_metrics["health_checks_performed"] += 1
    
    def _update_creation_time_metric(self, creation_time_ms: float):
        """Update average creation time metric."""
        
        current_count = self.factory_metrics["agents_created"]
        current_avg = self.factory_metrics["average_creation_time_ms"]
        
        self.factory_metrics["average_creation_time_ms"] = (
            (current_avg * (current_count - 1) + creation_time_ms) / current_count
        )
    
    def _get_tier_distribution(self) -> Dict[str, int]:
        """Get distribution of agents by tier."""
        
        distribution = {}
        for spec in self.agent_specifications.values():
            tier = spec.tier_level.value
            distribution[tier] = distribution.get(tier, 0) + 1
        
        return distribution
    
    def _get_emergency_priority_distribution(self) -> Dict[str, int]:
        """Get distribution of agents by emergency priority."""
        
        distribution = {}
        for spec in self.agent_specifications.values():
            priority = spec.emergency_priority.value
            distribution[str(priority)] = distribution.get(str(priority), 0) + 1
        
        return distribution


# Convenience functions
async def create_staff_factory(intelligence_coordinator: Optional[IntelligenceCoordinator] = None,
                              auto_initialize: bool = True) -> StaffFactory:
    """Create and initialize a staff factory."""
    
    factory = StaffFactory(
        intelligence_coordinator=intelligence_coordinator,
        auto_initialize_agents=auto_initialize
    )
    
    await factory.initialize_factory()
    return factory


def get_agent_specification(agent_id: str) -> Optional[AgentSpecification]:
    """Get agent specification by ID without creating a factory."""
    
    # Create temporary factory to access specifications
    temp_factory = StaffFactory(auto_initialize_agents=False)
    return temp_factory.agent_specifications.get(agent_id)
