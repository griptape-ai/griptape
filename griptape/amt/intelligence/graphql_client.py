"""
AMT GraphQL Federation Client - Advanced data orchestration across Hive, Supabase, and Neo4j.
Handles Triangle Defense queries, formation analysis, and real-time intelligence synthesis.
Integrates with existing GraphQL federation gateway and supports complex tactical analytics.
"""

import logging
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import httpx
import websockets
from pathlib import Path
from collections import defaultdict, deque
import hashlib


class DataSource(Enum):
    """Data source types for federation queries."""
    HIVE = "hive"                    # Historical analytics
    SUPABASE = "supabase"           # Real-time operations  
    NEO4J = "neo4j"                 # Graph relationships
    FEDERATION = "federation"        # Multi-source queries


class QueryComplexity(Enum):
    """Query complexity levels for optimization."""
    SIMPLE = "simple"               # Single table/node queries
    MODERATE = "moderate"           # Multi-table joins
    COMPLEX = "complex"             # Cross-source federation
    ADVANCED = "advanced"           # Graph algorithms + ML
    STRATEGIC = "strategic"         # Full ecosystem analysis


class SubscriptionType(Enum):
    """Real-time subscription types."""
    FORMATION_UPDATES = "formation_updates"
    GAME_STATE_CHANGES = "game_state_changes"
    TACTICAL_INSIGHTS = "tactical_insights"
    STAFF_COORDINATION = "staff_coordination"
    EMERGENCY_ALERTS = "emergency_alerts"


@dataclass
class QueryMetrics:
    """Performance metrics for GraphQL queries."""
    query_id: str
    data_sources: List[DataSource]
    complexity: QueryComplexity
    execution_time_ms: float
    cache_hit: bool
    result_size_bytes: int
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FormationQueryResult:
    """Results from Triangle Defense formation queries."""
    formations: List[Dict[str, Any]]
    similarity_graph: Optional[Dict[str, Any]] = None
    tactical_insights: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Optional[QueryMetrics] = None
    cache_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TriangleDefenseContext:
    """Context for Triangle Defense specific queries."""
    formation_type: Optional[str] = None
    hash_position: Optional[str] = None
    field_zone: Optional[str] = None
    game_situation: Optional[str] = None
    opponent_tendencies: List[str] = field(default_factory=list)
    historical_success_threshold: float = 0.75
    include_similarity_analysis: bool = True
    include_tactical_evolution: bool = False
    max_results: int = 100


class GraphQLFederationClient:
    """
    Advanced GraphQL federation client for AMT intelligence coordination.
    
    Orchestrates complex queries across Hive (historical), Supabase (real-time), 
    and Neo4j (graph) data sources with intelligent caching, performance optimization,
    and Triangle Defense specific analytics.
    """
    
    def __init__(self, 
                 federation_endpoint: str = "http://localhost:4000/graphql",
                 websocket_endpoint: str = "ws://localhost:4000/subscriptions",
                 auth_token: Optional[str] = None,
                 cache_ttl_seconds: int = 300,
                 max_concurrent_queries: int = 10):
        """
        Initialize GraphQL federation client with performance optimization.
        
        Args:
            federation_endpoint: GraphQL federation gateway URL
            websocket_endpoint: WebSocket endpoint for subscriptions
            auth_token: Authentication token for secure queries
            cache_ttl_seconds: Cache time-to-live for query results
            max_concurrent_queries: Maximum concurrent query limit
        """
        
        self.federation_endpoint = federation_endpoint
        self.websocket_endpoint = websocket_endpoint
        self.auth_token = auth_token
        self.cache_ttl_seconds = cache_ttl_seconds
        self.max_concurrent_queries = max_concurrent_queries
        
        # Performance optimization components
        self.query_cache: Dict[str, Tuple[Any, datetime]] = {}
        self.performance_metrics: List[QueryMetrics] = []
        self.active_queries: Set[str] = set()
        self.query_semaphore = asyncio.Semaphore(max_concurrent_queries)
        
        # Connection management
        self.http_client: Optional[httpx.AsyncClient] = None
        self.websocket_connection: Optional[websockets.WebSocketServerProtocol] = None
        self.subscription_handlers: Dict[SubscriptionType, callable] = {}
        
        # Triangle Defense query templates
        self.triangle_defense_queries = self._initialize_triangle_defense_queries()
        
        # Logger
        self.logger = logging.getLogger("AMT.GraphQLClient")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info(f"GraphQL Federation Client initialized - Endpoint: {federation_endpoint}")
    
    async def initialize(self):
        """Initialize HTTP client and establish connections."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        self.http_client = httpx.AsyncClient(
            headers=headers,
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10)
        )
        
        self.logger.info("GraphQL client initialized with HTTP connection pool")
    
    async def close(self):
        """Clean up connections and resources."""
        if self.http_client:
            await self.http_client.aclose()
        
        if self.websocket_connection:
            await self.websocket_connection.close()
        
        self.logger.info("GraphQL client connections closed")
    
    async def execute_query(self,
                           query: str,
                           variables: Optional[Dict[str, Any]] = None,
                           data_sources: Optional[List[DataSource]] = None,
                           complexity: QueryComplexity = QueryComplexity.MODERATE,
                           use_cache: bool = True,
                           timeout_seconds: float = 30.0) -> Dict[str, Any]:
        """
        Execute GraphQL query with intelligent caching and performance tracking.
        
        Args:
            query: GraphQL query string
            variables: Query variables
            data_sources: Target data sources for optimization
            complexity: Query complexity level
            use_cache: Whether to use cached results
            timeout_seconds: Query timeout
            
        Returns:
            Query results with metadata
        """
        variables = variables or {}
        data_sources = data_sources or [DataSource.FEDERATION]
        
        # Generate cache key
        cache_key = self._generate_cache_key(query, variables)
        
        # Check cache if enabled
        if use_cache and cache_key in self.query_cache:
            cached_result, cached_time = self.query_cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl_seconds):
                self.logger.debug(f"Cache hit for query: {cache_key[:16]}...")
                return {
                    "data": cached_result,
                    "cache_hit": True,
                    "cached_at": cached_time
                }
        
        # Execute query with concurrency control
        async with self.query_semaphore:
            start_time = time.time()
            query_id = f"query_{int(start_time * 1000)}"
            self.active_queries.add(query_id)
            
            try:
                # Prepare request payload
                payload = {
                    "query": query,
                    "variables": variables,
                    "operationName": self._extract_operation_name(query)
                }
                
                # Add source routing hints for federation
                if len(data_sources) == 1 and data_sources[0] != DataSource.FEDERATION:
                    payload["extensions"] = {
                        "source_hint": data_sources[0].value,
                        "complexity": complexity.value
                    }
                
                # Execute HTTP request
                if not self.http_client:
                    await self.initialize()
                
                response = await self.http_client.post(
                    self.federation_endpoint,
                    json=payload,
                    timeout=timeout_seconds
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Calculate metrics
                execution_time = (time.time() - start_time) * 1000
                result_size = len(json.dumps(result).encode('utf-8'))
                
                # Store performance metrics
                metrics = QueryMetrics(
                    query_id=query_id,
                    data_sources=data_sources,
                    complexity=complexity,
                    execution_time_ms=execution_time,
                    cache_hit=False,
                    result_size_bytes=result_size,
                    error_count=1 if "errors" in result else 0
                )
                self.performance_metrics.append(metrics)
                
                # Cache successful results
                if use_cache and "errors" not in result:
                    self.query_cache[cache_key] = (result["data"], datetime.now())
                
                # Add metadata to result
                result["execution_metadata"] = {
                    "query_id": query_id,
                    "execution_time_ms": execution_time,
                    "data_sources": [ds.value for ds in data_sources],
                    "cache_hit": False,
                    "complexity": complexity.value
                }
                
                self.logger.debug(f"Query executed: {query_id} ({execution_time:.2f}ms)")
                return result
                
            except Exception as e:
                self.logger.error(f"Query execution failed: {query_id} - {str(e)}")
                raise
            finally:
                self.active_queries.discard(query_id)
    
    async def query_triangle_defense_formations(self,
                                              context: TriangleDefenseContext) -> FormationQueryResult:
        """
        Execute specialized Triangle Defense formation analysis queries.
        
        Args:
            context: Triangle Defense query context and parameters
            
        Returns:
            Comprehensive formation analysis results
        """
        
        # Build dynamic query based on context
        query_parts = []
        variables = {}
        
        # Base formation query
        base_query = """
        query TriangleDefenseAnalysis($filters: FormationFilters!, $limit: Int!) {
            formations(filter: $filters, limit: $limit) {
                id
                gameId
                timestamp
                formationType
                hashPosition
                fieldZone
                playerPositions {
                    playerId
                    position {
                        x
                        y
                        z
                    }
                    role
                }
                triangularRelationships {
                    vertex1
                    vertex2  
                    vertex3
                    relationshipType
                    strength
                }
                # Real-time data from Supabase
                isLive
                currentDown
                yardsToGo
                gameState
                
                # Historical data from Hive
                historicalSuccessRate
                seasonTrends {
                    season
                    usage
                    effectiveness
                }
                
                # Graph analysis from Neo4j
                ...on TriangleDefenseFormation {
                    formationImportance: importance_score
                    centralityMeasures {
                        betweenness
                        closeness
                        eigenvector
                        pagerank
                    }
                }
            }
        }
        """
        
        # Build filter variables
        filters = {}
        if context.formation_type:
            filters["formationType"] = context.formation_type
        if context.hash_position:
            filters["hashPosition"] = context.hash_position
        if context.field_zone:
            filters["fieldZone"] = context.field_zone
        if context.game_situation:
            filters["gameSituation"] = context.game_situation
        
        variables = {
            "filters": filters,
            "limit": context.max_results
        }
        
        # Add similarity analysis if requested
        if context.include_similarity_analysis:
            similarity_query = """
            formationSimilarity(sourceFormationId: $sourceFormationId, threshold: $threshold) {
                targetFormation {
                    id
                    formationType
                    similarity_score
                }
                relationshipAnalysis {
                    structural_similarity
                    tactical_similarity
                    performance_correlation
                }
            }
            """
            variables["threshold"] = context.historical_success_threshold
        
        # Add tactical evolution if requested
        if context.include_tactical_evolution:
            evolution_query = """
            tacticalEvolution(formationId: $formationId) {
                evolutionPath {
                    step
                    formation {
                        id
                        formationType
                        adaptation_reason
                    }
                    confidence_score
                }
                clusterAnalysis {
                    cluster_id
                    formations_in_cluster
                    cluster_characteristics
                }
            }
            """
        
        # Execute the comprehensive query
        try:
            result = await self.execute_query(
                query=base_query,
                variables=variables,
                data_sources=[DataSource.FEDERATION],
                complexity=QueryComplexity.COMPLEX if context.include_similarity_analysis else QueryComplexity.MODERATE
            )
            
            formations = result.get("data", {}).get("formations", [])
            
            # Extract similarity graph if included
            similarity_graph = None
            if context.include_similarity_analysis and formations:
                similarity_graph = await self._build_similarity_graph(formations, context)
            
            # Generate tactical insights
            tactical_insights = await self._generate_tactical_insights(formations, context)
            
            return FormationQueryResult(
                formations=formations,
                similarity_graph=similarity_graph,
                tactical_insights=tactical_insights,
                performance_metrics=result.get("execution_metadata"),
                cache_metadata={"cache_hit": result.get("cache_hit", False)}
            )
            
        except Exception as e:
            self.logger.error(f"Triangle Defense query failed: {str(e)}")
            raise
    
    async def query_real_time_intelligence(self,
                                         staff_coordination: bool = True,
                                         game_state: bool = True,
                                         formation_tracking: bool = True) -> Dict[str, Any]:
        """
        Query real-time intelligence data for immediate decision making.
        
        Args:
            staff_coordination: Include staff coordination data
            game_state: Include live game state
            formation_tracking: Include formation tracking
            
        Returns:
            Real-time intelligence summary
        """
        
        query_fragments = []
        
        if staff_coordination:
            query_fragments.append("""
            staffCoordination {
                activeAssignments {
                    staffId
                    taskId
                    priority
                    estimatedCompletion
                    status
                }
                emergencyAlerts {
                    alertId
                    severity
                    message
                    triggeredAt
                }
                workloadDistribution {
                    tierId
                    currentUtilization
                    availableCapacity
                }
            }
            """)
        
        if game_state:
            query_fragments.append("""
            liveGameState {
                activeGames {
                    gameId
                    quarter
                    timeRemaining
                    possession {
                        team
                        down
                        yardsToGo
                        fieldPosition
                    }
                    currentFormation {
                        offensive
                        defensive  
                        confidence
                    }
                }
            }
            """)
        
        if formation_tracking:
            query_fragments.append("""
            realtimeFormations {
                liveFormations {
                    formationId
                    timestamp
                    formationType
                    playerPositions {
                        playerId
                        realTimePosition {
                            x
                            y
                            velocity
                        }
                    }
                    triangleMetrics {
                        stability_score
                        coverage_effectiveness
                        pressure_generation
                    }
                }
            }
            """)
        
        full_query = f"""
        query RealTimeIntelligence {{
            {chr(10).join(query_fragments)}
        }}
        """
        
        result = await self.execute_query(
            query=full_query,
            data_sources=[DataSource.SUPABASE],
            complexity=QueryComplexity.MODERATE,
            use_cache=False  # Real-time data shouldn't be cached
        )
        
        return result.get("data", {})
    
    async def query_historical_patterns(self,
                                       timeframe_days: int = 30,
                                       pattern_types: List[str] = None,
                                       success_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Query historical pattern analysis from Hive data warehouse.
        
        Args:
            timeframe_days: Analysis timeframe in days
            pattern_types: Specific pattern types to analyze
            success_threshold: Minimum success rate threshold
            
        Returns:
            Historical pattern analysis results
        """
        
        pattern_types = pattern_types or ["formation_success", "tactical_evolution", "opponent_adaptation"]
        
        query = """
        query HistoricalPatterns($timeframe: Int!, $patterns: [String!]!, $threshold: Float!) {
            historicalAnalysis(timeframeDays: $timeframe) {
                formationTrends(patterns: $patterns, successThreshold: $threshold) {
                    pattern_type
                    trend_data {
                        period
                        formations {
                            formation_type
                            usage_frequency
                            success_rate
                            adaptation_indicators
                        }
                    }
                    predictive_insights {
                        trend_direction
                        confidence_score
                        recommended_adjustments
                    }
                }
                
                tacticalEvolution {
                    evolution_sequences {
                        sequence_id
                        formation_progression
                        trigger_events
                        effectiveness_metrics
                    }
                    meta_patterns {
                        pattern_category
                        frequency
                        success_correlation
                    }
                }
                
                opponentAnalysis {
                    adaptation_patterns {
                        opponent_id
                        counter_formations
                        effectiveness_timeline
                        response_time_metrics
                    }
                }
            }
        }
        """
        
        variables = {
            "timeframe": timeframe_days,
            "patterns": pattern_types,
            "threshold": success_threshold
        }
        
        result = await self.execute_query(
            query=query,
            variables=variables,
            data_sources=[DataSource.HIVE],
            complexity=QueryComplexity.COMPLEX
        )
        
        return result.get("data", {}).get("historicalAnalysis", {})
    
    async def execute_graph_analysis(self,
                                   analysis_type: str,
                                   formation_ids: List[str] = None,
                                   centrality_measures: List[str] = None) -> Dict[str, Any]:
        """
        Execute advanced graph analysis using Neo4j algorithms.
        
        Args:
            analysis_type: Type of graph analysis (similarity, centrality, community, etc.)
            formation_ids: Specific formation IDs to analyze
            centrality_measures: Centrality measures to calculate
            
        Returns:
            Graph analysis results
        """
        
        centrality_measures = centrality_measures or ["betweenness", "closeness", "pagerank"]
        
        # Dynamic query construction based on analysis type
        if analysis_type == "formation_similarity":
            query = """
            query FormationSimilarityAnalysis($formationIds: [ID!], $measures: [String!]!) {
                graphAnalysis {
                    formationSimilarityNetwork(formationIds: $formationIds) {
                        nodes {
                            id
                            formationType
                            properties {
                                importance_score
                                cluster_id
                            }
                        }
                        edges {
                            source
                            target
                            similarity_score
                            relationship_type
                        }
                        networkMetrics {
                            density
                            modularity
                            average_clustering
                        }
                    }
                    
                    centralityAnalysis(measures: $measures) {
                        formation_importance_ranking {
                            formation_id
                            centrality_scores {
                                measure
                                score
                                ranking
                            }
                        }
                    }
                }
            }
            """
        
        elif analysis_type == "tactical_pathfinding":
            query = """
            query TacticalPathfinding($formationIds: [ID!]!) {
                graphAnalysis {
                    tacticalEvolutionPaths(sourceFormations: $formationIds) {
                        optimal_paths {
                            path_id
                            formation_sequence
                            transition_costs
                            total_effectiveness
                        }
                        alternative_routes {
                            route_id
                            formation_sequence  
                            risk_assessment
                            adaptation_flexibility
                        }
                    }
                }
            }
            """
        
        elif analysis_type == "community_detection":
            query = """
            query CommunityDetection {
                graphAnalysis {
                    formationCommunities {
                        communities {
                            community_id
                            formations
                            shared_characteristics
                            tactical_theme
                        }
                        community_relationships {
                            source_community
                            target_community
                            interaction_strength
                            tactical_compatibility
                        }
                    }
                }
            }
            """
        
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
        
        variables = {
            "formationIds": formation_ids or [],
            "measures": centrality_measures
        }
        
        result = await self.execute_query(
            query=query,
            variables=variables,
            data_sources=[DataSource.NEO4J],
            complexity=QueryComplexity.ADVANCED
        )
        
        return result.get("data", {}).get("graphAnalysis", {})
    
    async def subscribe_to_updates(self,
                                  subscription_type: SubscriptionType,
                                  handler: callable,
                                  filter_params: Dict[str, Any] = None) -> str:
        """
        Subscribe to real-time updates via WebSocket.
        
        Args:
            subscription_type: Type of subscription
            handler: Callback function for updates
            filter_params: Optional filtering parameters
            
        Returns:
            Subscription ID
        """
        
        if not self.websocket_connection:
            await self._establish_websocket_connection()
        
        subscription_id = f"{subscription_type.value}_{int(time.time() * 1000)}"
        self.subscription_handlers[subscription_type] = handler
        
        # Build subscription query based on type
        subscription_query = self._build_subscription_query(subscription_type, filter_params)
        
        # Send subscription request
        subscription_request = {
            "id": subscription_id,
            "type": "start",
            "payload": {
                "query": subscription_query,
                "variables": filter_params or {}
            }
        }
        
        await self.websocket_connection.send(json.dumps(subscription_request))
        
        self.logger.info(f"Subscription established: {subscription_id}")
        return subscription_id
    
    async def unsubscribe(self, subscription_id: str):
        """Unsubscribe from real-time updates."""
        if self.websocket_connection:
            unsubscribe_request = {
                "id": subscription_id,
                "type": "stop"
            }
            await self.websocket_connection.send(json.dumps(unsubscribe_request))
            
        self.logger.info(f"Unsubscribed: {subscription_id}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        if not self.performance_metrics:
            return {"message": "No queries executed yet"}
        
        recent_metrics = [m for m in self.performance_metrics if 
                         datetime.now() - m.timestamp < timedelta(hours=1)]
        
        avg_execution_time = sum(m.execution_time_ms for m in recent_metrics) / len(recent_metrics)
        cache_hit_rate = sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)
        
        return {
            "total_queries": len(self.performance_metrics),
            "recent_queries_1h": len(recent_metrics),
            "average_execution_time_ms": avg_execution_time,
            "cache_hit_rate": cache_hit_rate,
            "active_queries": len(self.active_queries),
            "data_source_distribution": self._analyze_data_source_usage(),
            "complexity_distribution": self._analyze_complexity_distribution(),
            "cache_size": len(self.query_cache)
        }
    
    def clear_cache(self, selective: bool = False, older_than_minutes: int = 60):
        """Clear query cache with optional selective clearing."""
        if selective:
            cutoff_time = datetime.now() - timedelta(minutes=older_than_minutes)
            keys_to_remove = [
                key for key, (_, cached_time) in self.query_cache.items()
                if cached_time < cutoff_time
            ]
            for key in keys_to_remove:
                del self.query_cache[key]
            self.logger.info(f"Cleared {len(keys_to_remove)} cached queries older than {older_than_minutes} minutes")
        else:
            self.query_cache.clear()
            self.logger.info("Cleared all cached queries")
    
    # Private helper methods
    def _generate_cache_key(self, query: str, variables: Dict[str, Any]) -> str:
        """Generate cache key for query + variables combination."""
        query_normalized = " ".join(query.split())  # Normalize whitespace
        variables_json = json.dumps(variables, sort_keys=True)
        combined = f"{query_normalized}|{variables_json}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _extract_operation_name(self, query: str) -> Optional[str]:
        """Extract operation name from GraphQL query."""
        query_lines = query.strip().split('\n')
        for line in query_lines:
            if line.strip().startswith(('query ', 'mutation ', 'subscription ')):
                parts = line.strip().split()
                if len(parts) > 1:
                    return parts[1].split('(')[0]
        return None
    
    def _initialize_triangle_defense_queries(self) -> Dict[str, str]:
        """Initialize common Triangle Defense query templates."""
        return {
            "formation_lookup": """
            query FormationLookup($id: ID!) {
                formation(id: $id) {
                    id
                    formationType
                    triangularRelationships {
                        strength
                        relationshipType
                    }
                    effectiveness_metrics {
                        success_rate
                        usage_frequency
                    }
                }
            }
            """,
            
            "similar_formations": """
            query SimilarFormations($sourceId: ID!, $threshold: Float!) {
                formationSimilarity(sourceFormationId: $sourceId, threshold: $threshold) {
                    targetFormation {
                        id
                        formationType
                        similarity_score
                    }
                }
            }
            """,
            
            "tactical_analysis": """
            query TacticalAnalysis($formationIds: [ID!]!) {
                tacticalAnalysis(formationIds: $formationIds) {
                    formation_relationships
                    strategic_recommendations
                    adaptation_suggestions
                }
            }
            """
        }
    
    async def _build_similarity_graph(self, formations: List[Dict], context: TriangleDefenseContext) -> Dict[str, Any]:
        """Build formation similarity graph from query results."""
        if not formations:
            return {}
        
        # Extract formation IDs for similarity analysis
        formation_ids = [f["id"] for f in formations[:10]]  # Limit for performance
        
        similarity_result = await self.execute_graph_analysis(
            analysis_type="formation_similarity",
            formation_ids=formation_ids
        )
        
        return similarity_result.get("formationSimilarityNetwork", {})
    
    async def _generate_tactical_insights(self, formations: List[Dict], context: TriangleDefenseContext) -> List[Dict]:
        """Generate tactical insights from formation analysis results."""
        insights = []
        
        # Success rate analysis
        if formations:
            success_rates = [f.get("historicalSuccessRate", 0) for f in formations if f.get("historicalSuccessRate")]
            if success_rates:
                avg_success = sum(success_rates) / len(success_rates)
                insights.append({
                    "type": "success_analysis",
                    "insight": f"Average success rate: {avg_success:.1%}",
                    "recommendation": "Focus on formations with >75% success rate" if avg_success > 0.75 else "Review formation effectiveness"
                })
        
        # Formation type distribution
        formation_types = [f.get("formationType") for f in formations]
        type_distribution = {ft: formation_types.count(ft) for ft in set(formation_types) if ft}
        if type_distribution:
            most_common = max(type_distribution, key=type_distribution.get)
            insights.append({
                "type": "distribution_analysis", 
                "insight": f"Most common formation type: {most_common} ({type_distribution[most_common]} instances)",
                "recommendation": f"Consider diversifying beyond {most_common} formations"
            })
        
        return insights
    
    async def _establish_websocket_connection(self):
        """Establish WebSocket connection for subscriptions."""
        try:
            headers = {}
            if self.auth_token:
                headers["Authorization"] = f"Bearer {self.auth_token}"
            
            self.websocket_connection = await websockets.connect(
                self.websocket_endpoint,
                extra_headers=headers
            )
            
            # Start listening for messages
            asyncio.create_task(self._handle_websocket_messages())
            
            self.logger.info("WebSocket connection established")
            
        except Exception as e:
            self.logger.error(f"Failed to establish WebSocket connection: {str(e)}")
            raise
    
    async def _handle_websocket_messages(self):
        """Handle incoming WebSocket messages."""
        try:
            async for message in self.websocket_connection:
                data = json.loads(message)
                
                if data.get("type") == "data":
                    # Route to appropriate handler
                    for subscription_type, handler in self.subscription_handlers.items():
                        try:
                            await handler(data.get("payload", {}))
                        except Exception as e:
                            self.logger.error(f"Subscription handler error: {str(e)}")
                            
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("WebSocket connection closed")
        except Exception as e:
            self.logger.error(f"WebSocket message handling error: {str(e)}")
    
    def _build_subscription_query(self, subscription_type: SubscriptionType, filter_params: Dict[str, Any]) -> str:
        """Build subscription query based on type."""
        if subscription_type == SubscriptionType.FORMATION_UPDATES:
            return """
            subscription FormationUpdates($filters: FormationFilters) {
                formationUpdated(filters: $filters) {
                    id
                    formationType
                    timestamp
                    playerPositions {
                        playerId
                        position {
                            x
                            y
                            z
                        }
                    }
                }
            }
            """
        
        elif subscription_type == SubscriptionType.GAME_STATE_CHANGES:
            return """
            subscription GameStateChanges {
                gameStateChanged {
                    gameId
                    quarter
                    timeRemaining
                    possession {
                        team
                        down
                        yardsToGo
                    }
                }
            }
            """
        
        elif subscription_type == SubscriptionType.EMERGENCY_ALERTS:
            return """
            subscription EmergencyAlerts {
                emergencyAlert {
                    alertId
                    severity
                    message
                    triggeredAt
                    requiredAction
                }
            }
            """
        
        else:
            raise ValueError(f"Unsupported subscription type: {subscription_type}")
    
    def _analyze_data_source_usage(self) -> Dict[str, int]:
        """Analyze data source usage patterns."""
        source_counts = defaultdict(int)
        for metric in self.performance_metrics:
            for source in metric.data_sources:
                source_counts[source.value] += 1
        return dict(source_counts)
    
    def _analyze_complexity_distribution(self) -> Dict[str, int]:
        """Analyze query complexity distribution."""
        complexity_counts = defaultdict(int)
        for metric in self.performance_metrics:
            complexity_counts[metric.complexity.value] += 1
        return dict(complexity_counts)


# Convenience functions for common operations
async def create_federation_client(config: Dict[str, Any] = None) -> GraphQLFederationClient:
    """Create and initialize a GraphQL federation client."""
    config = config or {}
    
    client = GraphQLFederationClient(
        federation_endpoint=config.get("federation_endpoint", "http://localhost:4000/graphql"),
        websocket_endpoint=config.get("websocket_endpoint", "ws://localhost:4000/subscriptions"),
        auth_token=config.get("auth_token"),
        cache_ttl_seconds=config.get("cache_ttl", 300),
        max_concurrent_queries=config.get("max_concurrent", 10)
    )
    
    await client.initialize()
    return client


async def query_triangle_defense_quick(formation_type: str = None,
                                     hash_position: str = None,
                                     include_similarity: bool = False) -> FormationQueryResult:
    """Quick Triangle Defense formation query with sensible defaults."""
    
    client = await create_federation_client()
    
    try:
        context = TriangleDefenseContext(
            formation_type=formation_type,
            hash_position=hash_position,
            include_similarity_analysis=include_similarity,
            max_results=20
        )
        
        return await client.query_triangle_defense_formations(context)
        
    finally:
        await client.close()
