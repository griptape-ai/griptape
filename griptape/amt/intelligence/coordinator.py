"""
AMT Intelligence Coordinator - Core orchestration engine for the AnalyzeMyTeam ecosystem.
Coordinates all intelligence operations across 25 championship professionals and 12 companies.
Integrates with Airtable intelligence brain, GraphQL federation, and advanced analytics.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

from griptape.structures import Agent, Workflow, Pipeline
from griptape.tasks import PromptTask, TextSummaryTask
from griptape.memory import ConversationMemory
from griptape.artifacts import TextArtifact, ListArtifact, BaseArtifact
from griptape.utils import Chat

# AMT specific imports
from .staff_registry import StaffRegistry, StaffMember, TierLevel
from .tier_manager import TierManager, TaskComplexity, UrgencyLevel
from .airtable_bridge import AirtableBridge, StaffUpdate, TaskAssignment
from .graphql_client import GraphQLClient, QueryBuilder, DataSource


class IntelligenceMode(Enum):
    """Operating modes for the intelligence coordinator."""
    STANDARD = "standard"
    CRISIS = "crisis"
    STRATEGIC = "strategic"
    RESEARCH = "research"
    REAL_TIME = "real_time"


class RequestType(Enum):
    """Types of intelligence requests."""
    FORMATION_ANALYSIS = "formation_analysis"
    STAFF_COORDINATION = "staff_coordination"
    STRATEGIC_DECISION = "strategic_decision"
    CROSS_COMPANY = "cross_company"
    TRIANGLE_DEFENSE = "triangle_defense"
    PREDICTIVE_MODELING = "predictive_modeling"
    EMERGENCY_RESPONSE = "emergency_response"


@dataclass
class IntelligenceRequest:
    """Structured intelligence request with context and routing information."""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_type: RequestType = RequestType.FORMATION_ANALYSIS
    user_id: str = ""
    content: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    complexity: TaskComplexity = TaskComplexity.STANDARD
    required_data_sources: List[DataSource] = field(default_factory=list)
    target_tier: Optional[TierLevel] = None
    assigned_staff: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntelligenceResponse:
    """Comprehensive response from intelligence coordination."""
    request_id: str
    response_type: str
    primary_response: str
    supporting_analysis: Dict[str, Any] = field(default_factory=dict)
    data_synthesis: Dict[str, Any] = field(default_factory=dict)
    staff_contributions: List[Dict[str, Any]] = field(default_factory=list)
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    sources_consulted: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    follow_up_actions: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)


class IntelligenceCoordinator:
    """
    Master intelligence coordination engine for AnalyzeMyTeam ecosystem.
    
    Orchestrates all intelligence operations across:
    - 25 championship professionals in 7 tiers
    - Multi-source data federation (Hive, Supabase, Neo4j)
    - Cross-company coordination for 12 companies
    - Real-time Triangle Defense analysis
    - Advanced ML integration with Spark jobs
    """
    
    def __init__(self, 
                 airtable_config: Dict[str, str],
                 graphql_config: Dict[str, str],
                 mode: IntelligenceMode = IntelligenceMode.STANDARD):
        """
        Initialize the intelligence coordinator with full ecosystem integration.
        
        Args:
            airtable_config: Configuration for Airtable intelligence brain connection
            graphql_config: Configuration for GraphQL federation endpoints
            mode: Operating mode for intelligence coordination
        """
        self.mode = mode
        self.request_queue: List[IntelligenceRequest] = []
        self.active_requests: Dict[str, IntelligenceRequest] = {}
        self.completed_requests: Dict[str, IntelligenceResponse] = {}
        
        # Initialize core components
        self.staff_registry = StaffRegistry()
        self.tier_manager = TierManager()
        self.airtable_bridge = AirtableBridge(airtable_config)
        self.graphql_client = GraphQLClient(graphql_config)
        
        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix="AMT-Intel")
        
        # Intelligence metrics
        self.metrics = {
            "requests_processed": 0,
            "avg_response_time": 0.0,
            "staff_utilization": {},
            "data_source_usage": {},
            "success_rate": 0.0
        }
        
        # Configure logging
        self.logger = logging.getLogger(f"AMT.Intelligence.{mode.value}")
        self.logger.setLevel(logging.INFO)
        
        # Initialize intelligence workflows
        self._initialize_workflows()
        
        self.logger.info(f"Intelligence Coordinator initialized in {mode.value} mode")
    
    async def coordinate_intelligence(self, request: IntelligenceRequest) -> IntelligenceResponse:
        """
        Master coordination method for all intelligence requests.
        
        Args:
            request: Structured intelligence request
            
        Returns:
            Comprehensive intelligence response with multi-source synthesis
        """
        start_time = datetime.now()
        
        try:
            # Add to active requests
            self.active_requests[request.request_id] = request
            
            self.logger.info(f"Processing intelligence request {request.request_id}: {request.request_type.value}")
            
            # Phase 1: Intelligence Assessment
            assessment = await self._assess_request_complexity(request)
            
            # Phase 2: Resource Allocation
            allocation = await self._allocate_resources(request, assessment)
            
            # Phase 3: Data Source Coordination
            data_synthesis = await self._coordinate_data_sources(request, allocation)
            
            # Phase 4: Staff Coordination
            staff_coordination = await self._coordinate_staff_execution(request, allocation, data_synthesis)
            
            # Phase 5: Response Synthesis
            response = await self._synthesize_response(request, assessment, data_synthesis, staff_coordination)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            response.processing_time_ms = int(processing_time)
            
            # Update metrics
            self._update_metrics(request, response, processing_time)
            
            # Store completed request
            self.completed_requests[request.request_id] = response
            del self.active_requests[request.request_id]
            
            self.logger.info(f"Completed request {request.request_id} in {processing_time:.2f}ms")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing request {request.request_id}: {str(e)}")
            
            # Create error response
            error_response = IntelligenceResponse(
                request_id=request.request_id,
                response_type="error",
                primary_response=f"Intelligence coordination error: {str(e)}",
                processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                confidence_score=0.0
            )
            
            return error_response
    
    async def _assess_request_complexity(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """
        Assess request complexity and determine optimal processing strategy.
        
        Args:
            request: Intelligence request to assess
            
        Returns:
            Assessment results with processing recommendations
        """
        assessment = {
            "complexity_score": 0,
            "estimated_time_seconds": 0,
            "required_tier_level": TierLevel.FOOTBALL,
            "data_sources_needed": [],
            "processing_strategy": "standard",
            "staff_requirements": []
        }
        
        # Analyze request type complexity
        type_complexity = {
            RequestType.FORMATION_ANALYSIS: 3,
            RequestType.STAFF_COORDINATION: 2,
            RequestType.STRATEGIC_DECISION: 5,
            RequestType.CROSS_COMPANY: 6,
            RequestType.TRIANGLE_DEFENSE: 4,
            RequestType.PREDICTIVE_MODELING: 7,
            RequestType.EMERGENCY_RESPONSE: 8
        }
        
        base_complexity = type_complexity.get(request.request_type, 3)
        
        # Add context complexity
        context_factors = {
            "multi_company": 2,
            "real_time": 2,
            "historical_analysis": 1,
            "predictive": 3,
            "cross_functional": 2
        }
        
        context_complexity = sum(
            context_factors.get(key, 0) 
            for key in request.context.keys()
        )
        
        total_complexity = base_complexity + context_complexity
        assessment["complexity_score"] = total_complexity
        
        # Determine tier requirements
        if total_complexity >= 8:
            assessment["required_tier_level"] = TierLevel.FOUNDER
            assessment["estimated_time_seconds"] = 300
        elif total_complexity >= 6:
            assessment["required_tier_level"] = TierLevel.EXECUTIVE
            assessment["estimated_time_seconds"] = 180
        elif total_complexity >= 4:
            assessment["required_tier_level"] = TierLevel.STRATEGIC
            assessment["estimated_time_seconds"] = 120
        else:
            assessment["required_tier_level"] = TierLevel.FOOTBALL
            assessment["estimated_time_seconds"] = 60
        
        # Determine data sources needed
        if request.request_type in [RequestType.FORMATION_ANALYSIS, RequestType.TRIANGLE_DEFENSE]:
            assessment["data_sources_needed"] = [DataSource.HIVE, DataSource.NEO4J]
        elif request.request_type == RequestType.PREDICTIVE_MODELING:
            assessment["data_sources_needed"] = [DataSource.HIVE, DataSource.NEO4J, DataSource.SPARK]
        elif request.request_type in [RequestType.STRATEGIC_DECISION, RequestType.CROSS_COMPANY]:
            assessment["data_sources_needed"] = [DataSource.SUPABASE, DataSource.AIRTABLE]
        else:
            assessment["data_sources_needed"] = [DataSource.SUPABASE]
        
        return assessment
    
    async def _allocate_resources(self, 
                                request: IntelligenceRequest, 
                                assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allocate optimal staff and system resources for request processing.
        
        Args:
            request: Intelligence request
            assessment: Complexity assessment results
            
        Returns:
            Resource allocation plan
        """
        allocation = {
            "primary_staff": [],
            "supporting_staff": [],
            "data_sources": assessment["data_sources_needed"],
            "processing_mode": "standard",
            "priority_level": request.urgency.value
        }
        
        # Get available staff for required tier
        available_staff = await self.staff_registry.get_available_staff(
            tier_level=assessment["required_tier_level"],
            expertise_areas=self._extract_expertise_requirements(request)
        )
        
        # Select primary staff member
        if available_staff:
            primary_staff = self.tier_manager.select_optimal_staff(
                available_staff, request, assessment
            )
            allocation["primary_staff"] = [primary_staff.staff_id]
            
            # Mark staff as assigned
            await self.airtable_bridge.update_staff_status(
                primary_staff.staff_id, 
                "assigned",
                request.request_id
            )
        
        # Determine if supporting staff needed
        if assessment["complexity_score"] >= 6:
            supporting_staff = await self._get_supporting_staff(request, assessment, available_staff)
            allocation["supporting_staff"] = [s.staff_id for s in supporting_staff]
        
        # Set processing mode based on urgency
        if request.urgency == UrgencyLevel.CRITICAL:
            allocation["processing_mode"] = "priority"
        elif request.urgency == UrgencyLevel.HIGH:
            allocation["processing_mode"] = "expedited"
        
        return allocation
    
    async def _coordinate_data_sources(self, 
                                     request: IntelligenceRequest,
                                     allocation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate data retrieval and synthesis from multiple sources.
        
        Args:
            request: Intelligence request
            allocation: Resource allocation plan
            
        Returns:
            Synthesized data from all required sources
        """
        data_synthesis = {
            "sources_consulted": [],
            "data_quality_score": 0.0,
            "synthesis_confidence": 0.0,
            "real_time_data": {},
            "historical_data": {},
            "graph_analysis": {},
            "predictive_data": {}
        }
        
        # Coordinate concurrent data retrieval
        data_tasks = []
        
        for source in allocation["data_sources"]:
            if source == DataSource.SUPABASE:
                task = self._fetch_real_time_data(request)
                data_tasks.append(("supabase", task))
            elif source == DataSource.HIVE:
                task = self._fetch_historical_data(request)
                data_tasks.append(("hive", task))
            elif source == DataSource.NEO4J:
                task = self._fetch_graph_data(request)
                data_tasks.append(("neo4j", task))
            elif source == DataSource.SPARK:
                task = self._fetch_ml_predictions(request)
                data_tasks.append(("spark", task))
        
        # Execute data retrieval tasks concurrently
        futures = {
            self.executor.submit(asyncio.run, task): source_name 
            for source_name, task in data_tasks
        }
        
        for future in as_completed(futures):
            source_name = futures[future]
            try:
                result = future.result()
                data_synthesis[f"{source_name}_data"] = result
                data_synthesis["sources_consulted"].append(source_name)
            except Exception as e:
                self.logger.error(f"Error fetching data from {source_name}: {str(e)}")
        
        # Calculate data quality metrics
        data_synthesis["data_quality_score"] = self._calculate_data_quality(data_synthesis)
        data_synthesis["synthesis_confidence"] = self._calculate_synthesis_confidence(data_synthesis)
        
        return data_synthesis
    
    async def _coordinate_staff_execution(self,
                                        request: IntelligenceRequest,
                                        allocation: Dict[str, Any],
                                        data_synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate staff execution with synthesized data and context.
        
        Args:
            request: Intelligence request
            allocation: Resource allocation plan
            data_synthesis: Synthesized data from all sources
            
        Returns:
            Staff coordination results and contributions
        """
        coordination_results = {
            "primary_analysis": "",
            "supporting_analysis": [],
            "staff_confidence": 0.0,
            "execution_quality": 0.0,
            "collaboration_score": 0.0
        }
        
        # Execute primary staff analysis
        if allocation["primary_staff"]:
            primary_staff_id = allocation["primary_staff"][0]
            primary_staff = await self.staff_registry.get_staff_member(primary_staff_id)
            
            if primary_staff:
                primary_analysis = await self._execute_staff_analysis(
                    primary_staff, request, data_synthesis, is_primary=True
                )
                coordination_results["primary_analysis"] = primary_analysis
        
        # Execute supporting staff analysis if needed
        if allocation["supporting_staff"]:
            supporting_analyses = []
            
            for staff_id in allocation["supporting_staff"]:
                staff_member = await self.staff_registry.get_staff_member(staff_id)
                if staff_member:
                    analysis = await self._execute_staff_analysis(
                        staff_member, request, data_synthesis, is_primary=False
                    )
                    supporting_analyses.append({
                        "staff_id": staff_id,
                        "analysis": analysis,
                        "expertise": staff_member.expertise_areas
                    })
            
            coordination_results["supporting_analysis"] = supporting_analyses
        
        # Calculate coordination quality metrics
        coordination_results["staff_confidence"] = self._calculate_staff_confidence(coordination_results)
        coordination_results["execution_quality"] = self._calculate_execution_quality(coordination_results)
        coordination_results["collaboration_score"] = self._calculate_collaboration_score(coordination_results)
        
        return coordination_results
    
    async def _synthesize_response(self,
                                 request: IntelligenceRequest,
                                 assessment: Dict[str, Any],
                                 data_synthesis: Dict[str, Any],
                                 staff_coordination: Dict[str, Any]) -> IntelligenceResponse:
        """
        Synthesize final comprehensive response from all coordination results.
        
        Args:
            request: Original intelligence request
            assessment: Complexity assessment
            data_synthesis: Multi-source data synthesis
            staff_coordination: Staff execution results
            
        Returns:
            Comprehensive intelligence response
        """
        # Create the primary response synthesis
        primary_response = self._create_primary_response(
            request, staff_coordination["primary_analysis"], data_synthesis
        )
        
        # Generate supporting analysis
        supporting_analysis = {
            "complexity_assessment": assessment,
            "data_quality": data_synthesis.get("data_quality_score", 0.0),
            "staff_expertise_applied": self._extract_expertise_applied(staff_coordination),
            "confidence_factors": self._analyze_confidence_factors(data_synthesis, staff_coordination)
        }
        
        # Calculate overall confidence score
        confidence_score = self._calculate_overall_confidence(data_synthesis, staff_coordination)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(request, data_synthesis, staff_coordination)
        
        # Generate follow-up actions
        follow_up_actions = self._generate_follow_up_actions(request, assessment, staff_coordination)
        
        response = IntelligenceResponse(
            request_id=request.request_id,
            response_type=request.request_type.value,
            primary_response=primary_response,
            supporting_analysis=supporting_analysis,
            data_synthesis=data_synthesis,
            staff_contributions=self._format_staff_contributions(staff_coordination),
            confidence_score=confidence_score,
            sources_consulted=data_synthesis.get("sources_consulted", []),
            recommendations=recommendations,
            follow_up_actions=follow_up_actions
        )
        
        return response
    
    # Helper methods for workflow initialization and data operations
    def _initialize_workflows(self):
        """Initialize Griptape workflows for different intelligence operations."""
        # Standard Analysis Workflow
        self.standard_workflow = Workflow(
            tasks=[
                PromptTask(
                    id="context_analysis",
                    input="{{ request_context }}",
                    rules=["Analyze request context and determine optimal approach"]
                ),
                PromptTask(
                    id="data_interpretation",
                    input="{{ data_synthesis }}",
                    rules=["Interpret synthesized data with Triangle Defense methodology"]
                ),
                TextSummaryTask(
                    id="response_synthesis",
                    input="{{ analysis_results }}",
                    rules=["Synthesize comprehensive response with actionable insights"]
                )
            ]
        )
        
        # Strategic Decision Workflow
        self.strategic_workflow = Workflow(
            tasks=[
                PromptTask(
                    id="strategic_assessment",
                    input="{{ strategic_context }}",
                    rules=["Assess strategic implications across all 12 companies"]
                ),
                PromptTask(
                    id="cross_company_impact",
                    input="{{ company_data }}",
                    rules=["Analyze cross-company impacts and coordination requirements"]
                ),
                PromptTask(
                    id="decision_framework",
                    input="{{ impact_analysis }}",
                    rules=["Apply AMT decision framework with championship standards"]
                )
            ]
        )
    
    def _extract_expertise_requirements(self, request: IntelligenceRequest) -> List[str]:
        """Extract required expertise areas from request content and type."""
        expertise_map = {
            RequestType.FORMATION_ANALYSIS: ["Triangle Defense", "Football Analytics"],
            RequestType.TRIANGLE_DEFENSE: ["Triangle Defense Mastery", "Defensive Analysis"],
            RequestType.PREDICTIVE_MODELING: ["AI Development", "Statistical Intelligence"],
            RequestType.STRATEGIC_DECISION: ["Strategic Planning", "Leadership Excellence"],
            RequestType.CROSS_COMPANY: ["Project Management", "Operations Excellence"]
        }
        
        return expertise_map.get(request.request_type, ["General Excellence"])
    
    async def _fetch_real_time_data(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Fetch real-time data from Supabase."""
        # Implementation would connect to Supabase for live data
        return {"status": "placeholder", "source": "supabase"}
    
    async def _fetch_historical_data(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Fetch historical analytics from Hive."""
        # Implementation would connect to Hive for historical data
        return {"status": "placeholder", "source": "hive"}
    
    async def _fetch_graph_data(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Fetch graph analysis from Neo4j."""
        # Implementation would connect to Neo4j for relationship data
        return {"status": "placeholder", "source": "neo4j"}
    
    async def _fetch_ml_predictions(self, request: IntelligenceRequest) -> Dict[str, Any]:
        """Fetch ML predictions from Spark jobs."""
        # Implementation would connect to Spark for A* algorithm results
        return {"status": "placeholder", "source": "spark"}
    
    def _calculate_data_quality(self, data_synthesis: Dict[str, Any]) -> float:
        """Calculate overall data quality score."""
        return min(1.0, len(data_synthesis["sources_consulted"]) / 3.0)
    
    def _calculate_synthesis_confidence(self, data_synthesis: Dict[str, Any]) -> float:
        """Calculate confidence in data synthesis."""
        return 0.85  # Placeholder implementation
    
    async def _execute_staff_analysis(self, 
                                    staff: StaffMember, 
                                    request: IntelligenceRequest,
                                    data_synthesis: Dict[str, Any],
                                    is_primary: bool) -> str:
        """Execute analysis using staff member's specific agent."""
        # This would instantiate the specific staff agent and execute analysis
        return f"Analysis from {staff.full_name} ({staff.nickname}): Placeholder analysis"
    
    def _calculate_staff_confidence(self, coordination_results: Dict[str, Any]) -> float:
        """Calculate confidence in staff coordination."""
        return 0.88  # Placeholder implementation
    
    def _calculate_execution_quality(self, coordination_results: Dict[str, Any]) -> float:
        """Calculate quality of execution."""
        return 0.91  # Placeholder implementation
    
    def _calculate_collaboration_score(self, coordination_results: Dict[str, Any]) -> float:
        """Calculate collaboration effectiveness score."""
        return 0.86  # Placeholder implementation
    
    def _create_primary_response(self, 
                               request: IntelligenceRequest,
                               primary_analysis: str,
                               data_synthesis: Dict[str, Any]) -> str:
        """Create the primary response synthesis."""
        return f"Intelligence Response for {request.request_type.value}: {primary_analysis}"
    
    def _extract_expertise_applied(self, staff_coordination: Dict[str, Any]) -> List[str]:
        """Extract expertise areas that were applied."""
        return ["Triangle Defense", "Strategic Analysis"]  # Placeholder
    
    def _analyze_confidence_factors(self, 
                                  data_synthesis: Dict[str, Any],
                                  staff_coordination: Dict[str, Any]) -> Dict[str, float]:
        """Analyze factors contributing to overall confidence."""
        return {
            "data_quality": data_synthesis.get("data_quality_score", 0.0),
            "staff_expertise": staff_coordination.get("staff_confidence", 0.0),
            "source_reliability": 0.85
        }
    
    def _calculate_overall_confidence(self,
                                    data_synthesis: Dict[str, Any],
                                    staff_coordination: Dict[str, Any]) -> float:
        """Calculate overall confidence in the response."""
        data_confidence = data_synthesis.get("synthesis_confidence", 0.0)
        staff_confidence = staff_coordination.get("staff_confidence", 0.0)
        return (data_confidence + staff_confidence) / 2.0
    
    def _generate_recommendations(self,
                                request: IntelligenceRequest,
                                data_synthesis: Dict[str, Any],
                                staff_coordination: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        return [
            "Implement Triangle Defense optimization",
            "Coordinate cross-functional team alignment",
            "Monitor real-time performance metrics"
        ]
    
    def _generate_follow_up_actions(self,
                                  request: IntelligenceRequest,
                                  assessment: Dict[str, Any],
                                  staff_coordination: Dict[str, Any]) -> List[str]:
        """Generate follow-up actions."""
        return [
            "Schedule tactical review session",
            "Update staff performance metrics",
            "Coordinate with supporting departments"
        ]
    
    def _format_staff_contributions(self, staff_coordination: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format staff contributions for response."""
        contributions = []
        
        if staff_coordination["primary_analysis"]:
            contributions.append({
                "type": "primary",
                "analysis": staff_coordination["primary_analysis"],
                "confidence": staff_coordination.get("staff_confidence", 0.0)
            })
        
        for supporting in staff_coordination.get("supporting_analysis", []):
            contributions.append({
                "type": "supporting",
                "staff_id": supporting["staff_id"],
                "analysis": supporting["analysis"],
                "expertise": supporting["expertise"]
            })
        
        return contributions
    
    def _update_metrics(self, 
                       request: IntelligenceRequest,
                       response: IntelligenceResponse,
                       processing_time: float):
        """Update intelligence coordination metrics."""
        self.metrics["requests_processed"] += 1
        
        # Update average response time
        total_requests = self.metrics["requests_processed"]
        current_avg = self.metrics["avg_response_time"]
        self.metrics["avg_response_time"] = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        
        # Update success rate based on confidence score
        if response.confidence_score >= 0.8:
            self.metrics["success_rate"] = (self.metrics["success_rate"] * 0.9) + (1.0 * 0.1)
        else:
            self.metrics["success_rate"] = (self.metrics["success_rate"] * 0.9) + (0.0 * 0.1)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and metrics."""
        return {
            "mode": self.mode.value,
            "active_requests": len(self.active_requests),
            "queue_length": len(self.request_queue),
            "metrics": self.metrics,
            "staff_status": await self.staff_registry.get_staff_status_summary(),
            "system_health": "operational"
        }
    
    async def shutdown(self):
        """Gracefully shutdown the intelligence coordinator."""
        self.logger.info("Shutting down Intelligence Coordinator...")
        
        # Complete active requests
        if self.active_requests:
            self.logger.info(f"Waiting for {len(self.active_requests)} active requests to complete...")
            # Implementation would wait for active requests
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        self.logger.info("Intelligence Coordinator shutdown complete")


# Factory function for easy instantiation
def create_intelligence_coordinator(airtable_config: Dict[str, str],
                                  graphql_config: Dict[str, str],
                                  mode: IntelligenceMode = IntelligenceMode.STANDARD) -> IntelligenceCoordinator:
    """
    Factory function to create and configure an Intelligence Coordinator.
    
    Args:
        airtable_config: Airtable connection configuration
        graphql_config: GraphQL federation configuration
        mode: Operating mode for the coordinator
        
    Returns:
        Configured IntelligenceCoordinator instance
    """
    return IntelligenceCoordinator(airtable_config, graphql_config, mode)
