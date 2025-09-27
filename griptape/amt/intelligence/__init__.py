"""
AMT Intelligence Module - Unified intelligence coordination for AnalyzeMyTeam ecosystem.

This module provides the complete intelligence framework for managing 25 championship 
professionals across 7 organizational tiers with multi-source data federation, 
Triangle Defense integration, and championship-level performance standards.

Core Components:
- IntelligenceCoordinator: Master orchestration engine
- StaffRegistry: 25 professional management system  
- TierManager: Sophisticated task complexity and staff selection
- AirtableBridge: Real-time intelligence brain integration
- GraphQLFederationClient: Multi-source data orchestration

Usage:
    from griptape.amt.intelligence import IntelligenceCoordinator, create_amt_intelligence_system
    
    # Initialize complete intelligence system
    coordinator = await create_amt_intelligence_system()
    
    # Process intelligence request
    result = await coordinator.process_request(
        "Analyze Triangle Defense formation effectiveness for Sunday's game",
        urgency="high",
        context={"opponent": "Chiefs", "game_situation": "red_zone"}
    )
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import os

# Core intelligence components
from .coordinator import (
    IntelligenceCoordinator,
    IntelligenceRequest,
    IntelligenceResponse,
    RequestType,
    ProcessingMode,
    IntelligenceConfig
)

from .staff_registry import (
    StaffRegistry,
    StaffMember,
    TierLevel,
    ExpertiseArea,
    StaffStatus,
    PerformanceMetrics,
    StaffProfile
)

from .tier_manager import (
    TierManager,
    TaskComplexity,
    UrgencyLevel,
    DecisionScope,
    EscalationTrigger,
    ComplexityAssessment,
    UrgencyAssessment,
    StaffSelectionCriteria,
    StaffSelectionResult,
    EscalationProtocol
)

from .airtable_bridge import (
    AirtableBridge,
    TriangleAnalysisRecord,
    MELCoordinationRecord,
    StaffCoordinationRecord,
    MissionControlRecord
)

from .graphql_client import (
    GraphQLFederationClient,
    DataSource,
    QueryComplexity,
    SubscriptionType,
    FormationQueryResult,
    TriangleDefenseContext,
    QueryMetrics,
    create_federation_client,
    query_triangle_defense_quick
)

# Configuration and utilities
__version__ = "1.0.0-amt.intelligence"
__author__ = "AnalyzeMyTeam Intelligence Division"
__description__ = "Championship-level intelligence coordination for the AMT ecosystem"

# Configure module-level logging
logging.getLogger("AMT.Intelligence").setLevel(logging.INFO)

# Public API exports
__all__ = [
    # Core Components
    "IntelligenceCoordinator",
    "StaffRegistry", 
    "TierManager",
    "AirtableBridge",
    "GraphQLFederationClient",
    
    # Request/Response Models
    "IntelligenceRequest",
    "IntelligenceResponse",
    "ComplexityAssessment",
    "UrgencyAssessment",
    "StaffSelectionResult",
    "FormationQueryResult",
    "TriangleDefenseContext",
    
    # Staff Management
    "StaffMember",
    "StaffProfile",
    "PerformanceMetrics",
    "StaffSelectionCriteria",
    
    # Data Models
    "TriangleAnalysisRecord",
    "MELCoordinationRecord", 
    "StaffCoordinationRecord",
    "MissionControlRecord",
    "QueryMetrics",
    
    # Enums
    "RequestType",
    "ProcessingMode",
    "TierLevel",
    "ExpertiseArea",
    "StaffStatus",
    "TaskComplexity",
    "UrgencyLevel",
    "DecisionScope",
    "EscalationTrigger",
    "DataSource",
    "QueryComplexity",
    "SubscriptionType",
    
    # Configuration
    "IntelligenceConfig",
    "AMTIntelligenceConfig",
    
    # Factory Functions
    "create_amt_intelligence_system",
    "create_intelligence_coordinator",
    "create_staff_registry",
    "create_tier_manager",
    "create_airtable_bridge",
    "create_graphql_client",
    
    # Utility Functions
    "initialize_intelligence_logging",
    "validate_amt_environment",
    "get_intelligence_status",
    "emergency_escalation_protocol"
]


class AMTIntelligenceConfig:
    """
    Comprehensive configuration for the AMT Intelligence system.
    
    Manages all configuration aspects including API endpoints, authentication,
    performance tuning, and operational parameters.
    """
    
    def __init__(self,
                 # Airtable Configuration
                 airtable_api_key: Optional[str] = None,
                 airtable_base_id: str = "appN3SXLemGYCEg4K",
                 
                 # GraphQL Federation Configuration  
                 graphql_endpoint: str = "http://localhost:4000/graphql",
                 graphql_websocket: str = "ws://localhost:4000/subscriptions",
                 graphql_auth_token: Optional[str] = None,
                 
                 # Performance Configuration
                 max_concurrent_requests: int = 20,
                 cache_ttl_seconds: int = 300,
                 query_timeout_seconds: float = 30.0,
                 
                 # Staff Configuration
                 staff_data_path: Optional[Path] = None,
                 auto_load_staff: bool = True,
                 enable_succession_planning: bool = True,
                 
                 # Intelligence Configuration
                 default_processing_mode: ProcessingMode = ProcessingMode.STANDARD,
                 enable_emergency_protocols: bool = True,
                 nuclear_escalation_enabled: bool = True,
                 
                 # Logging Configuration
                 log_level: str = "INFO",
                 log_file_path: Optional[Path] = None,
                 enable_performance_logging: bool = True):
        
        # API Configuration
        self.airtable_api_key = airtable_api_key or os.getenv("AIRTABLE_API_KEY")
        self.airtable_base_id = airtable_base_id
        self.graphql_endpoint = graphql_endpoint
        self.graphql_websocket = graphql_websocket  
        self.graphql_auth_token = graphql_auth_token or os.getenv("GRAPHQL_AUTH_TOKEN")
        
        # Performance Configuration
        self.max_concurrent_requests = max_concurrent_requests
        self.cache_ttl_seconds = cache_ttl_seconds
        self.query_timeout_seconds = query_timeout_seconds
        
        # Staff Configuration
        self.staff_data_path = staff_data_path or Path("data/amt_staff_registry.json")
        self.auto_load_staff = auto_load_staff
        self.enable_succession_planning = enable_succession_planning
        
        # Intelligence Configuration
        self.default_processing_mode = default_processing_mode
        self.enable_emergency_protocols = enable_emergency_protocols
        self.nuclear_escalation_enabled = nuclear_escalation_enabled
        
        # Logging Configuration
        self.log_level = log_level
        self.log_file_path = log_file_path
        self.enable_performance_logging = enable_performance_logging
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration parameters."""
        if not self.airtable_api_key:
            raise ValueError("Airtable API key is required - set AIRTABLE_API_KEY environment variable")
        
        if self.max_concurrent_requests < 1:
            raise ValueError("max_concurrent_requests must be at least 1")
        
        if self.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "airtable": {
                "api_key": "***" if self.airtable_api_key else None,
                "base_id": self.airtable_base_id
            },
            "graphql": {
                "endpoint": self.graphql_endpoint,
                "websocket": self.graphql_websocket,
                "auth_token": "***" if self.graphql_auth_token else None
            },
            "performance": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "cache_ttl_seconds": self.cache_ttl_seconds,
                "query_timeout_seconds": self.query_timeout_seconds
            },
            "staff": {
                "data_path": str(self.staff_data_path),
                "auto_load_staff": self.auto_load_staff,
                "enable_succession_planning": self.enable_succession_planning
            },
            "intelligence": {
                "default_processing_mode": self.default_processing_mode.value,
                "enable_emergency_protocols": self.enable_emergency_protocols,
                "nuclear_escalation_enabled": self.nuclear_escalation_enabled
            },
            "logging": {
                "log_level": self.log_level,
                "log_file_path": str(self.log_file_path) if self.log_file_path else None,
                "enable_performance_logging": self.enable_performance_logging
            }
        }


# Factory Functions
async def create_amt_intelligence_system(config: Optional[AMTIntelligenceConfig] = None) -> IntelligenceCoordinator:
    """
    Create and initialize the complete AMT Intelligence system.
    
    This is the primary entry point for setting up the full intelligence
    coordination system with all components properly initialized and integrated.
    
    Args:
        config: Optional configuration object. Uses defaults if not provided.
        
    Returns:
        Fully initialized IntelligenceCoordinator ready for operation
        
    Example:
        coordinator = await create_amt_intelligence_system()
        result = await coordinator.process_request("Analyze formation effectiveness")
    """
    
    if config is None:
        config = AMTIntelligenceConfig()
    
    # Initialize logging
    initialize_intelligence_logging(config)
    
    logger = logging.getLogger("AMT.Intelligence.Factory")
    logger.info("Initializing complete AMT Intelligence system")
    
    try:
        # Create core components
        staff_registry = await create_staff_registry(config)
        tier_manager = create_tier_manager()
        airtable_bridge = await create_airtable_bridge(config)
        graphql_client = await create_graphql_client(config)
        
        # Create intelligence configuration
        intelligence_config = IntelligenceConfig(
            max_concurrent_requests=config.max_concurrent_requests,
            cache_ttl_seconds=config.cache_ttl_seconds,
            default_processing_mode=config.default_processing_mode,
            enable_emergency_protocols=config.enable_emergency_protocols,
            nuclear_escalation_enabled=config.nuclear_escalation_enabled
        )
        
        # Create and initialize coordinator
        coordinator = IntelligenceCoordinator(
            staff_registry=staff_registry,
            tier_manager=tier_manager,
            airtable_bridge=airtable_bridge,
            graphql_client=graphql_client,
            config=intelligence_config
        )
        
        await coordinator.initialize()
        
        logger.info("AMT Intelligence system initialization complete")
        return coordinator
        
    except Exception as e:
        logger.error(f"Failed to initialize AMT Intelligence system: {str(e)}")
        raise


async def create_intelligence_coordinator(staff_registry: StaffRegistry,
                                        tier_manager: TierManager,
                                        airtable_bridge: AirtableBridge,
                                        graphql_client: GraphQLFederationClient,
                                        config: Optional[IntelligenceConfig] = None) -> IntelligenceCoordinator:
    """Create IntelligenceCoordinator with provided components."""
    
    coordinator = IntelligenceCoordinator(
        staff_registry=staff_registry,
        tier_manager=tier_manager,
        airtable_bridge=airtable_bridge,
        graphql_client=graphql_client,
        config=config or IntelligenceConfig()
    )
    
    await coordinator.initialize()
    return coordinator


async def create_staff_registry(config: AMTIntelligenceConfig) -> StaffRegistry:
    """Create and initialize StaffRegistry with AMT staff data."""
    
    registry = StaffRegistry()
    
    if config.auto_load_staff:
        if config.staff_data_path.exists():
            await registry.load_staff_data(config.staff_data_path)
        else:
            # Initialize with default AMT staff if no data file exists
            await registry.initialize_amt_staff()
            # Save for future use
            await registry.save_staff_data(config.staff_data_path)
    
    return registry


def create_tier_manager() -> TierManager:
    """Create TierManager with AMT-optimized algorithms."""
    return TierManager()


async def create_airtable_bridge(config: AMTIntelligenceConfig) -> AirtableBridge:
    """Create and initialize AirtableBridge with AMT tables."""
    
    bridge = AirtableBridge(
        api_key=config.airtable_api_key,
        base_id=config.airtable_base_id
    )
    
    await bridge.initialize()
    return bridge


async def create_graphql_client(config: AMTIntelligenceConfig) -> GraphQLFederationClient:
    """Create and initialize GraphQL federation client."""
    
    client_config = {
        "federation_endpoint": config.graphql_endpoint,
        "websocket_endpoint": config.graphql_websocket,
        "auth_token": config.graphql_auth_token,
        "cache_ttl": config.cache_ttl_seconds,
        "max_concurrent": config.max_concurrent_requests
    }
    
    return await create_federation_client(client_config)


# Utility Functions
def initialize_intelligence_logging(config: AMTIntelligenceConfig):
    """Initialize comprehensive logging for the intelligence system."""
    
    # Configure root AMT logger
    amt_logger = logging.getLogger("AMT")
    amt_logger.setLevel(getattr(logging, config.log_level.upper()))
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    if not amt_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(simple_formatter)
        amt_logger.addHandler(console_handler)
    
    # File handler if configured
    if config.log_file_path:
        config.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file_path)
        file_handler.setFormatter(detailed_formatter)
        amt_logger.addHandler(file_handler)
    
    # Performance logging
    if config.enable_performance_logging:
        perf_logger = logging.getLogger("AMT.Performance")
        perf_logger.setLevel(logging.DEBUG)
    
    amt_logger.info("AMT Intelligence logging initialized")


def validate_amt_environment() -> Dict[str, Any]:
    """
    Validate the AMT environment and return status information.
    
    Returns:
        Dictionary containing validation results and environment status
    """
    
    validation_results = {
        "environment_valid": True,
        "errors": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Check required environment variables
    required_env_vars = ["AIRTABLE_API_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            validation_results["errors"].append(f"Missing required environment variable: {var}")
            validation_results["environment_valid"] = False
    
    # Check optional environment variables
    optional_env_vars = ["GRAPHQL_AUTH_TOKEN", "SUPABASE_URL", "SUPABASE_KEY"]
    for var in optional_env_vars:
        if not os.getenv(var):
            validation_results["warnings"].append(f"Optional environment variable not set: {var}")
    
    # Check data directories
    data_dir = Path("data")
    if not data_dir.exists():
        validation_results["recommendations"].append("Create 'data' directory for persistent storage")
    
    # Check log directories
    log_dir = Path("logs")
    if not log_dir.exists():
        validation_results["recommendations"].append("Create 'logs' directory for log files")
    
    return validation_results


async def get_intelligence_status(coordinator: Optional[IntelligenceCoordinator] = None) -> Dict[str, Any]:
    """
    Get comprehensive status of the intelligence system.
    
    Args:
        coordinator: Optional coordinator instance. Creates new one if not provided.
        
    Returns:
        Comprehensive system status information
    """
    
    if coordinator is None:
        try:
            coordinator = await create_amt_intelligence_system()
        except Exception as e:
            return {
                "system_status": "error",
                "error_message": str(e),
                "timestamp": str(datetime.now())
            }
    
    try:
        status = {
            "system_status": "operational",
            "timestamp": str(datetime.now()),
            "components": {
                "staff_registry": coordinator.staff_registry.get_registry_status(),
                "tier_manager": coordinator.tier_manager.get_tier_manager_metrics(),
                "airtable_bridge": await coordinator.airtable_bridge.get_health_status(),
                "graphql_client": coordinator.graphql_client.get_performance_metrics()
            },
            "performance_metrics": coordinator.get_performance_metrics(),
            "environment": validate_amt_environment()
        }
        
        return status
        
    except Exception as e:
        return {
            "system_status": "degraded",
            "error_message": str(e),
            "timestamp": str(datetime.now())
        }


async def emergency_escalation_protocol(emergency_type: str,
                                      severity: str,
                                      context: Dict[str, Any],
                                      coordinator: Optional[IntelligenceCoordinator] = None) -> Dict[str, Any]:
    """
    Execute emergency escalation protocol for critical situations.
    
    Args:
        emergency_type: Type of emergency (system_failure, security_breach, etc.)
        severity: Severity level (low, medium, high, critical, nuclear)
        context: Emergency context and details
        coordinator: Optional coordinator instance
        
    Returns:
        Emergency response coordination results
    """
    
    if coordinator is None:
        coordinator = await create_amt_intelligence_system()
    
    # Create emergency request
    emergency_request = IntelligenceRequest(
        content=f"EMERGENCY: {emergency_type}",
        request_type=RequestType.EMERGENCY_RESPONSE,
        context={
            **context,
            "emergency_type": emergency_type,
            "severity": severity,
            "triggered_at": datetime.now().isoformat()
        },
        urgency_indicators=["emergency", "critical", "immediate"],
        processing_mode=ProcessingMode.CRISIS
    )
    
    # Process emergency request
    response = await coordinator.process_request(emergency_request)
    
    # Log emergency escalation
    logger = logging.getLogger("AMT.Emergency")
    logger.critical(f"Emergency escalation executed: {emergency_type} - Severity: {severity}")
    
    return {
        "emergency_id": response.request_id,
        "escalation_status": "activated",
        "assigned_staff": [staff.full_name for staff in response.assigned_staff],
        "response_time_seconds": response.processing_time_seconds,
        "emergency_details": {
            "type": emergency_type,
            "severity": severity,
            "context": context
        },
        "next_actions": response.recommendations[:3]  # Top 3 critical actions
    }


# Version and metadata
def get_version_info() -> Dict[str, str]:
    """Get version and build information."""
    return {
        "version": __version__,
        "author": __author__, 
        "description": __description__,
        "components": {
            "intelligence_coordinator": "1.0.0",
            "staff_registry": "1.0.0", 
            "tier_manager": "1.0.0",
            "airtable_bridge": "1.0.0",
            "graphql_client": "1.0.0"
        }
    }


# Module initialization
def _initialize_module():
    """Initialize the intelligence module on import."""
    
    # Set up basic logging if not already configured
    amt_logger = logging.getLogger("AMT.Intelligence")
    if not amt_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        amt_logger.addHandler(handler)
        amt_logger.setLevel(logging.WARNING)  # Conservative default
    
    amt_logger.info(f"AMT Intelligence Module {__version__} loaded")


# Initialize on import
_initialize_module()
